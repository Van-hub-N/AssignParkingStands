cmake_minimum_required(VERSION 3.16)

project(AirportGateScheduling
        VERSION 1.0.0
        DESCRIPTION "Stopping gate scheduling: case generation, greedy, backtracking and branch-and-bound strategies"
        LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY  ${CMAKE_BINARY_DIR}/lib)

# 核心库：案例读写、贪心算法、公共校验函数
add_library(airport_core STATIC
    src/io.cpp
    src/greedy.cpp
    src/backtracking.cpp
    src/branch_bound.cpp
    src/utils.cpp
)

target_include_directories(airport_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(airport_core PUBLIC cxx_std_17)

if(MSVC)
  target_compile_options(airport_core PRIVATE /W4 /permissive-)
else()
  target_compile_options(airport_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# 命令行工具
add_executable(generate_cases tools/generate_cases.cpp)
target_link_libraries(generate_cases PRIVATE airport_core)

add_executable(dump_case tools/dump_case.cpp)
target_link_libraries(dump_case PRIVATE airport_core)

add_executable(validate_all tools/validate_all.cpp)
target_link_libraries(validate_all PRIVATE airport_core)

add_executable(benchmark tools/benchmark.cpp)
target_link_libraries(benchmark PRIVATE airport_core)

add_executable(backtrack_benchmark tools/backtracking_benchmark.cpp)
target_link_libraries(backtrack_benchmark PRIVATE airport_core)

add_executable(branch_bound_benchmark tools/branch_bound_benchmark.cpp)
target_link_libraries(branch_bound_benchmark PRIVATE airport_core)

add_executable(solve_case tools/solve_case.cpp)
target_link_libraries(solve_case PRIVATE airport_core)

# 让从构建目录直接运行时也能通过相对路径 data/cases 找到案例。
# 提交包可能只带 data/sample_cases，此时不创建指向不存在目录的软链接。
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/data/cases)
  add_custom_target(prepare_data ALL
      COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/data
      COMMAND ${CMAKE_COMMAND} -E create_symlink
              ${CMAKE_CURRENT_SOURCE_DIR}/data/cases
              ${CMAKE_BINARY_DIR}/data/cases
      COMMENT "为构建目录创建 data/cases 软链接"
  )
else()
  add_custom_target(prepare_data ALL
      COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/data
      COMMENT "未找到 data/cases，跳过软链接"
  )
endif()
add_dependencies(generate_cases prepare_data)
add_dependencies(dump_case      prepare_data)
add_dependencies(validate_all   prepare_data)
add_dependencies(benchmark      prepare_data)
add_dependencies(backtrack_benchmark prepare_data)
add_dependencies(branch_bound_benchmark prepare_data)
add_dependencies(solve_case      prepare_data)

enable_testing()
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/data/cases/case_00000.bin)
  add_test(NAME validate_first_100
           COMMAND validate_all --start 0 --count 100
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/cases)
  add_test(NAME benchmark_first_10
           COMMAND benchmark --start 0 --count 10
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/cases
                   --out ${CMAKE_BINARY_DIR}/smoke_benchmark.csv)
  add_test(NAME backtracking_small
           COMMAND backtrack_benchmark --start 200 --count 10 --max-k 6
                   --time-limit-ms 1000 --node-limit 1000000
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/cases
                   --out ${CMAKE_BINARY_DIR}/smoke_backtracking.csv)
  add_test(NAME branch_bound_small
           COMMAND branch_bound_benchmark --start 200 --count 10 --max-k 6
                   --time-limit-ms 1000 --node-limit 1000000
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/cases
                   --out ${CMAKE_BINARY_DIR}/smoke_branch_bound.csv)
elseif(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/data/sample_cases/case_00000.bin)
  # 提交包不带完整数据集时，用样例案例做冒烟测试。
  add_test(NAME validate_sample
           COMMAND validate_all --start 0 --count 1
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/sample_cases)
  add_test(NAME benchmark_sample
           COMMAND benchmark --start 7000 --count 1
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/sample_cases
                   --out ${CMAKE_BINARY_DIR}/smoke_benchmark.csv)
  add_test(NAME backtracking_sample
           COMMAND backtrack_benchmark --start 2500 --count 1 --max-k 10
                   --time-limit-ms 1000 --node-limit 1000000
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/sample_cases
                   --out ${CMAKE_BINARY_DIR}/smoke_backtracking.csv)
  add_test(NAME branch_bound_sample
           COMMAND branch_bound_benchmark --start 2500 --count 1 --max-k 10
                   --time-limit-ms 1000 --node-limit 1000000
                   --data-dir ${CMAKE_CURRENT_SOURCE_DIR}/data/sample_cases
                   --out ${CMAKE_BINARY_DIR}/smoke_branch_bound.csv)
else()
  message(STATUS "未找到 data/cases 或样例案例，跳过 CTest 数据集测试")
endif()
