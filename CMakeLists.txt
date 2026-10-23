cmake_minimum_required(VERSION 3.16)

project(AirportGateScheduling
        VERSION 1.0.0
        DESCRIPTION "Stopping gate scheduling: greedy/backtracking/B&B/heuristic"
        LANGUAGES CXX)

# ---- 全局编译选项 ----
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# 统一输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY  ${CMAKE_BINARY_DIR}/lib)

# ---- 核心库：src/ 下全部实现，无 main ----
add_library(airport_core STATIC
    src/io.cpp
    src/greedy.cpp
    src/backtracking.cpp
    src/branch_bound.cpp
    src/heuristic.cpp
)

target_include_directories(airport_core
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(airport_core PUBLIC cxx_std_17)

if(MSVC)
  target_compile_options(airport_core PRIVATE /W4 /permissive-)
else()
  target_compile_options(airport_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# ---- 可执行文件：tools/ 下每个 cpp 一个目标 ----
add_executable(generate_cases tools/generate_cases.cpp)
target_link_libraries(generate_cases PRIVATE airport_core)

add_executable(dump_case tools/dump_case.cpp)
target_link_libraries(dump_case PRIVATE airport_core)

add_executable(validate_all tools/validate_all.cpp)
target_link_libraries(validate_all PRIVATE airport_core)

# ---- 让运行目录下有 data/ ----
# 程序里用相对路径 "data/..."，相对于进程工作目录。
# 这里把源码树的 data/ 结构准备到构建目录，保证 cd build && ./bin/xxx 可直接运行。

add_custom_target(prepare_data ALL
    COMMAND ${CMAKE_COMMAND} -E make_directory
            ${CMAKE_BINARY_DIR}/data/cases
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${CMAKE_CURRENT_SOURCE_DIR}/data/combos.csv
            ${CMAKE_BINARY_DIR}/data/combos.csv
    COMMENT "准备构建目录下的 data/"
)

# 只让需要读 data/ 的目标依赖它；generate_cases 也写 data/cases/，所以同样依赖
add_dependencies(generate_cases prepare_data)
add_dependencies(dump_case      prepare_data)
add_dependencies(validate_all   prepare_data)

# ---- 可选：测试 ----
enable_testing()
# add_test(NAME smoke COMMAND validate_all WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
