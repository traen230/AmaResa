@echo off
cd /d %~dp0
setlocal
set BASEDIR=%cd%

REM === クリーンアップ ===
rd /s /q build
rd /s /q dist
del app.spec 2>nul

REM === ビルド ===
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
  --add-data "%BASEDIR%\templates;templates" ^
  --add-data "%BASEDIR%\static;static" ^
  --add-data "%BASEDIR%\driver\chromedriver.exe;driver" ^
  --add-data "%BASEDIR%\start_chrome_with_extension.py;." ^
  --hidden-import=bs4 ^
  --hidden-import=scipy._lib.array_api_compat.numpy.fft ^
  --collect-submodules sklearn ^
  --collect-submodules scipy ^
  --collect-submodules tensorflow ^
  app.py

REM === version.txt自動生成 ===
set VERSION=117.1.0
set RELEASE_DATE=%DATE%

echo AmaResa Local App > dist\app\version.txt
echo Version: %VERSION% >> dist\app\version.txt
echo Release Date: %RELEASE_DATE% >> dist\app\version.txt
echo. >> dist\app\version.txt
echo [Environment] >> dist\app\version.txt
echo Python: 3.11.9 >> dist\app\version.txt
echo PyInstaller: 5.13.0 >> dist\app\version.txt
echo ChromeDriver: 117.0.5938.92 >> dist\app\version.txt
echo. >> dist\app\version.txt
echo [Dependencies] >> dist\app\version.txt
echo tensorflow: 2.15.0 >> dist\app\version.txt
echo scikit-learn: 1.4.2 >> dist\app\version.txt
echo scipy: 1.13.0 >> dist\app\version.txt

pause
