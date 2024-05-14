#!/bin/bash
pip3 install -r requirements.txt
export SERVER_MODE=standard
python3 main.py --port 3001