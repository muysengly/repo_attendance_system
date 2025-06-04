@REM Change directory to C:\
cd C:\


@REM Download the repository
curl -L -o repo.zip https://github.com/muysengly/repo_attendance_system/archive/refs/heads/main.zip


@REM Extract the downloaded zip file
tar -xf repo.zip


@REM Delete the zip file after extraction
del repo.zip


@REM Change directory to the extracted folder
cd repo_attendance_system-main


@REM run setup.bat
call setup.bat
