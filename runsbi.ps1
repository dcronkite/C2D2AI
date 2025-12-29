# input dir is the dir of the notes for patients
# $INPUT_DIR = "C:\reev\data\proj_SBI\ESPRESSO-2023\input\"
# $OUTPUT_DIR = "C:\reev\data\proj_SBI\ESPRESSO-2023\output\raw\"
# $OUTPUT_SUMMARY_DIR = "C:\reev\data\proj_SBI\ESPRESSO-2023\output\summary\"
# $RULES_DIR = "C:\reev\data\proj_SBI\ESPRESSO-2023\SBI\"

# Get the directory where the script is located
$DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

$INPUT_DIR = Join-Path $DIR "input"
$OUTPUT_DIR = Join-Path $DIR "output\raw"
$OUTPUT_SUMMARY_DIR = Join-Path $DIR "output\summary"
$RULES_DIR = Join-Path $DIR "SBI"

Write-Host $INPUT_DIR

java -Xms512M -Xmx2000M -jar MedTagger-fit.jar "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
.venv\Scripts\python SBI\model\run_output_sbi.py "$OUTPUT_DIR" "$OUTPUT_SUMMARY_DIR" "1"