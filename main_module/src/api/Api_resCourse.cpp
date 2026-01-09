#include "Api_resCourse.h"


Api_resCourse::Api_resCourse(ResourceCourse& resCourse) : resCourse(resCourse) {};

void Api_resCourse::get_all(const httplib::Request& req, httplib::Response& res) {
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
	int course_id = std::stoi(req.matches[1]);
	auto info = resCourse.get_info(course_id);
	nlohmann::json json_res = { {"name", info.name},{"description", info.description},{"instructor_id", info.instructor_id} };
	res.set_content(json_res.dump(), "application/json");
}

void Api_resCourse::update_info(const httplib::Request& req, httplib::Response& res) {
	int id = std::stoi(req.matches[1]);
	std::string name = req.get_param_value("name");
	std::string description = req.get_param_value("description");
	resCourse.update_info(id, name, description);
}

void Api_resCourse::get_tests(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	auto tests = resCourse.get_tests(course_id);
	nlohmann::json json_res = nlohmann::json::array();
	for (const auto& test : tests) {
		json_res.push_back({ {"name", test.name},{"id", test.id} });
	}
	res.set_content(json_res.dump(), "application/json");
}

void Api_resCourse::is_test_active(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	int test_id = std::stoi(req.matches[2]);
	bool is_active = resCourse.is_test_active(course_id, test_id);
	res.set_content(is_active ? "true" : "false", "text/plain");
}

void Api_resCourse::set_test_active(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	int test_id = std::stoi(req.matches[2]);
	bool active = req.get_param_value("active") == "true";
	resCourse.set_test_active(course_id, test_id, active);
}

void Api_resCourse::add_test(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	std::string test_name = req.get_param_value("test_name");
	int new_test_id = resCourse.add_test(course_id, test_name);
	res.set_content(std::to_string(new_test_id), "text/plain");
}

void Api_resCourse::remove_test(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	int test_id = std::stoi(req.matches[2]);
	resCourse.remove_test(course_id, test_id);
}

void Api_resCourse::get_students(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	auto students = resCourse.get_students(course_id);
	nlohmann::json json_res = students;
	res.set_content(json_res.dump(), "application/json");
}


void Api_resCourse::add_user(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	int user_id = std::stoi(req.get_param_value("user_id"));
	resCourse.add_user(user_id, course_id);
}


void Api_resCourse::remove_user(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	int user_id = std::stoi(req.get_param_value("user_id"));
	resCourse.remove_user(user_id, course_id);
}


void Api_resCourse::create_course(const httplib::Request& req, httplib::Response& res) {
	std::string name = req.get_param_value("name");
	std::string description = req.get_param_value("description");
	int instructor_id = std::stoi(req.get_param_value("instructor_id"));
	int course_id = resCourse.create_course(name, description, instructor_id);
	res.set_content(std::to_string(course_id), "text/plain");
}

void Api_resCourse::delete_course(const httplib::Request& req, httplib::Response& res) {
	int course_id = std::stoi(req.matches[1]);
	resCourse.delete_course(course_id);
}
