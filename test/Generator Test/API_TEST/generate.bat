@echo off
@SET PROJECT_DIR="C:\Users\Robert\Desktop\PROJECTS\AI PROJECTS\Context\Context\test\Generator Test\API_TEST"
SET PROJECT_DIR="C:\Users\werfi\Desktop\My Projects\Context-Lang\test\Generator Test\API_TEST"
echo Starting automatic Context generation...

REM Create the database connection setup
echo Generating database connection setup...
context --debug --log --filepath %PROJECT_DIR%\db.py
timeout /t 2 /nobreak >nul

REM Generate the SQLAlchemy database models first
echo Generating database models...
context --debug --log --filepath %PROJECT_DIR%\db_models.py
timeout /t 2 /nobreak >nul

REM Generate ORM queries
echo Generating ORM queries...
context --debug --log --filepath %PROJECT_DIR%\queries.py

@REM REM Generate services that might depend on db models and queries
@REM echo Generating services...
@REM context --filepath %PROJECT_DIR%\services.py

@REM REM Finally, generate the endpoints that depend on everything else
@REM echo Generating FastAPI endpoints...
@REM context --filepath %PROJECT_DIR%\main.py

@REM echo Context generation process completed.
pause