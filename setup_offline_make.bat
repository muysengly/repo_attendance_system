@echo off


@REM call venv\Scripts\activate
call venv\Scripts\activate


@REM // freeze the current environment
pip freeze > requirements.txt


@REM // download dependencies
pip download -r requirements.txt -d setup_offline
