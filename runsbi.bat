@echo off
REM input dir is the dir of the notes for patients
REM INPUT_DIR="C:\reev\data\proj_SBI\ESPRESSO-2023\input\"
REM OUTPUT_DIR="C:\reev\data\proj_SBI\ESPRESSO-2023\output\raw\"
REM OUTPUT_SUMMARY_DIR="C:\reev\data\proj_SBI\ESPRESSO-2023\output\summary\"
REM RULES_DIR="C:\reev\data\proj_SBI\ESPRESSO-2023\SBI\"

setlocal
set DIR=%~dp0
set DIR=%DIR:~0,-1%

set INPUT_DIR=%DIR%\input\
set OUTPUT_DIR=%DIR%\output\raw\
set OUTPUT_SUMMARY_DIR=%DIR%\output\summary\
set RULES_DIR=%DIR%\SBI\

echo %INPUT_DIR%

java -Xms512M -Xmx2000M -jar MedTagger-fit.jar "%INPUT_DIR%" "%OUTPUT_DIR%" "%RULES_DIR%"
.venv\Scripts\python SBI\model\run_output_sbi.py "%OUTPUT_DIR%" "%OUTPUT_SUMMARY_DIR%" "1"

endlocal