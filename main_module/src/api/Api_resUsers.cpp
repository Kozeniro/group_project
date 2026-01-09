#include "Api_resUsers.h"

Api_resUsers::Api_resUsers(ResourceUsers& resUsers) : resUsers(resUsers) {};

void Api_resUsers::get_all(const httplib::Request& req, httplib::Response& res) {
	auto users = resUsers.get_all();
	nlohmann::json j = nlohmann::json::array();
	for (const auto& user : users) {
		j.push_back({ {"id",user.id},{"name",user.full_name} });
	}
	res.set_content(j.dump(), "application/json");
}

void Api_resUsers::get_name(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.matches[1]);
	std::string full_name = resUsers.get_name(user_id);
	res.set_content(full_name, "text/plain");
}

void Api_resUsers::update_name(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.matches[1]);
	auto new_name = req.get_param_value("new_name");
	resUsers.update_name(user_id, new_name);
}

void Api_resUsers::get_info(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.matches[1]);
	auto info_type_str = req.get_param_value("info_type");
	Info info_type;

	if (info_type_str == "courses") { info_type = Courses; }
	else if (info_type_str == "scores") { info_type = Scores; }
	else if (info_type_str == "tests") { info_type = Tests; }
	else {}

	std::vector<std::string> info_list = resUsers.get_info(user_id, info_type);

	nlohmann::json j;
	if (info_type == Scores) {
		std::vector<int> vec_scores;
		for (const auto& score : info_list) vec_scores.push_back(stoi(score));
		j = vec_scores;
	}
	else j = info_list;

	res.set_content(j.dump(), "application/json");
}

void Api_resUsers::get_roles(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.matches[1]);
	auto roles = resUsers.get_roles(user_id);
	nlohmann::json j = roles;
	res.set_content(j, "application/json");
}

void Api_resUsers::set_roles(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.matches[1]);
	auto json_roles = nlohmann::json::parse(req.get_param_value("roles"));
	std::vector<std::string> new_roles = json_roles.get<std::vector<std::string>>();
	resUsers.set_roles(user_id, new_roles);
}

void Api_resUsers::check_user_blocked(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.matches[1]);
	bool blocked = resUsers.is_blocked(user_id);
	res.set_content(blocked ? "true" : "false", "text/plain");
}

void Api_resUsers::set_user_blocked(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.matches[1]);
	bool blocked = (req.get_param_value("blocked") == "true");
	resUsers.set_blocked(user_id, blocked);
}