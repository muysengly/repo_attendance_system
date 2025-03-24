@echo off


@REM create a virtual environment if it doesn't exist
if not exist venv (
    py -3.12 -m venv venv
)


@REM call venv\Scripts\activate
call venv\Scripts\activate


@REM update pip
python.exe -m pip install --upgrade pip


@REM install dependencies
pip install setuptools jupyter opencv-python insightface onnxruntime pyqt5 pillow-heif


@REM create a folder result
if not exist "result" (
    mkdir "result"
)


@REM create a folder data
if not exist "data" (
    mkdir "data"
)


@REM download the model
if not exist "models" (
    python -c "import os; from insightface.app import FaceAnalysis; FaceAnalysis(name='buffalo_sc', root=os.getcwd(), providers=['CPUExecutionProvider'])"
)