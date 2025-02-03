import pytest

from ios_build import printer

def testPrintValue(capsys):
    with pytest.raises(TypeError):
        printer.printValue(None, None)
    printer.printValue("text", "value", end='\n')

    captured = capsys.readouterr()

    assert captured.out == "text                             value\n"

def testPrintTick(capsys):
    printer.tick()

    captured = capsys.readouterr()

    assert captured.out == "\U00002705\n"

def testPrintCross(capsys):
    printer.cross()

    captured = capsys.readouterr()

    assert captured.out == "\U0000274c\n"

test_cases = [
    ({}, ""),
    ({"key": "value"}, "key                              value\n"),
    ({"key": "value", "key2": {"newkey": "newval"}}, 
     "key                              value\nkey2:\nnewkey                           newval\n"),
    ({"key": "value", "key2": {"newkey": "newval", "newkey2": {"newnewkey": "newnewval"}}}, 
     "key                              value\nkey2:\nnewkey                           newval\nnewkey2:\nnewnewkey                        newnewval\n")
]

@pytest.mark.parametrize('value, expected_output', test_cases)
def testEmbeddedDict(capsys, value, expected_output):
    printer.printEmbeddedDict(value)

    captured = capsys.readouterr()
    printer.printEmbeddedDict(value)
    assert captured.out == expected_output
