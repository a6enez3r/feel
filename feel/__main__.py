"""
    feel: a tiny CLI to filter rows by column values in a CSV file
"""
from feel import Feel


def main():
    """
    main function encapsulating command line logic
    """
    parser = Feel.parser()
    args = parser.parse_args()
    Feel.cli(args)


if __name__ == "__main__":
    main()
