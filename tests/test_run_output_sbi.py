import pytest
import csv
from pathlib import Path
from run_output_sbi import run_eval_sbi

def test_run_eval_sbi(tmp_path):
    tests_dir = Path(__file__).parent
    input_dir = tests_dir / 'data' / 'input'
    output_dir = tmp_path / 'output'
    expected_file = tests_dir / 'data' / 'expected_patient_level.csv'

    run_eval_sbi(input_dir, output_dir)

    # check output exists
    output_file = output_dir / 'patient_level.csv'
    assert output_file.exists()

    with open(output_file) as fh:
        actual_rows = list(csv.reader(fh, delimiter='|'))

    with open(expected_file) as fh:
        expected_rows = list(csv.reader(fh, delimiter='|'))

    # sort rows by filename to ensure comparison is consistent
    actual_rows.sort(key=lambda x: x[0])
    expected_rows.sort(key=lambda x: x[0])

    assert len(actual_rows) == len(expected_rows)
    for actual, expected in zip(actual_rows, expected_rows):
        assert actual == expected
