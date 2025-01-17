# Required for Github runner
cmake_minimum_required(VERSION 3.22)
project(IOSBuildExampleProject LANGUAGES C)

set(CMAKE_C_STANDARD 17)

message(STATUS "CMAKE VERSION: ${CMAKE_VERSION}")
message(STATUS "CMAKE_SOURCE_DIR: ${CMAKE_SOURCE_DIR}")
message(STATUS "CMAKE_BINARY_DIR: ${CMAKE_BINARY_DIR}")

add_library(ExampleLibrary)
target_include_directories(ExampleLibrary PUBLIC ${CMAKE_SOURCE_DIR}/include)

add_subdirectory(src)
