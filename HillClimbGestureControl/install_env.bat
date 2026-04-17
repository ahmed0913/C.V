@echo off
echo ========================================================
echo Installing Python 3.11 and setting up the environment
echo ========================================================

echo 1. Downloading Python 3.11 installer...
curl -o python-installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

echo 2. Installing Python 3.11 (Please wait and click YES if asked for permission)...
start /wait python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

echo 3. Waiting for installation to complete...
timeout /t 10

echo 4. Upgrading pip and installing requirements...
pip install --upgrade pip
pip install -r requirements.txt

echo ========================================================
echo Setup Complete! You can now run your project using run.bat
echo ========================================================
pause
