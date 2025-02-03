def printValue(text, value, end="\t"):
    print("{0:<32} {1}".format(text, value), end=end)


def tick():
    print("\U00002705")


def cross():
    print("\U0000274c")


def printEmbeddedDict(input_dict: dict):
    for k, v in input_dict.items():
        if type(v) is dict:
            print("{}:".format(k))
            printEmbeddedDict(v)
        else:
            printValue(k, v, end="\n")
