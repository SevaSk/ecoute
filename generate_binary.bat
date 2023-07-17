REM Define variables for different hard coded paths
SET SOURCE_DIR=C:\git\transcribe
SET OUTPUT_DIR=C:\git\output
SET LIBSITE_PACAGES_DIR=C:\pyenv\transcribe\Lib\site-packages
SET EXECUTABLE_NAME=transcribe.exe
SET ZIP_FILE_NAME=transcribe.zip

REM pyinstaller --clean --noconfirm --specpath C:\\git\\output --distpath C:\\git\\output\dist -n transcribe.exe --log-level DEBUG --recursive-copy-metadata "openai-whisper" main.py

SET PYINSTALLER_DIST_PATH=%OUTPUT_DIR%\dist
ECHO %PYINSTALLER_DIST_PATH%

echo pyinstaller --clean --noconfirm --specpath %OUTPUT_DIR% --distpath %PYINSTALLER_DIST_PATH% -n %EXECUTABLE_NAME% --log-level DEBUG --add-data "C:\pyenv\transcribe\Lib\site-packages\whisper\;."  --add-data "C:\pyenv\transcribe\Lib\site-packages\whisper\assets\mel_filters.npz;." main.py
copy C:\\git\\transcribe\\tiny.en.pt C:\\git\\output\\dist\\transcribe.exe\\tiny.en.pt
copy C:\\pyenv\\transcribe\\Lib\\site-packages\\whisper\\assets\\mel_filters.npz C:\\git\\output\\dist\\transcribe.exe\\whisper\\assets\\mel_filters.npz

REM Code for zipping the final package
