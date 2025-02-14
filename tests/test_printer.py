import pytest

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

    printer.printEmbeddedDict(value, verbosity=print_level+1)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
