#include "Api_resAttempt.h"

Api_resAttempt::Api_resAttempt(ResourceAttempt& resAttempt) : resAttempt(resAttempt) {};


void Api_resAttempt::create_attempt(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.get_param_value("user_id"));
	int test_id = std::stoi(req.get_param_value("test_id"));
	int attempt_id = resAttempt.create_attempt(user_id, test_id);
	res.set_content(std::to_string(attempt_id), "text/plain");
}

void Api_resAttempt::update_answer(const httplib::Request& req, httplib::Response& res) {
	int attempt_id = std::stoi(req.matches[1]);
	int answer_id = std::stoi(req.get_param_value("answer_id"));
	int answer_option = std::stoi(req.get_param_value("answer_option"));
	resAttempt.update_answer(attempt_id, answer_id, answer_option);
}

void Api_resAttempt::finish_attempt(const httplib::Request& req, httplib::Response& res) {
	int attempt_id = std::stoi(req.matches[1]);
	resAttempt.finish_attempt(attempt_id);
}

void Api_resAttempt::get_info(const httplib::Request& req, httplib::Response& res) {
	int user_id = std::stoi(req.get_param_value("user_id"));
	int test_id = std::stoi(req.get_param_value("test_id"));
	AttemptInfo info = resAttempt.get_info(user_id, test_id);
	nlohmann::json json_res;
	json_res["status"] = info.status;
	json_res["answers"] = nlohmann::json::array();
	for (const auto& ans : info.answers) {
		json_res["answers"].push_back({
			{"question_id", ans.question_id},
			{"question_version", ans.question_ver},
			{"answer_option", ans.option}
			});
	}
	res.set_content(json_res.dump(), "application/json");
}


