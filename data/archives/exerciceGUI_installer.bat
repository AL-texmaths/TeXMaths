@echo off
REM Ouvre une boîte de dialogue pour choisir un dossier
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.FolderBrowserDialog; if($f.ShowDialog() -eq 'OK'){Write-Output $f.SelectedPath}"`) do set "DISTPATH=%%i"

echo Dossier sélectionné : %DISTPATH%
pause

set PYTHON=\Root\Programmes\Python\

cd /d \Root\Projets\TeXMaths

%PYTHON%scripts\pyinstaller --onedir --distpath %DISTPATH% --noconfirm --windowed --clean exerciceGUI.py
%PYTHON%python src\exerciceGUI_data_installer.py %DISTPATH%

echo ExerciceGUI a bien été installé

pause