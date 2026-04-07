cmake_minimum_required(VERSION 3.20)
project(claude_agent_tools CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler warnings
if(MSVC)
  add_compile_options(/W4)
else()
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

add_library(agent_tools SHARED tools.cpp)
target_include_directories(agent_tools PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Tests
enable_testing()
add_executable(tools_test tools_test.cpp)
target_link_libraries(tools_test agent_tools)
add_test(NAME tools_test COMMAND tools_test)
