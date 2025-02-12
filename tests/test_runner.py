import pytest
from ios_build.run import runner


def checkRunner(args, exit_code, capfd=None, err=None, out=None):
    assert runner(args=args) == exit_code
    if capfd:
        captured = capfd.readouterr()
        if err:
            assert err in captured.err
        if out:
            assert out in captured.out


def testRunner(capfd):
    # Environment dependent error
    try:
        checkRunner(None, 2, capfd, err="iOSBuild: error: unrecognized arguments:")
    except AssertionError:
        checkRunner(
            None,
            2,
            capfd,
            err="iOSBuild: error: the following arguments are required: path",
        )

    args = []
    checkRunner(
        args,
        2,
        capfd,
        err="iOSBuild: error: the following arguments are required: path",
    )

    args.append("example")
    args.append("-D")
    checkRunner(
        args, 2, capfd, err="iOSBuild: error: argument -D: expected one argument"
    )

    args[1] = "-DPLATFORM=IOS"
    checkRunner(
        args,
        1,
        capfd,
        out="Invalid input: CMake option PLATFORM is used by iOSBuild and cannot be specified",
    )

    args[1] = "-DOPTION=VALUE"
    args.append("-DOPTION=VALUE")
    checkRunner(args, 1, capfd, out="Invalid input: Option OPTION already specified")

    args[1] = "--cmake"
    args[2] = "notcmake"
    checkRunner(args, 1, capfd, out="Error: CMake not found")

    # TODO Simulate a CMake error
    # TODO Simulate an xcodebuilderror


# TODO Fix code so this test always works!!!
@pytest.mark.slow
def testRun():
    args = ["example"]
    checkRunner(args, 0)
