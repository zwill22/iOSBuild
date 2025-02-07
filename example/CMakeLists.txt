# Required for Github runner
cmake_minimum_required(VERSION 3.22)
project(IOSBuildExampleProject LANGUAGES C)

set(CMAKE_C_STANDARD 17)

message(STATUS "CMAKE VERSION: ${CMAKE_VERSION}")
message(STATUS "CMAKE_SOURCE_DIR: ${CMAKE_SOURCE_DIR}")
message(STATUS "CMAKE_BINARY_DIR: ${CMAKE_BINARY_DIR}")
message(STATUS "CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")

add_library(iosbuildexample)
target_include_directories(iosbuildexample PUBLIC ${CMAKE_SOURCE_DIR}/include)

add_subdirectory(src)

install(
    FILES ${CMAKE_SOURCE_DIR}/include/library.h
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)
install(
    TARGETS iosbuildexample
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)
