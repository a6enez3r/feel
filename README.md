# `feel` [![test](https://github.com/a6enez3r/feel/actions/workflows/test.yml/badge.svg)](https://github.com/a6enez3r/feel/actions/workflows/test.yml)

Is a tiny python CLI that allows you to filter CSV rows by column values on the command line. It it built on top of `pandas` & has a relatively low memory footprint. Currently supports the following filter operations:

```
    TYPES                                      DESCRIPTION                          SUPPORTED TYPES

    "col_name:filter_val"                      col_name IS filter_val               [number, string]

    "col_name:~filter_val"                     col_name IS NOT filter_val           [number, string]

    "col_name:>filter_val"                     col_name IS GREATER THAN filter_val  [number]

    "col_name:<filter_val"                     col_name IS LESS THAN filter_val     [number]

    "col_name:val_1|val_2"                     col_name IS IN [val1, val2]          [number, string]

    "col_name:~val_1|val_2"                    col_name IS NOT IN [val1, val2]      [number, string]
```
and is invoked with the following syntax
```

    feel input.csv filtered.csv --filter "col_name:filter_val" --filter "col_name:~filter_val" \
        --filter "col_name:>filter_val" --filter "col_name:<filter_val" --filter \
        "col_name:filter_vals|filter_vals" --filter "col_name:~filter_vals|filter_vals" \
```

## Quickstart

- Create a virtual environment & install all dependencies
```
python3 -m venv venv
source venv/bin/activate
make deps
```
- Install CLI dependencies & the CLI itself
```
make pkg-install
```
- Run `feel --help` to see all available options
```
usage: feel [-h] [-v] [-c] [-n] [-s [SAMPLE]] -f FILTER input output

positional arguments:
  input                           path to input CSV file
  output                          path to output CSV file

optional arguments:
  -h, --help                      show this help message and exit
  -v, --verbose                   display value counts for filtered columns
  -c, --counts                    display original value counts for filtered columns
  -n, --normalize                 whether to normalize value counts
  -s [SAMPLE], --sample [SAMPLE]  sample n rows from filtered CSV
  -f FILTER, --filter FILTER      
                                  FILTER TYPES                         DESCRIPTION                              SUPPORTED TYPES
                                  
                                  "col_name:filter_val"                col_name IS filter_val                   [number, string]
                                  
                                  "col_name:~filter_val"               col_name IS NOT filter_val               [number, string]
                                  
                                  "col_name:>filter_val"               col_name IS GREATER THAN filter_val      [number]
                                  
                                  "col_name:<filter_val"               col_name IS LESS THAN filter_val         [number]
                                  
                                  "col_name:filter_vals|filter_vals"   col_name IS IN [val1, val2]              [number, string]
                                           
                                  "col_name:~filter_vals|filter_vals"  col_name IS NOT IN [val1, val2]          [number, string]
```
