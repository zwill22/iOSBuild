import pytest
from ios_build.run import runner


def testRunnerNoArgs(capsys):
    assert runner() == 2
    captured = capsys.readouterr()
    try:
        assert (
            "iOSBuild: error: the following arguments are required: path"
            in captured.err
        )
    except AssertionError:
        assert "iOSBuild: error: unrecognized arguments: " in captured.err


test_cases = [
    ([], 2, "iOSBuild: error: the following arguments are required: path"),
    (["example", "-D"], 2, "iOSBuild: error: argument -D: expected one argument"),
    (
        ["example", "-DPLATFORM=IOS"],
        1,
        "Invalid input: CMake option PLATFORM is used by iOSBuild and cannot be specified",
    ),
    (
        ["example", "-DOPTION=VALUE", "-DOPTION=VALUE"],
        1,
        "Invalid input: Option OPTION already specified",
    ),
    (["example", "--cmake", "notcmake"], 1, "Error: CMake not found"),
    (["example", "--cmake", "xcodebuild"], 2, "xcodebuild: error: invalid option"),
]


# TODO Simulate an XCodeError
@pytest.mark.parametrize("args, exit_code, error", test_cases)
def testRunner(capsys, args, exit_code, error):
    code = runner(args=args)
    assert code == exit_code
    captured = capsys.readouterr()
    err_out = captured.err
    assert error in err_out


@pytest.mark.slow
def testRun(tmp_path):
    args = ["example", "--output-dir={}".format(tmp_path)]
    assert runner(args=args) == 0
