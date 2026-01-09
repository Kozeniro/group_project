cmake_minimum_required(VERSION 3.10)
project(main_module)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(PQXX REQUIRED libpqxx)
find_package(PostgreSQL REQUIRED)

add_executable(main_module src/main.cpp

    src/database/ResourceAnswers.cpp
    src/database/ResourceAttempt.cpp
    src/database/ResourceCourse.cpp
    src/database/ResourceQuestions.cpp
    src/database/ResourceTests.cpp
    src/database/ResourceUsers.cpp

    src/api/Api_resAnswers.cpp
    src/api/Api_resAttempt.cpp
    src/api/Api_resCourse.cpp
    src/api/Api_resQuestions.cpp
    src/api/Api_resTests.cpp
    src/api/Api_resUsers.cpp

    src/register_routes.cpp
)

target_include_directories(main_module PRIVATE ./src ./src/database ./src/api)
target_include_directories(main_module PRIVATE ./include)
target_include_directories(main_module PRIVATE ${PQXX_INCLUDE_DIRS} ${PostgreSQL_INCLUDE_DIRS})
target_link_libraries(main_module PRIVATE ${PQXX_LIBRARIES} PostgreSQL::PostgreSQL)
target_compile_options(main_module PRIVATE ${PQXX_CFLAGS_OTHER})