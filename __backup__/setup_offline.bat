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
@REM if not exist "result" (
@REM     mkdir "result"
@REM )


@REM create a folder data
@REM if not exist "database" (
@REM     mkdir "database"
@REM )
