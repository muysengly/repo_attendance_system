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
pip install setuptools jupyter opencv-python insightface onnxruntime pyqt5


@REM create a folder result
@REM if not exist "result" (
@REM     mkdir "result"
@REM )


@REM create a folder data
@REM if not exist "database" (
@REM     mkdir "database"
@REM )


@REM download the model
@REM if not exist "models" (
@REM     python -c "import os; from insightface.app import FaceAnalysis; FaceAnalysis(name='buffalo_sc', root=os.getcwd(), providers=['CPUExecutionProvider'])"
@REM )