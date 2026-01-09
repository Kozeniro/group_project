cmake_minimum_required(VERSION 3.10)
project(main_module)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


find_package(PkgConfig REQUIRED)
pkg_check_modules(PQXX REQUIRED libpqxx)
find_package(PostgreSQL REQUIRED)

add_executable(main_module main.cpp)

target_include_directories(main_module PRIVATE ${PQXX_INCLUDE_DIRS} ${PostgreSQL_INCLUDE_DIRS})
target_link_libraries(main_module PRIVATE ${PQXX_LIBRARIES} PostgreSQL::PostgreSQL)
target_compile_options(main_module PRIVATE ${PQXX_CFLAGS_OTHER})