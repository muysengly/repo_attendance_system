@echo off

@REM install dependencies
pip install opencv-python insightface onnxruntime pyqt5


@REM Copy shortcut to desktop
copy "C:\repo_attendance_system-main\resource\utility\Attendance System.lnk" "%USERPROFILE%\Desktop\Attendance System.lnk"


pause