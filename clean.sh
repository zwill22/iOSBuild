#/bin/bash

rm -Rf install
rm -Rf run
rm -Rf iOSBuild.egg-info
rm -Rf .venv
rm -Rf .ruff_cache
rm -Rf .pytest_cache
rm -Rf uv.lock
rm ios.toolchain.cmake
rm -Rf tests/__pycache__
rm -Rf ios_build/__pycache__
rm -Rf build/