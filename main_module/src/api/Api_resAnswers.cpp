#include "Api_resAnswers.h"

Api_resAnswers::Api_resAnswers(ResourceAnswers& resAnswers) : resAnswers(resAnswers) {};

void Api_resAnswers::create_answer(const httplib::Request& req, httplib::Response& res) {
	int attempt_id = std::stoi(req.get_param_value("attempt_id"));
	int question_id = std::stoi(req.get_param_value("question_id"));
	resAnswers.create_answer(attempt_id, question_id);
}

void Api_resAnswers::get_answer(const httplib::Request& req, httplib::Response& res) {
	int answer_id = std::stoi(req.matches[1]);
	AnswerLine answer = resAnswers.get_answer(answer_id);
	nlohmann::json json_res = {
		{"question_id", answer.question_id},
		{"question_version", answer.question_ver},
		{"answer_option", answer.option}
	};
	res.set_content(json_res.dump(), "application/json");
}

void Api_resAnswers::update_answer(const httplib::Request& req, httplib::Response& res) {
	int answer_id = std::stoi(req.matches[1]);
	int new_option = std::stoi(req.get_param_value("answer_option"));
	resAnswers.update_answer(answer_id, new_option);
}

void Api_resAnswers::delete_answer(const httplib::Request& req, httplib::Response& res) {
	int answer_id = std::stoi(req.matches[1]);
	resAnswers.delete_answer(answer_id);
}
