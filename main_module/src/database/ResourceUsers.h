#pragma once

#include <pqxx/pqxx>
#include <vector>
#include <string>

struct UserLine {
    int id;
    std::string full_name;
};

enum Info {
    Courses,
    Scores,
    Tests
};

class ResourceUsers
{
private:
    pqxx::connection& conn;
public:
    ResourceUsers(pqxx::connection& conn);
    int get_user_id(std::string auth_id);
    std::vector<UserLine> get_all();
    std::string get_name(int user_id);
    void update_name(int user_id, const std::string& new_name);
    std::vector<std::string> get_info(int user_id, Info info_type);
    std::vector<std::string> get_roles(int user_id);
    void set_roles(int user_id, const std::vector<std::string>& new_roles);
    bool is_blocked(int user_id);
    void set_blocked(int user_id, bool blocked);
};

