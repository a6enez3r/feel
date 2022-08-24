"""
    feel: a tiny CLI to filter rows by column values in a CSV file
"""
import sys
from src import Feel
from typing import List, Any

import pandas as pd

def main():
    cli_parser = Feel.get_parser()
    cli_args = cli_parser.parse_args()
    if cli_args.input == "" or cli_args.output == "":
        print("valid path to input/output CSV is required")
        sys.exit()
    # read CSV into a pandas dataframe + extract column names using pandas
    csv_dataframe: pd.DataFrame = Feel.get_file(cli_args.input)
    dataframe_columns: List[Any] = list(csv_dataframe.columns)
    # translate command line filters into a format acceptable by pandas
    col_filters, col_in_use = Feel.apply_filters(
        cli_args.filter, csv_dataframe, dataframe_columns
    )
    # apply pandas filters on dataframe
    filtered = csv_dataframe[Feel.conjunction(*col_filters)]
    
    if cli_args.sample is not None:
        print(f"\nsampled: {cli_args.sample} rows")
        filtered = filtered.sample(n=cli_args.sample)    
    if cli_args.verbose:
        for col in col_in_use:
            if cli_args.counts:
                print(
                    f"\nOriginal Counts: {col}\n\n{csv_dataframe[col].value_counts(normalize=cli_args.normalize).to_markdown()}"
                )
            print(
                f"\nFiltered Counts: {col}\n\n{filtered[col].value_counts(normalize=cli_args.normalize).to_markdown()}"
            )
    filtered.to_csv(cli_args.output, index=False)

if __name__ == '__main__':
    main()