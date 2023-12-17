#! venv/bin/python3

import re
import sqlite3
import fire
import json
import pprint
import test


def main(query='', states=False, debug=False, which=-2):

    conn = sqlite3.connect('chatbot.db')
    cursor_users = conn.cursor()
    cursor_replies = conn.cursor()
    # Prepare users table
    if not query.lower().startswith("where") and query:
        query = "WHERE " + query

    full_query = f"SELECT * FROM user {query};\n"
    print(full_query)
    cursor_users.execute(full_query)
    users = cursor_users.fetchall()
    # Prepare replies table
    user_ids = [user[0] for user in users.__iter__()]
    if len(user_ids) == 0:
        user_ids = ""
    elif len(user_ids) == 1:
        user_ids = f"== {user_ids[0]}"
    else:
        user_ids = f"IN {str(tuple(user_ids))}"

    cursor_replies.execute(f"SELECT * FROM reply WHERE user_id {user_ids};")
    replies = cursor_replies.fetchall()
    csi_container = []

    # Format the conversations
    for user in users:

        def user_bot(who):

            if who:
                if len(user[1]) < 6:
                    return f"{user[1].capitalize()} ({reply[4] / 1000}s):\t"
                else:
                    return f"{user[1].capitalize()} ({reply[4] / 1000}s):\t"
            else:
                return f"{user[2].capitalize()}:\t"

        # print info of user - TODO make it a return
        if not user[4]:
            time_date = re.search('(.{10}).(.{8})', user[3])
            if time_date is not None and not debug:
                print(
                    f"User {user[1].capitalize()} (no.{user[0]})\n" +
                    f"Talked to {user[2].capitalize()} " +
                    f"on {time_date.group(1)}\n" +
                    f"from {time_date.group(2)}\n" +
                    f"and ended the conversation prematurely (or it never had a fixed end).\n"
                )
        else:
            time_date = re.search('(.{10}).(.{8})', user[3])
            time_end = re.search('(.{10}).(.{8})', user[4])
            abort = lambda val: "Aborted" if val == 1 else "Did not abort"
            if time_date is not None and time_end is not None and not debug:
                print(
                    f"\n\nUser {user[1].capitalize()} (id {user[0]})\n" +
                    f"Talked to {user[2].capitalize()} " +
                    f"on {time_date.group(1)}\n" +
                    f"from {time_date.group(2)} " +
                    f"to {time_end.group(2)}.\n" +
                    f"{abort(user[5])}, " +
                    f"rated {user[6]}.\n" +
                    f"and commented:\n\t'{user[7].capitalize().strip()}'\n"
                )


        csi = {}
        for reply in replies:
            if reply[4]:
                csi["user_reply"] = reply[2]
            if reply[1] == user[0]:
                if debug and reply[6]:
                    turn_metadata = reply[6]
                    data_dict = json.loads(json.loads(turn_metadata))


                    if "user_reply" in csi:
                        csi_container.append(csi.copy())
                        #pprint.pp(csi)

                    csi = {
                        "reply": data_dict["reply"],
                        "user_reply": reply[2],
                        "last_states": data_dict["meta"]["last_states"],
                        "states_usage": data_dict["meta"]["states_usage"],
                        "turns_since_initiative": data_dict["meta"]["turns_since_initiative"],
                        "bot_turns": data_dict["meta"]["bot_turns"],
                        "coda": data_dict["meta"]["coda"],
                        "initiativity": data_dict["meta"]["initiativity"],
                        "context": data_dict["meta"]["context"]
                    }
                    #pprint.pp(csi)

                # the actual conversation
                elif not debug:
                    print(f"{user_bot(reply[4])} {reply[2].strip()}")
                    if states and not reply[4]:
                        turn_metadata = reply[6]
                        # greetings from noobsville
                        # print("whole tuple"+str(reply))
                        pprint.pp(json.dumps(json.loads(turn_metadata), ensure_ascii=False).replace("\\", ""))
                        if reply[5]:
                            print("prompt: "+reply[5])
                        print("\n")
                        print("\n______\n")


    if debug:
        print("debug time")
        pprint.pp(csi_container)
        """ [which]) """
        test.main(csi_container[which])

    # Close the cursor and connection objects
    cursor_users.close()
    cursor_replies.close()
    conn.close()


def cols(table):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()

    # return names of table in scheme
    if table == "?":
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return "\ntables in scheme are" \
               ":\n"+str([row[0] for row in cursor.fetchall()])+"\nquery only has access to user table\n"

    # return names of cols in tables
    cursor.execute(f"SELECT name FROM pragma_table_info('{table}')")
    return [row[0] for row in cursor.fetchall()]

if __name__ == '__main__':
    fire.Fire(main)