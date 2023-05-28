# pylint: disable=E1133,E0213,E1136,E0213,E0211,E1102,C0301
"""
feel: a module to filter rows by column values in a CSV file

Usage
-----

    python3 feel test.csv --filter "col_name:filter_val" --filter "col_name:~filter_val" \
        --filter "col_name:>filter_val" --filter "col_name:<filter_val" --filter \
        "col_name:filter_vals|filter_vals" --filter "col_name:~filter_vals|filter_vals" \

Filters
-------

    TYPES                                      DESCRIPTION                          SUPPORTED TYPES

    "col_name:filter_val"                      col_name IS filter_val               [number, string]

    "col_name:~filter_val"                     col_name IS NOT filter_val           [number, string]

    "col_name:>filter_val"                     col_name IS GREATER THAN filter_val  [number]

    "col_name:<filter_val"                     col_name IS LESS THAN filter_val     [number]

    "col_name:val_1|val_2"                     col_name IS IN [val1, val2]          [number, string]

    "col_name:~val_1|val_2"                    col_name IS NOT IN [val1, val2]      [number, string]
"""
import argparse
import functools
import sys
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd

from feel import _version

__version__ = _version.get_versions()["version"]


FILTER_TYPES = """
FILTER TYPES\t\t\t\tDESCRIPTION\t\t\t\tSUPPORTED TYPES

"col_name:filter_val"\t\t\tcol_name IS filter_val\t\t\t[number, string]\n
"col_name:~filter_val"\t\t\tcol_name IS NOT filter_val\t\t[number, string]\n
"col_name:>filter_val"\t\t\tcol_name IS GREATER THAN filter_val\t[number]\n
"col_name:<filter_val"\t\t\tcol_name IS LESS THAN filter_val\t[number]\n
"col_name:filter_vals|filter_vals"\tcol_name IS IN [val1, val2]\t\t[number, string]\n         
"col_name:~filter_vals|filter_vals"\tcol_name IS NOT IN [val1, val2]\t\t[number, string]\n
"""
FILTER_OPERATORS = ["~", ">", "<", "|"]


class Operations:
    """Utility class for type operations."""

    @staticmethod
    def can_float(element: Any) -> bool:
        """
        Check whether a given object is a float.

        Args
        -----
            - element (Any): The object to check.

        Returns
        -------
            bool: True if the object can be converted to a float, False otherwise.
        """
        try:
            float(element)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def can_int(element: Any) -> bool:
        """
        Check whether a given object is an int.

        Args
        ----
            - element: The object to check.

        Returns
        -------
            bool: True if the object can be converted to an int, False otherwise.
        """
        try:
            return int(element) == element
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def conjunction(*conditions: List[Any]):
        """
        Chain pandas filters stored in a list together. See link below for more info :-
        https://stackoverflow.com/questions/13611065/efficient-way-to-apply-multiple-filters-to-pandas-dataframe-or-series

        Args
        -----
            - conditions: List of conditions to combine.

        Returns
        -------
            np.ndarray: Result of applying logical AND to the conditions.
        """
        return functools.reduce(np.logical_and, conditions)


class Terminal:
    """
    Utility class for common command line operations.
    """

    def _prettier(
        formatter: argparse.RawTextHelpFormatter, width: int = 120, height: int = 36
    ):
        """
        Return a wider HelpFormatter if possible to allow us to show a wider help message
        when python3 feel --help is run. See the link below for more info :-
        https://stackoverflow.com/questions/3853722/how-to-insert-newlines-on-argparse-help-text

        Args
        ----
            - formatter (argparse.RawTextHelpFormatter): The formatter object to be modified.
            - width (int): The desired width of the formatter. Default is 120.
            - height (int): The desired height of the formatter. Default is 36.

        Returns
        -------
            callable: The modified formatter function.
        """
        try:
            # https://stackoverflow.com/a/5464440
            # beware: "Only the name of this class is considered a public API."
            kwargs = {"width": width, "max_help_position": height}
            formatter(None, **kwargs)
            return lambda prog: formatter(prog, **kwargs)
        except TypeError:
            return formatter

    @staticmethod
    def parser() -> argparse.ArgumentParser:
        """
        Initialize command line parser with a wide text formatter.

        Returns
        -------
            argparse.ArgumentParser: The configured argument parser.
        """
        parser = argparse.ArgumentParser(
            formatter_class=Terminal._prettier(argparse.RawTextHelpFormatter)
        )
        parser.add_argument("input", help="path to input CSV file")
        parser.add_argument("output", help="path to output CSV file")
        parser.add_argument(
            "-v",
            "--verbose",
            help="display value counts for filtered columns",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-c",
            "--counts",
            help="display original value counts for filtered columns",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-n",
            "--normalize",
            help="whether to normalize value counts",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-s",
            "--sample",
            help="sample n rows from filtered CSV",
            type=int,
            default=None,
            nargs="?",
        )
        parser.add_argument(
            "-f", "--filter", action="append", help=f"{FILTER_TYPES}", required=True
        )
        return parser

    @staticmethod
    def reader(path: str) -> pd.DataFrame:
        """
        Read a CSV file into a pandas DataFrame.

        Args
        ----
            - path (str): The path to the CSV file.

        Returns
        -------
            pd.DataFrame: The DataFrame created from the CSV file.
        """
        return pd.read_csv(path)


class Feel(Terminal):
    """
    A class for performing primitive filter operations on a CSV file.
    """

    def _convert_filter(
        dataframe: pd.DataFrame, column: str, operator: str, filter_val: str
    ) -> pd.Series:
        """
        Create a pandas filter from a command line filter.

        Args
        ----
            - dataframe (pd.DataFrame): The dataframe we are operating on (parsed from CSV).
            - column (str): The column we want to filter by.
            - operator (str): The filtering operator (~, <, >).
            - filter_val (str): The column value we want to filter by.

        Returns
        -------
            pd.Series: The pandas filter condition.
        """
        if isinstance(filter_val, list):
            if operator == "~":
                return ~(dataframe[column].isin(filter_val))
            return dataframe[column].isin(filter_val)
        if operator == "~":
            return ~(dataframe[column] == filter_val)
        if operator == ">":
            return dataframe[column] > filter_val
        if operator == "<":
            return dataframe[column] < filter_val
        return dataframe[column] == filter_val

    @staticmethod
    def _column_filter(
        dataframe: pd.DataFrame,
        filter_val: str,
        column: str,
        operator: Optional[str] = None,
    ) -> pd.Series:
        """
        Parse command line filter and convert it to a pandas filter condition.

        Args
        ----
            dataframe (pd.DataFrame): The dataframe we are operating on (parsed from CSV).
            filter_val (str): The column value we want to filter by.
            column (str): The column we want to filter by.
            operator (str): The filtering operator (~, <, >, |).

        Returns
        -------
            pd.Series: The pandas filter condition.
        """
        float_val = Operations.can_float(filter_val)
        int_val = Operations.can_int(filter_val)
        list_val = "|" in filter_val
        if float_val or int_val:
            if Operations.can_float(filter_val):
                return Feel._convert_filter(
                    dataframe, column, operator, float(filter_val)
                )
            return Feel._convert_filter(dataframe, column, operator, int(filter_val))
        if list_val:
            multi_val = filter_val.split("|")
            float_list, int_list = Operations.can_float(
                multi_val[0]
            ), Operations.can_int(filter_val[0])
            if float_list or int_list:
                if float_list:
                    converted_multi_val = [float(val) for val in multi_val]
                else:
                    converted_multi_val = [int(val) for val in multi_val]
                return Feel._column_filter(
                    dataframe, converted_multi_val, column, operator
                )
            return Feel._column_filter(dataframe, multi_val, column, operator)
        return Feel._convert_filter(dataframe, column, operator, filter_val)

    def filtering(
        filters: List[Any], dataframe: pd.DataFrame, columns: str
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Verify a filter value is of the right format

        Args
        ----
            - filters (List[Any]): The list of filter values to apply.
            - dataframe (pd.DataFrame): The dataframe to filter.
            - columns (List[str]): The list of column names in the dataframe.

        Returns
        -------
            Tuple[pd.DataFrame, List[str]]: A tuple containing the filtered dataframe and the list of
                                            columns used for filtering.

        Raises
        ------
            argparse.ArgumentTypeError: If a filter value is not in the correct format or if a column
                                        is not valid.


        FILTER TYPES                              DESCRIPTION                             SUPPORTED TYPES

        "col_name:filter_val"                     col_name IS filter_val                  [number, string]

        "col_name:~filter_val"                    col_name IS NOT filter_val              [number, string]

        "col_name:>filter_val"                    col_name IS GREATER THAN filter_val     [number]

        "col_name:<filter_val"                    col_name IS LESS THAN filter_val        [number]

        "col_name:filter_vals|filter_vals"        col_name IS IN [val1, val2]             [number, string]

        "col_name:~filter_vals|filter_vals"       col_name IS NOT IN [val1, val2]         [number, string]
        """
        concatenated = []
        in_use = []
        for value in filters:
            split = value.split(":", 1)
            # filter type
            if len(split) != 2:
                raise argparse.ArgumentTypeError(
                    f"{value} is not a valid column filter.\n" + "{FILTER_TYPES}"
                )
            column, filter_val = split[0], split[1]
            in_use.append(column)
            if column not in columns:
                raise argparse.ArgumentTypeError(
                    f"{column} is not a valid column.\n" + f"Use one of: {columns}"
                )
            # parse operator / convert to pandas friendly format
            has_operator = any(
                operator for operator in FILTER_OPERATORS if operator in filter_val
            )
            if has_operator:
                if "~" in filter_val:
                    operator, stripped_val = (
                        "~",
                        filter_val.split("~")[1],
                    )
                    concatenated.append(
                        Feel._column_filter(dataframe, stripped_val, column, operator)
                    )
                elif ">" in filter_val:
                    operator, stripped_val = (
                        ">",
                        filter_val.split(">")[1],
                    )
                    concatenated.append(
                        Feel._column_filter(dataframe, stripped_val, column, operator)
                    )
                elif "<" in filter_val:
                    operator, stripped_val = (
                        "<",
                        filter_val.split("<")[1],
                    )
                    concatenated.append(
                        Feel._column_filter(dataframe, stripped_val, column, operator)
                    )
                else:
                    concatenated.append(
                        Feel._column_filter(dataframe, filter_val, column)
                    )
            else:
                concatenated.append(Feel._column_filter(dataframe, filter_val, column))
        return dataframe[Operations.conjunction(*concatenated)], in_use

    @staticmethod
    def cli(cli_args: argparse.Namespace):
        """
        Process command line arguments and perform the filtering operation.

        Args
        ----
            - cli_args (argparse.Namespace): The command line arguments.

        Raises
        ------
            SystemExit: If a valid path to input/output CSV is not provided.
        """
        if cli_args.input == "" or cli_args.output == "":
            print("valid path to input/output CSV is required")
            sys.exit()
        # read CSV into a pandas dataframe + extract column names using pandas
        original_dataframe: pd.DataFrame = Feel.reader(cli_args.input)
        dataframe_columns: List[Any] = list(original_dataframe.columns)
        # apply pandas filters on dataframe
        filtered_dataframe, col_in_use = Feel.filtering(
            cli_args.filter, original_dataframe, dataframe_columns
        )

        if cli_args.sample is not None:
            print(f"\nsampled: {cli_args.sample} rows")
            filtered_dataframe = filtered_dataframe.sample(n=cli_args.sample)
        if cli_args.verbose:
            for col in col_in_use:
                if cli_args.counts:
                    print(
                        f"\nOriginal Counts: {col}\n\n{original_dataframe[col].value_counts(normalize=cli_args.normalize).to_markdown()}"
                    )
                print(
                    f"\nFiltered Counts: {col}\n\n{filtered_dataframe[col].value_counts(normalize=cli_args.normalize).to_markdown()}"
                )
        filtered_dataframe.to_csv(cli_args.output, index=False)
