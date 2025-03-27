@echo off


@REM create a virtual environment if it doesn't exist
if not exist venv (
    py -3.12 -m venv venv
)


@REM call venv\Scripts\activate
call venv\Scripts\activate


@REM install dependencies
pip install --no-index --find-links=setup_offline -r requirements.txt


@REM create a folder result
if not exist "result" (
    mkdir "result"
)


@REM create a folder data
if not exist "database" (
    mkdir "database"
)

