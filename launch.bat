@ECHO OFF
cls

CHCP 65001 > NUL
CD /d "%~dp0"

SETLOCAL ENABLEEXTENSIONS
SET KEY_NAME="HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
SET VALUE_NAME=HideFileExt

FOR /F "usebackq tokens=1-3" %%A IN (`REG QUERY %KEY_NAME% /v %VALUE_NAME% 2^>nul`) DO (
    SET ValueName=%%A
    SET ValueType=%%B
    SET ValueValue=%%C
)

IF x%ValueValue:0x0=%==x%ValueValue% (
    ECHO Unhiding file extensions...
    START CMD /c REG ADD HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced /v HideFileExt /t REG_DWORD /d 0 /f
)
ENDLOCAL

python --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO nopython

git.exe --version > NUL
IF %ERRORLEVEL% NEQ 0 GOTO nogit

:start
ECHO Launcher for the VectorBot
ECHO 'auto' for automatically restarting the bot on shutdown
ECHO 'update' to update the bot
ECHO 'autoupdate' to update the bot then run it with automattic restart
ECHO Just press enter to just run the bot normally
set choice=
set /p choice=
IF not '%choice%'=='' GOTO normal
IF '%choice%'=='auto' GOTO auto
IF '%choice%'=='autoupdate' GOTO autoupdate
IF '%choice%'=='update' GOTO update
IF '%choice%'=='a' GOTO auto
IF '%choice%'=='au' GOTO autoupdate
IF '%choice%'=='u' GOTO update

:normal
CLS
CMD /k python bot.py
GOTO end

:update
CLS
call git fetch
call git pull
GOTO end

:autoupdate
CLS
CALL git fetch
CALL git pull
CLS
GOTO auto

:auto
CLS
GOTO normal

:nopython
ECHO ERROR: Python has either not been installed or not added to your PATH.
GOTO end

:nogit
ECHO ERROR: Git has either not been installed or not added to your PATH.
GOTO end

:end
pause
