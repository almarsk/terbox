#!/bin/bash

cp convform/bots/vtipobot_edited.json ../convform/bots/vtipobot.json
cp -r ../convform/bots/ convform/bots/
cp ../convform/Cargo.toml convform/Cargo.toml

# cd convform/ && maturin develop --features debug
python test.py
