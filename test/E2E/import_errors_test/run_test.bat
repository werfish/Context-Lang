@echo off
SETLOCAL EnableDelayedExpansion

:: Step 1: Add text to .gitignore if it doesn't already exist
FINDSTR /C:"#Ignore the test ignore folder" .gitignore || ECHO #Ignore the test ignore folder>> .gitignore
FINDSTR /C:"**/IgnoredFiles/" .gitignore || ECHO **/IgnoredFiles/>> .gitignore

:: Step 2: Call your command
Context --debug --log --parser

:: Step 3: Remove the specific lines from .gitignore
SET "tempFile=%temp%\%~nx0.tmp"
IF EXIST "%tempFile%" DEL "%tempFile%"
FOR /F "tokens=*" %%i IN ('TYPE ".gitignore"') DO (
    SET "line=%%i"
    SET "modLine=!line:#Ignore the test ignore folder=!"
    SET "modLine=!modLine:**/IgnoredFiles/=!"
    IF "!modLine!" NEQ "!line!" (
        ECHO Skipped: !line!
    ) ELSE (
        ECHO !line!>>"%tempFile%"
    )
)

MOVE /Y "%tempFile%" ".gitignore"
ENDLOCAL
pause