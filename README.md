# iOSBuild

[![macOS][macos-badge]][macos]
[![Python][python-badge]][python]
[![GitHub][github-badge]][github]
[![uv][uv-badge]][uv]
[![Pytest][pytest-badge]][pytest]
[![GitHub Actions][github-actions-badge]][github-actions]
[![CI Build][ci-badge]][ci-build]
[![Read the Docs][rtd-badge]][rtd]
[![Documentation Status][doc-badge]][doc]
[![CodeCov][codecov-badge]][codecov]
[![Coverage][coverage-badge]][coverage]
[![License: MIT][license-badge]][license]
[![Buy Me A Coffee][buy-me-a-coffee-badge]][buy-me-a-coffee]
[![No AI][noai-badge]](#)

Welcome to iOSBuild, a Python application for building CMake libraries for Apple systems.
The aim of the project is to use a `CMakeLists.txt` file to generate an
[XCFramework](https://developer.apple.com/documentation/xcode/creating-a-multi-platform-binary-framework-bundle)
containing static libraries for use across iOS and other Apple operating systems.

This project makes use of the [ios-cmake toolchain](https://github.com/leetal/ios-cmake)
to configure and build the libraries using [CMake](https://cmake.org).
The libraries are built for each of the specified platforms and combined into a single `xcframework`
for each library. These may then be included in iOS, watchOS, visionOS, tvOS, and macOS applications [using Xcode](https://github.com/zwill22/blogs/blob/main/linking.md#adding-xcframeworks-to-xcode).

## Pre-requisites

In order to run the code there are a number of non-Python projects which must be installed:

- [CMake](https://cmake.org/cmake/help/latest/) (minimum tested version 3.22)
- [XCode](https://developer.apple.com/xcode/) (command line tools)
- [Apple SDKs](https://developer.apple.com/support/xcode/) for each of the specified targets
- [Python](https://docs.python.org/3/) (versions 3.9-3.13 supported)

Optional Dependencies:

- [Pytest](https://docs.pytest.org/en/stable/) (for testing)
- [Sphinx](https://www.sphinx-doc.org/en/master/) (for building documentation)

Since the project requires XCode and the SDK for each target platform, the project only works for macOS.

## Getting started

This repository includes a simple example `CMake` project for testing the build system.

To build using `pip` from this repo:

```
pip install iosbuild
pip -m ios_build -v example
```

This builds the example project using sensible defaults for iOS (ARM64), iOS Simulator (ARM64),
and macOS (ARM64). This configuration builds the files in a subdirectory `build` of the current
directory, downloads the `ios.toolchain.cmake` file to the current directory and installs the libraries
and the `xcframework` to `install`.
If successful, this outputs a file `libiosbuildexample.xcframeworks` in the `install/` directory.

<!-- Badges -->

[macos-badge]: https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=F0F0F0&style=for-the-badge
[python-badge]: https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge
[github-badge]: https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white&style=for-the-badge
[uv-badge]: https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white
[pytest-badge]: https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3
[license-badge]: https://img.shields.io/github/license/zwill22/iosbuild?style=for-the-badge
[github-actions-badge]: https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white&style=for-the-badge
[ci-badge]: https://img.shields.io/github/actions/workflow/status/zwill22/iosbuild/ci.yml?style=for-the-badge&logo=github
[issues-badge]: https://img.shields.io/github/issues/zwill22/iosbuild?style=for-the-badge&logo=github
[rtd-badge]: https://img.shields.io/badge/Read%20the%20Docs-8CA1AF?logo=readthedocs&logoColor=fff&labelColor=333&style=for-the-badge
[doc-badge]: https://img.shields.io/readthedocs/iosbuild?style=for-the-badge
[codecov-badge]: https://img.shields.io/badge/Codecov-F01F7A?logo=codecov&logoColor=fff&style=for-the-badge
[coverage-badge]: https://img.shields.io/codecov/c/github/zwill22/iosbuild?style=for-the-badge&logo=codecov
[buy-me-a-coffee-badge]: https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?&logo=buy-me-a-coffee&logoColor=black&style=for-the-badge
[noai-badge]: https://custom-icon-badges.demolab.com/badge/No%20AI-2f2f2f?logo=non-ai&logoColor=white&style=for-the-badge

<!-- Links -->

[macos]: https://www.apple.com/macos/
[python]: https://www.python.org
[github]: https://github.com/zwill22/iOSBuild
[license]: https://github.com/zwill22/iosbuild/blob/main/LICENSE
[github-actions]: https://github.com/zwill22/iosbuild/actions
[ci-build]: https://github.com/zwill22/iOSBuild/actions/workflows/ci.yml
[rtd]: https://about.readthedocs.com/
[doc]: https://iosbuild.readthedocs.io/en/latest
[codecov]: https://about.codecov.io/
[coverage]: https://app.codecov.io/gh/zwill22/iOSBuild
[buy-me-a-coffee]: https://coff.ee/zmwill
[uv]: https://docs.astral.sh/uv/
[pytest]: https://docs.pytest.org/
