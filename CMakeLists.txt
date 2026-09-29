cmake_minimum_required(VERSION 3.20)
project(STONEBOTTRY LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(STONEBOTTRY
    src/main.cpp
    src/Core/Logger.cpp
)

target_include_directories(STONEBOTTRY PRIVATE include)

if (WIN32)
    target_compile_definitions(STONEBOTTRY PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
endif()
