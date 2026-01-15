#pragma once

#include <pqxx/pqxx>
#include <string>
#include <vector>

struct CourseLine {
    int id;
    std::string name;
    std::string description;
};
struct CourseInfo {
    std::string name;
    std::string description;
    int instructor_id;
};
struct TestLine {
    std::string name;
    int id;
};

class ResourceCourse
{
private:
    pqxx::connection& conn;
public:
    ResourceCourse(pqxx::connection& conn);
    std::vector<CourseLine> get_all();
    CourseInfo get_info(int course_id);
    bool update_info(int course_id, const std::string& name, const std::string& description);
    std::vector<TestLine> get_tests(int course_id);
    bool is_test_active(int course_id, int test_id);
    bool set_test_active(int course_id, int test_id, bool active);
    int add_test(int course_id, const std::string& test_name);
    bool remove_test(int course_id, int test_id);
    std::vector<int> get_students(int course_id);
    void add_user(int user_id, int course_id);
    bool remove_user(int user_id, int course_id);
    int create_course(const std::string& name, const std::string& description, int instructor_id);
    bool delete_course(int course_id);
};

