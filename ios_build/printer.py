def printValue(text, value, end="\t"):
    """
    Print a value inline with a fixed width for key.

    Args:
        text (_type_): Key for printed value
        value (_type_): value to be printed
        end (str, optional): End character for `print`. Defaults to "\t".
    """
    print("{0:<32} {1}".format(text, value), end=end)


def tick():
    """
    Print a \U00002705 character
    """
    print("\U00002705")


def cross():
    """
    Print a \U0000274c character
    """
    print("\U0000274c")


def printEmbeddedDict(input_dict: dict):
    """
    Print a dictionary using a recursive algorithm
    for embedded dictionaries.

    Args:
        input_dict (dict): Input dictionary
    """
    for k, v in input_dict.items():
        if type(v) is dict:
            print("{}:".format(k))
            printEmbeddedDict(v)
        else:
            printValue(k, v, end="\n")
