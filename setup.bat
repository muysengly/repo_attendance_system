@echo off

@REM install dependencies
py -3.12 -m pip install opencv-python insightface onnxruntime pyqt5


echo.
echo.
echo Dependencies installed successfully.
echo.
echo.
echo Please run "run.bat" to start the application.
echo.
echo.

pause