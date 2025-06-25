#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# install dependencies
pip install pyqt5 opencv-python insightface onnxruntime

read -p "Press any key to continue . . ."
