# pylint: disable=E1133,E0213,E1136,E0213,E0211,E1102,C0301
"""
feel: a module to filter rows by column values in a CSV file

invoked:

    python3 feel input.csv --filter "col_name:filter_val" --filter "col_name:~filter_val" \
        --filter "col_name:>filter_val" --filter "col_name:<filter_val" --filter \
        "col_name:filter_vals|filter_vals" --filter "col_name:~filter_vals|filter_vals" \

filters:

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
from typing import List, Any, Optional

import pandas as pd
import numpy as np


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


class Feel:
    """
    primitive filter operations on a CSV file
    """

    def is_float(element: Any) -> bool:
        """
        check whether a given object is a float
        """
        try:
            float(element)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    def is_int(element: Any) -> bool:
        """
        check whether a given object is an int
        """
        try:
            int(element)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    def conjunction(*conditions: List[Any]):
        """
        chain pandas filters stored in a list together

        https://stackoverflow.com/questions/13611065/efficient-way-to-apply-multiple-filters-to-pandas-dataframe-or-series
        """
        return functools.reduce(np.logical_and, conditions)

    def get_formatter(
        formatter: argparse.RawTextHelpFormatter, width: int = 120, height: int = 36
    ):
        """
        Return a wider HelpFormatter if possible to allow us to show a wider help message
        when python3 feel --help is run

        https://stackoverflow.com/questions/3853722/how-to-insert-newlines-on-argparse-help-text
        """
        try:
            # https://stackoverflow.com/a/5464440
            # beware: "Only the name of this class is considered a public API."
            kwargs = {"width": width, "max_help_position": height}
            formatter(None, **kwargs)
            return lambda prog: formatter(prog, **kwargs)
        except TypeError:
            argparse.ArgumentTypeError("argparse help formatter failed, falling back.")
            return formatter

    def get_parser() -> argparse.ArgumentParser:
        """
        Initialize command line parser with a wide text formatter
        """
        parser = argparse.ArgumentParser(
            formatter_class=Feel.get_formatter(argparse.RawTextHelpFormatter)
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
            nargs="?"
        )
        parser.add_argument(
            "-f", "--filter", action="append", help=f"{FILTER_TYPES}", required=True
        )
        return parser

    def get_file(path: str) -> pd.DataFrame:
        """
        read CSV file into dataframe

        :param path (str): path to CSV file we want to filter
        """
        return pd.read_csv(path)

    def convert_filter(
        dataframe: pd.DataFrame, column: str, operator: str, filter_val: str
    ):
        """
        create a pandas filter from a command line filter

        :param dataframe (pd.DataFrame): dataframe we are operating on (parsed from CSV)
        :param filter_val (str): the column value we want to filter by
        :param column (str): column we want to filter by
        :param operator (str): filtering operator (~, <, >)
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
    def column_filter(
        dataframe: pd.DataFrame,
        filter_val: str,
        column: str,
        operator: Optional[str] = None,
    ):
        """
        parse command line filter & convert it to a pandas filter condition

        :param dataframe (pd.DataFrame): dataframe we are operating on (parsed from CSV)
        :param filter_val (str): the column value we want to filter by
        :param column (str): column we want to filter by
        :param operator (str): filtering operator (~, <, >, |)
        """
        float_val = Feel.is_float(filter_val)
        int_val = Feel.is_int(filter_val)
        list_val = "|" in filter_val
        if float_val or int_val:
            if Feel.is_float(filter_val):
                return Feel.convert_filter(
                    dataframe, column, operator, float(filter_val)
                )
            return Feel.convert_filter(
                dataframe, column, operator, int(filter_val)
            )
        if list_val:
            multi_val = filter_val.split("|")
            float_list, int_list = Feel.is_float(multi_val[0]), Feel.is_int(
                filter_val[0]
            )
            if float_list or int_list:
                if float_list:
                    converted_multi_val = [float(val) for val in multi_val]
                else:
                    converted_multi_val = [int(val) for val in multi_val]
                return Feel.column_filter(
                    dataframe, converted_multi_val, column, operator
                )
            return Feel.column_filter(
                dataframe, multi_val, column, operator
            )
        return Feel.convert_filter(dataframe, column, operator, filter_val)

    def apply_filters(filters: List[Any], dataframe: pd.DataFrame, columns: str):
        """
        verify a filter value is of the right format

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
                        Feel.column_filter(
                            dataframe, stripped_val, column, operator
                        )
                    )
                elif ">" in filter_val:

                    operator, stripped_val = (
                        ">",
                        filter_val.split(">")[1],
                    )
                    concatenated.append(
                        Feel.column_filter(
                            dataframe, stripped_val, column, operator
                        )
                    )
                elif "<" in filter_val:
                    operator, stripped_val = (
                        "<",
                        filter_val.split("<")[1],
                    )
                    concatenated.append(
                        Feel.column_filter(
                            dataframe, stripped_val, column, operator
                        )
                    )
                else:
                    concatenated.append(
                        Feel.column_filter(dataframe, filter_val, column)
                    )
            else:
                concatenated.append(
                    Feel.column_filter(dataframe, filter_val, column)
                )
        return concatenated, in_use

