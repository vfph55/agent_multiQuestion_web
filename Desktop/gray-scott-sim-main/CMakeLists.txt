cmake_minimum_required(VERSION 3.14)

# set project name
project(gray-scott-sim)

# set cpp standard
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


enable_testing()

add_subdirectory(src)
add_subdirectory(test)