# iOSBuild

[![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=F0F0F0)](https://www.apple.com/macos/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org)
[![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white)](https://github.com/zwill22/iOSBuild/blob/main/LICENSE)
[![License: MIT](https://img.shields.io/github/license/zwill22/iosbuild)](https://github.com/zwill22/iosbuild)
[![CI Build](https://github.com/zwill22/iOSBuild/actions/workflows/python-package.yml/badge.svg)](https://github.com/zwill22/iOSBuild/actions/workflows/python-package.yml)
[![Read the Docs](https://img.shields.io/badge/Read%20the%20Docs-8CA1AF?logo=readthedocs&logoColor=fff&labelColor=333)](https://iosbuild.readthedocs.io/en/latest)
[![Documentation Status](https://readthedocs.org/projects/iosbuild/badge/?version=latest)](https://iosbuild.readthedocs.io/en/latest/?badge=latest)
[![Coverage](https://codecov.io/gh/zwill22/iOSBuild/graph/badge.svg?token=IIGY2L49XB)](https://codecov.io/gh/zwill22/iOSBuild)


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
