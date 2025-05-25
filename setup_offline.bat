@echo off


@REM create a virtual environment if it doesn't exist
if not exist venv (
    py -3.12 -m venv venv
)


@REM call venv\Scripts\activate
call venv\Scripts\activate


@REM install dependencies
pip install --no-index --find-links=__setup__/setup_offline -r requirements.txt

