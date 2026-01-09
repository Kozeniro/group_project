#include "Api_resTests.h"

Api_resTests::Api_resTests(ResourceTests& resTests) : resTests(resTests) {};


void Api_resTests::remove_question(const httplib::Request& req, httplib::Response& res) {
	int test_id = std::stoi(req.matches[1]);
	int question_id = std::stoi(req.matches[2]);
	resTests.remove_question(test_id, question_id);
}

void Api_resTests::add_question(const httplib::Request& req, httplib::Response& res) {
	int test_id = std::stoi(req.matches[1]);
	int question_id = std::stoi(req.get_param_value("question_id"));
	resTests.add_question(test_id, question_id);
}

void Api_resTests::set_question_order(const httplib::Request& req, httplib::Response& res) {
	int test_id = std::stoi(req.matches[1]);
	nlohmann::json json_ids = nlohmann::json::parse(req.get_param_value("question_ids"));
	std::vector<int> question_ids = json_ids.get<std::vector<int>>();
	resTests.set_question_order(test_id, question_ids);
}

void Api_resTests::get_users_completed(const httplib::Request& req, httplib::Response& res) {
	int test_id = std::stoi(req.matches[1]);
	auto user_ids = resTests.get_users_completed(test_id);
	nlohmann::json json_res = user_ids;
	res.set_content(json_res.dump(), "application/json");
}

void Api_resTests::get_users_scores(const httplib::Request& req, httplib::Response& res) {
	int test_id = std::stoi(req.matches[1]);
	auto scores = resTests.get_users_scores(test_id);
	nlohmann::json json_res = nlohmann::json::array();
	for (const auto& s : scores) {
		json_res.push_back({ {"user_id", s.user_id}, {"score", s.score} });
	}
	res.set_content(json_res.dump(), "application/json");
}

void Api_resTests::get_users_answers(const httplib::Request& req, httplib::Response& res) {
	int test_id = std::stoi(req.matches[1]);
	auto users_answers = resTests.get_users_answers(test_id);
	nlohmann::json json_res = nlohmann::json::array();
	for (const auto& user_answer : users_answers) {
		nlohmann::json user_json;
		user_json["user_id"] = user_answer.user_id;
		nlohmann::json answers_json = nlohmann::json::array();
		for (const auto& qa : user_answer.answers) {
			answers_json.push_back(
				{ {"question_text", qa.question_text},{"answer_text", qa.answer_text} }
			);
		}
		user_json["answers"] = answers_json;
		json_res.push_back(user_json);
	}
	res.set_content(json_res.dump(), "application/json");
}
