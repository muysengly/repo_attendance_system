@echo off


@REM update pip
python.exe -m pip install --upgrade pip


@REM install dependencies
pip install opencv-python insightface onnxruntime pyqt5
