cmake_minimum_required(VERSION 3.20)
project(COMP51915)
set(CMAKE_CXX_STANDARD 11)

# set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
# aux_source_directory(${PROJECT_SOURCE_DIR}/src SRC_LIST)

add_executable(
    COMP51915
    gs.cpp
)


# # Locate GoogleTest
# find_package(GTest REQUIRED)
# include_directories(${GTEST_INCLUDE_DIRS})

# # Link GoogleTest to my test executable
# target_link_libraries(COMP51915 ${GTEST_LIBRARIES} pthread)
