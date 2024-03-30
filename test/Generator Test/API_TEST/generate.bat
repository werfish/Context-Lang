@echo off
SET "PROJECT_DIR=%CD%"

echo Starting automatic Context generation...

@REM REM Create the database connection setup
@REM echo Generating database connection setup...
@REM context --debug --log --filepath "%PROJECT_DIR%\db.py"

@REM REM Generate the SQLAlchemy database models first
@REM echo Generating database models...
@REM context --debug --log --filepath "%PROJECT_DIR%\db_models.py"

@REM REM Generate ORM queries
@REM echo Generating ORM queries...
@REM context --debug --log --filepath "%PROJECT_DIR%\queries.py"

@REM REM generate the integration with Binance
@REM echo Generating Binance Integration...
@REM context --debug --log --filepath "%PROJECT_DIR%\binance.py"

@REM REM generate download schedule data process
@REM echo Generating Binance Data Download Schedule...
@REM context --debug --log --filepath "%PROJECT_DIR%\data_download_schedule.py"

@REM REM generate the pydantic models
@REM echo Generating Pydantic Models...
@REM context --debug --log --filepath "%PROJECT_DIR%\pydantic_models.py"

@REM REM Finally, generate the endpoints that depend on everything else
@REM echo Generating FastAPI endpoints...
@REM context --debug --log --filepath "%PROJECT_DIR%\main.py"

echo Context generation process completed.

echo Generating requirements.txt using pipreqs...
pipreqs "%PROJECT_DIR%" --force

echo Adding dependencies to Poetry...
FOR /F "usebackq delims=" %%i IN (`type "%PROJECT_DIR%\requirements.txt"`) DO call poetry add "%%i"

echo Running main.py with Poetry...
poetry run python main.py

echo Running data_download_schedule.py with Poetry...
poetry run python data_download_schedule.py

pause