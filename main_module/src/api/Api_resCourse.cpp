#include "Api_resCourse.h"


Api_resCourse::Api_resCourse(ResourceCourse& resCourse, PermissionChecker& permChecker) : resCourse(resCourse), permChecker(permChecker) {};

void Api_resCourse::get_all(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    
    auto courses = resCourse.get_all();
    nlohmann::json json_res = nlohmann::json::array();
    for (const auto& course : courses) {
        json_res.push_back(
            { {"id", course.id},{"name", course.name},{"description", course.description} }
        );
    }
    res.set_content(json_res.dump(), "application/json");
}

void Api_resCourse::get_info(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    
    int course_id = std::stoi(req.matches[1]);
	try{
    auto info = resCourse.get_info(course_id);
    nlohmann::json json_res = { {"name", info.name},{"description", info.description},{"instructor_id", info.instructor_id} };
    res.set_content(json_res.dump(), "application/json");
	} catch(...) {res.status = 404;}
}

void Api_resCourse::update_info(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:info:write");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    if (p_info.status==403 && info.instructor_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    
    if (!body_json.contains("name") || !body_json.contains("description")) {
        res.status = 400; return;
    }
    
    std::string name = body_json["name"].get<std::string>();
    std::string description = body_json["description"].get<std::string>();
    if(!resCourse.update_info(course_id, name, description)) res.status = 404;
}

void Api_resCourse::get_tests(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:testList");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    auto students = resCourse.get_students(course_id);
    if (p_info.status==403 && 
        (info.instructor_id != p_info.user_id && std::find(students.begin(),students.end(),p_info.user_id)==students.end())){
        res.status = p_info.status; return;
    }
    
    auto tests = resCourse.get_tests(course_id);
    nlohmann::json json_res = nlohmann::json::array();
    for (const auto& test : tests) {
        json_res.push_back({ {"name", test.name},{"id", test.id} });
    }
    res.set_content(json_res.dump(), "application/json");
}

void Api_resCourse::is_test_active(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:test:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    auto students = resCourse.get_students(course_id);
    if (p_info.status==403 && 
        (info.instructor_id != p_info.user_id && std::find(students.begin(),students.end(),p_info.user_id)==students.end())){
        res.status = p_info.status; return;
    }

    int test_id = std::stoi(req.matches[2]);
	try{
    bool is_active = resCourse.is_test_active(course_id, test_id);
    nlohmann::json json_response;
    json_response["activity"] = is_active;
    res.set_content(json_response.dump(), "application/json");
	}catch(...){res.status = 404;}
}

void Api_resCourse::set_test_active(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:test:write");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    if (p_info.status==403 && info.instructor_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!body_json.contains("activity")) {
        res.status = 400; return;
    }
    
    bool active = body_json["activity"].get<bool>();
    int test_id = std::stoi(req.matches[2]);
    if(!resCourse.set_test_active(course_id, test_id, active)) res.status = 404;
}

void Api_resCourse::add_test(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:test:add");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    if (p_info.status==403 && info.instructor_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!body_json.contains("test_name")) {
        res.status = 400; return;
    }
    
    std::string test_name = body_json["test_name"].get<std::string>();
    int new_test_id = resCourse.add_test(course_id, test_name);
	if (new_test_id = -1) {res.status = 404; return;}
    nlohmann::json json_response;
    json_response["test_id"] = new_test_id;
    res.set_content(json_response.dump(), "application/json");
}

void Api_resCourse::remove_test(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:test:del");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    if (p_info.status==403 && info.instructor_id != p_info.user_id){
        res.status = p_info.status; return;
    }

    int test_id = std::stoi(req.matches[2]);
    resCourse.remove_test(course_id, test_id);
}

void Api_resCourse::get_students(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:userList");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    if (p_info.status==403 && info.instructor_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    
    auto students = resCourse.get_students(course_id);
    nlohmann::json json_res = students;
    res.set_content(json_res.dump(), "application/json");
}


void Api_resCourse::add_user(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:user:add");
    int course_id = std::stoi(req.matches[1]);
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!body_json.contains("user_id")) {
        res.status = 400; return;
    }
    int user_id = body_json["user_id"].get<int>();
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    if (p_info.status==403 && user_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    resCourse.add_user(user_id, course_id);
}


void Api_resCourse::remove_user(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:user:del");
    int course_id = std::stoi(req.matches[1]);
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!body_json.contains("user_id")) {
        res.status = 400; return;
    }
    int user_id = body_json["user_id"].get<int>();
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    if (p_info.status==403 && user_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    if(!resCourse.remove_user(user_id, course_id)) res.status = 404;
}


void Api_resCourse::create_course(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:add");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!body_json.contains("name") || !body_json.contains("description") || !body_json.contains("instructor_id")) {
        res.status = 400; return;
    }
    std::string name = body_json["name"].get<std::string>();
    std::string description = body_json["description"].get<std::string>();
    int instructor_id = body_json["instructor_id"].get<int>();
    int course_id = resCourse.create_course(name, description, instructor_id);
    nlohmann::json json_response;
    json_response["course_id"] = course_id;
    res.set_content(json_response.dump(), "application/json");
}

void Api_resCourse::delete_course(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "course:del");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int course_id = std::stoi(req.matches[1]);
    auto info = resCourse.get_info(course_id);
    if (p_info.status==403 && info.instructor_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    if(!resCourse.delete_course(course_id)) res.status = 404;
}
