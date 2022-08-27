"""
test_feel: tests for feel, a module to filter rows by column values in a CSV file
"""
import csv

import pytest
import pandas as pd

from src import Operations, Terminal, Feel


class TestOperations:
    """test utility math operations"""

    def test_can_float(self):
        """test method for checking float values"""
        assert Operations.can_float(3.5)
        assert Operations.can_float(0.5)
        assert Operations.can_float(1)
        assert not Operations.can_float("ha")

    def test_can_int(self):
        """test method for checking int values"""
        assert not Operations.can_int(3.5)
        assert not Operations.can_int(0.5)
        assert Operations.can_int(1)
        assert not Operations.can_int("ha")

    def test_conjunction(self):
        """test method for conjunction operator"""
        assert Operations.conjunction(*[1, 2, 3])
        assert not Operations.conjunction(*[1, 2, 3, 0])
        assert Operations.conjunction(*[True, True, True])
        assert not Operations.conjunction(*[True, True, True, False])


class TestTerminal:
    """test utility command line operations"""

    def test_parser(self):
        """test command line parser generation"""
        parser = Terminal.parser()
        assert parser is not None
        parsed = parser.parse_args(["input.csv", "filtered.csv", "--filter", "ID:1234"])
        assert parsed.input == "input.csv"
        assert parsed.output == "filtered.csv"
        assert parsed.filter == ["ID:1234"]
        parsed = parser.parse_args(
            ["input.csv", "filtered.csv", "--filter", "ID:1234", "--filter", "Name:Doe"]
        )
        assert parsed.filter == ["ID:1234", "Name:Doe"]

    @pytest.mark.parametrize(
        "data",
        [
            ({"ID": [123], "Name": ["Feel"]}),
            ({"ID": [123, 342, 123], "Name": ["Feel", "Feel", "Feel"]}),
            ({"ID": [123], "Name": ["Feel"]}),
        ],
    )
    def test_reader(self, tmp_path, data):
        """test CSV file reader"""
        tmp_file = tmp_path / "test_reader.csv"

        with open(tmp_file, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
        dataframe = Terminal.reader(tmp_file)
        assert dataframe.equals(pd.DataFrame.from_dict(data))


class TestFeel:
    """test feel, a CSV filtering package"""

    @pytest.mark.parametrize(
        "data",
        [
            ({"ID": [123, 342, 1234], "Name": ["Feel", "Feel", "Feel"]}),
            ({"ID": [123], "Name": ["Feel"]}),
        ],
    )
    def test_filtering_equals(self, tmp_path, data):
        """test CSV file filtering"""
        tmp_file = tmp_path / "test_reader.csv"

        with open(tmp_file, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
        dataframe = pd.DataFrame.from_dict(data)
        filtered, _ = Feel.filtering(
            filters=["ID:123"], dataframe=dataframe, columns=list(data.keys())
        )
        assert filtered.shape == (1, 2)

    @pytest.mark.parametrize(
        "data",
        [
            ({"ID": [123], "Name": ["Feel"]}),
            ({"ID": [123, 123, 123], "Name": ["Feel1", "Feel2", "Feel3"]}),
        ],
    )
    def test_filtering_not_equals(self, tmp_path, data):
        """test CSV file filtering"""
        tmp_file = tmp_path / "test_reader.csv"

        with open(tmp_file, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
        dataframe = pd.DataFrame.from_dict(data)
        filtered, _ = Feel.filtering(
            filters=["ID:~123"], dataframe=dataframe, columns=list(data.keys())
        )
        assert filtered.shape == (0, 2)

    @pytest.mark.parametrize(
        "data",
        [
            ({"ID": [123, 124], "Name": ["Feel", "Feel"]}),
        ],
    )
    def test_filtering_greater_than(self, tmp_path, data):
        """test CSV file filtering"""
        tmp_file = tmp_path / "test_reader.csv"

        with open(tmp_file, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
        dataframe = pd.DataFrame.from_dict(data)
        filtered, _ = Feel.filtering(
            filters=["ID:>123"], dataframe=dataframe, columns=list(data.keys())
        )
        assert filtered.shape == (1, 2)

    @pytest.mark.parametrize(
        "data",
        [
            ({"ID": [123, 124], "Name": ["Feel", "Feel"]}),
        ],
    )
    def test_filtering_less_than(self, tmp_path, data):
        """test CSV file filtering"""
        tmp_file = tmp_path / "test_reader.csv"

        with open(tmp_file, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
        dataframe = pd.DataFrame.from_dict(data)
        filtered, _ = Feel.filtering(
            filters=["ID:<124"], dataframe=dataframe, columns=list(data.keys())
        )
        assert filtered.shape == (1, 2)

    @pytest.mark.parametrize(
        "data",
        [
            ({"ID": [123, 124, 125], "Name": ["Feel", "Feel", "Feel"]}),
        ],
    )
    def test_filtering_in(self, tmp_path, data):
        """test CSV file filtering"""
        tmp_file = tmp_path / "test_reader.csv"

        with open(tmp_file, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
        dataframe = pd.DataFrame.from_dict(data)
        filtered, _ = Feel.filtering(
            filters=["ID:124|123"], dataframe=dataframe, columns=list(data.keys())
        )
        assert filtered.shape == (2, 2)

    @pytest.mark.parametrize(
        "data",
        [
            ({"ID": [123, 124, 125], "Name": ["Feel", "Feel", "Feel"]}),
        ],
    )
    def test_filtering_not_in(self, tmp_path, data):
        """test CSV file filtering"""
        tmp_file = tmp_path / "test_reader.csv"

        with open(tmp_file, "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
        dataframe = pd.DataFrame.from_dict(data)
        filtered, _ = Feel.filtering(
            filters=["ID:~124|123"], dataframe=dataframe, columns=list(data.keys())
        )
        assert filtered.shape == (1, 2)
