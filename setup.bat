@echo off

@REM install dependencies
pip install pyqt5 opencv-python insightface onnxruntime


@REM Copy shortcut to desktop
copy "C:\repo_attendance_system-main\resource\utility\Attendance System.lnk" "%USERPROFILE%\Desktop\Attendance System.lnk"


pause