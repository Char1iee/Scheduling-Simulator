# CSV Upload Error Test Files

Test CSV error handling in the Platform UI uploader (`Upload .csv or .json workload`). 

## Files and expected behavior

- `00_valid_reference.csv`
  - Valid control file; should parse successfully.

- `01_missing_required_columns.csv`
  - Missing `burst_time` column.
  - Expected error: `CSV is missing required columns: burst_time`

- `02_header_only.csv`
  - Has header only, no data rows.
  - Expected error: `CSV has a header but no rows`

- `03_missing_burst_value.csv`
  - Blank `burst_time` value in row 1.
  - Expected error: `Missing 'burst_time' in row 1`

- `04_invalid_arrival_integer.csv`
  - Non-integer `arrival_time` (`abc`) in row 1.
  - Expected error: `Invalid integer for 'arrival_time' in row 1`

- `05_negative_arrival.csv`
  - `arrival_time` is negative.
  - Expected error: `'arrival_time' in row 1 must be >= 0`

- `06_zero_burst.csv`
  - `burst_time` is zero.
  - Expected error: `'burst_time' in row 1 must be >= 1`

- `07_duplicate_job_id.csv`
  - Duplicate `job_id` values.
  - Expected error: `Duplicate job_id=1 at row 2`

- `08_empty.csv`
  - Empty file.
  - Expected error: `CSV appears to be empty`
