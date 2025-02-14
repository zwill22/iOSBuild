import tempfile
import sys
import datetime


class Printer:
    """
    Class to handle all printing using a verbosity scale to determine what to print
    """

    def __init__(self, print_level=0):
        """
        Initialise printer based on desired verbosity

        Args:
            verbose (int, optional): Verbosity level for printer. Defaults to None.
            quiet (bool, optional): Set output to quiet. Defaults to False.

        Raises:
            PrinterError: Raised if both quiet and verbose specified simultaneously
        """
        self.verbosity = print_level
        self.width = 34

    def print(self, value, verbosity=0, **kwargs):
        if self.verbosity >= verbosity:
            print(value, **kwargs)

    def printValue(self, text, value, verbosity=0, **kwargs):
        """
        Print a value inline with a fixed width for key.
        Args:
            text (str): Key for printed value
            value (str): value to be printed
            verbosity (int): The level of verbosity at which the statement should be printed. Defaults to 0.
        """
        if self.verbosity >= verbosity:
            print("{0:<32} {1}".format(text, value), **kwargs)

    def tick(self, verbosity=0, **kwargs):
        """
        Print a \U00002705 character

        Args:
            verbosity (int): The level of verbosity at which the statement should be printed. Defaults to 0.
        """
        if self.verbosity >= verbosity:
            print("\U00002705", **kwargs)

    def cross(self, verbosity=0, **kwargs):
        """
        Print a \U0000274c character

        Args:
            verbosity (int): The level of verbosity at which the statement should be printed. Defaults to 0.
        """
        if self.verbosity >= verbosity:
            print("\U0000274c", **kwargs)

    def printStat(self, text, tick="tick", **kwargs):
        self.printValue(text, "", end="\t", **kwargs)
        if tick == "tick":
            self.tick(**kwargs)
        elif tick == "cross":
            self.cross(**kwargs)
        else:
            self.print("", **kwargs)

    def printEmbeddedDict(
        self, input_dict: dict, verbosity: int = 0, header: str = None
    ):
        """
        Print a dictionary using a recursive algorithm
        for embedded dictionaries.

        Args:
            input_dict (dict): Input dictionary
            verbosity (int): The level of verbosity at which the statement should be printed. Defaults to 0.
            he
        """
        if self.verbosity < verbosity:
            return
        if header:
            print("{}:".format(header))
        for k, v in input_dict.items():
            if type(v) is dict:
                print("{}:".format(k))
                self.printEmbeddedDict(v, verbosity=verbosity)
            elif type(v) is tempfile.TemporaryDirectory:
                self.printValue(k, v.name, end="\n", verbosity=verbosity)
            else:
                self.printValue(k, v, end="\n", verbosity=verbosity)

    def showOutput(self):
        return self.verbosity > 0

    def showError(self):
        return self.verbosity > 1

    def printError(self, value):
        sys.stderr.buffer.write(value)

    def printHeader(self, **kwargs):
        if self.verbosity < 0:
            return

        with open("ios_build/logo.txt", "r") as f:
            logo = f.read()

        n = max([len(line) for line in logo.split("\n")])
        assert n == self.width
        print(logo)
        print()

    def printFooter(self, **kwargs) -> str:
        if self.verbosity < 0:
            return

        n = self.width
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("\U0001f5a5 " * n)
        print("iOSBuild complete")
        print("Time:\t{}".format(time))
        print("\U0001f4bb" * n)

        return time


def getPrinter(**kwargs) -> Printer:
    return kwargs.get("printer", Printer())
