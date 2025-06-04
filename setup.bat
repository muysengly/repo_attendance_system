@echo off

@REM install dependencies
pip install opencv-python insightface onnxruntime pyqt5


@REM copy a file c:\att/resource/utility/attendance  system.ink to desktop
copy "C:\repo_attendance_system-main\resource\utility\Attendance System.lnk" "%USERPROFILE%\Desktop\Attendance System.lnk"


pause