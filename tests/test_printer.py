import pytest
import tempfile

from ios_build.printer import Printer, getPrinter


def testGetPrinter():
    kwargs = {}
    printer = getPrinter(**kwargs)
    assert type(printer) is Printer
    assert printer.verbosity == 0

    for print_level in range(-1, 3):
        printer = Printer(print_level=print_level)

        kwargs["printer"] = printer

        new_printer = getPrinter(**kwargs)
        assert type(new_printer) is Printer
        assert new_printer.verbosity == print_level


@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrint(capsys, print_level):
    printer = Printer(print_level=print_level)
    with pytest.raises(TypeError):
        printer.printValue(None, verbosity=print_level)
    printer.print("text", verbosity=print_level)

    captured = capsys.readouterr()
    assert captured.out == "text\n"

    printer.print("text", verbosity=print_level + 1)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrintValue(capsys, print_level):
    printer = Printer(print_level=print_level)
    with pytest.raises(TypeError):
        printer.printValue(None, None, verbosity=print_level)
    printer.printValue("text", "value", verbosity=print_level)

    captured = capsys.readouterr()
    assert captured.out == "text                             value\n"

    printer.printValue("text", "value", verbosity=print_level + 1)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrintTick(capsys, print_level):
    printer = Printer(print_level=print_level)
    printer.tick(verbosity=print_level)

    captured = capsys.readouterr()
    assert captured.out == "\U00002705\n"

    printer.tick(verbosity=print_level + 1)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrintCross(capsys, print_level):
    printer = Printer(print_level=print_level)
    printer.cross(verbosity=print_level)

    captured = capsys.readouterr()
    assert captured.out == "\U0000274c\n"

    printer.cross(verbosity=print_level + 1)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


ticks = [("tick", "\U00002705"), ("cross", "\U0000274c"), ("other", "")]


@pytest.mark.parametrize("tick, output", ticks)
@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrintStat(capsys, tick, output, print_level):
    printer = Printer(print_level=print_level)
    with pytest.raises(TypeError):
        printer.printStat(None, tick=tick, verbosity=print_level)
    printer.printStat("text", verbosity=print_level, tick=tick)

    captured = capsys.readouterr()
    assert captured.out == "text                             \t" + output + "\n"

    printer.printStat("text", tick=tick, verbosity=print_level + 1)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


test_cases = [
    ({}, ""),
    ({"key": "value"}, "key                              value\n"),
    (
        {"key": "value", "key2": {"newkey": "newval"}},
        "key                              value\nkey2:\nnewkey                           newval\n",
    ),
    (
        {
            "key": "value",
            "key2": {"newkey": "newval", "newkey2": {"newnewkey": "newnewval"}},
        },
        "key                              value\nkey2:\nnewkey                           newval\nnewkey2:\nnewnewkey                        newnewval\n",
    ),
]


@pytest.mark.parametrize("print_level", range(-1, 3))
@pytest.mark.parametrize("value, expected_output", test_cases)
def testEmbeddedDict(capsys, value, expected_output, print_level):
    printer = Printer(print_level=print_level)
    printer.printEmbeddedDict(value, verbosity=print_level)

    captured = capsys.readouterr()
    assert captured.out == expected_output

    printer.printEmbeddedDict(value, verbosity=print_level + 1)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize("print_level", range(-1, 3))
@pytest.mark.parametrize("value, expected_output", test_cases)
def testHeaderDict(capsys, value, expected_output, print_level):
    printer = Printer(print_level=print_level)
    printer.printEmbeddedDict(value, header="A header", verbosity=print_level)

    captured = capsys.readouterr()
    assert captured.out == "A header:\n" + expected_output

    printer.printEmbeddedDict(value, header="A header", verbosity=print_level + 1)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize("print_level", range(-1, 3))
def testTempDir(capsys, tmp_path, print_level):
    tmp = tempfile.TemporaryDirectory(dir=tmp_path)
    kwargs = {"Dir": tmp}

    printer = Printer(print_level=print_level)

    printer.printEmbeddedDict(kwargs, verbosity=print_level)

    capture = capsys.readouterr()

    assert capture.out == "Dir                              {}\n".format(tmp.name)


@pytest.mark.parametrize("print_level", range(-1, 3))
def testShowOutput(print_level):
    printer = Printer(print_level=print_level)
    val = print_level > 0
    assert printer.showOutput() == val


@pytest.mark.parametrize("print_level", range(-1, 3))
def testShowError(print_level):
    printer = Printer(print_level=print_level)
    val = print_level > 1
    assert printer.showError() == val


@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrintError(capsys, print_level):
    printer = Printer(print_level=print_level)

    printer.printError("An error".encode())

    capture = capsys.readouterr()
    assert capture.out == ""
    assert capture.err == "An error"


@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrintHeader(capsys, print_level):
    printer = Printer(print_level=print_level)
    printer.printHeader()
    capture = capsys.readouterr()
    assert capture.err == ""
    if print_level < 0:
        assert capture.out == ""
        return

    with open("ios_build/logo.txt", "r") as f:
        logo = f.read()
        logo += "\n\n"

    assert capture.out == logo


@pytest.mark.parametrize("print_level", range(-1, 3))
def testPrintFooter(capsys, print_level):
    printer = Printer(print_level=print_level)
    time = printer.printFooter()
    capture = capsys.readouterr()
    assert capture.err == ""
    if print_level < 0:
        assert capture.out == ""
        return

    n = printer.width

    expected = "\U0001f5a5 " * n
    expected += "\niOSBuild complete\n"
    expected += "Time:\t{}\n".format(time)
    expected += "\U0001f4bb" * n
    expected += "\n"

    assert capture.out == expected
