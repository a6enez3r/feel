"""
    feel: a CLI to filter CSVs on the command line by column & row values
"""
from feel import Feel


def main():
    """
    Main function encapsulating command line logic.
    """
    parser = Feel.parser()
    args = parser.parse_args()
    Feel.cli(args)


if __name__ == "__main__":
    main()
