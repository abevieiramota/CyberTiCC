#!/bin/bash

cd db/
python init.py

cd ../delexicalizer
python delex.py
python ordering.py

cd ../scripts/
python entity_info.py