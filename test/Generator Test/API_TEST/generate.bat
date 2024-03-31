@echo off
SET "PROJECT_DIR=%CD%"

echo Starting automatic Context generation...

REM Create the database connection setup
echo Generating database connection setup...
context --debug --log --filepath "%PROJECT_DIR%\db.py"

REM Generate the SQLAlchemy database models first
echo Generating database models...
context --debug --log --filepath "%PROJECT_DIR%\db_models.py"

REM Generate ORM queries
echo Generating ORM queries...
context --debug --log --filepath "%PROJECT_DIR%\queries.py"

REM generate the integration with Binance
echo Generating Binance Integration...
context --debug --log --filepath "%PROJECT_DIR%\binance.py"

REM generate download schedule data process
echo Generating Binance Data Download Schedule...
context --debug --log --filepath "%PROJECT_DIR%\data_download_schedule.py"

REM generate the pydantic models
echo Generating Pydantic Models...
context --debug --log --filepath "%PROJECT_DIR%\pydantic_models.py"

REM Finally, generate the endpoints that depend on everything else
echo Generating FastAPI endpoints...
context --debug --log --filepath "%PROJECT_DIR%\main.py"

echo Context generation process completed.

echo Generating requirements.txt using pipreqs...
pipreqs "%PROJECT_DIR%" --force

echo Adding dependencies to Poetry...
FOR /F "usebackq delims=" %%i IN (`type "%PROJECT_DIR%\requirements.txt"`) DO (
    IF NOT "%%i"=="pydantic" (
        call poetry add "%%i"
    )
)

echo Adding Uvicorn to Poetry...
call poetry add uvicorn

echo Running main.py with Poetry...
poetry run python main.py

echo Running data_download_schedule.py with Poetry...
poetry run python data_download_schedule.py

pause