@echo off
echo Starting SortedPC Watcher...

cd /d C:\Users\SHRISW~1\DOCUME~1\SHRISW~1\Extras\Projects\sortedpc
set PY_PATH=venv\Scripts\pythonw.exe
set LOG_PATH=watcher_launch.log

:: Start detached
start "" "%PY_PATH%" -m src.core.pipelines.watcher > "%LOG_PATH%" 2>&1

:: Exit immediately
exit
