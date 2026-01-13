#include "Api_resAnswers.h"

Api_resAnswers::Api_resAnswers(ResourceAnswers& resAnswers, PermissionChecker& permChecker) : resAnswers(resAnswers), permChecker(permChecker) {};

void Api_resAnswers::create_answer(const httplib::Request& req, httplib::Response& res) {
	PermissionInfo p_info = permChecker.check(req, "system");
	if (p_info.status != 200) {
		res.status = p_info.status; return;
	}
	int attempt_id = std::stoi(req.get_param_value("attempt_id"));
	int question_id = std::stoi(req.get_param_value("question_id"));
	resAnswers.create_answer(attempt_id, question_id);
}

void Api_resAnswers::get_answer(const httplib::Request& req, httplib::Response& res) {
	PermissionInfo p_info = permChecker.check(req, "answer:read");
	if (p_info.status==401 || p_info.status==418) {
		res.status = p_info.status; return;
	}
	int answer_id = std::stoi(req.matches[1]);
	if (p_info.status==403 && resAnswers.get_user(answer_id)!=p_info.user_id && resAnswers.get_instructor(answer_id)!=p_info.user_id){
		res.status = p_info.status; return;
	}
	
	AnswerLine answer = resAnswers.get_answer(answer_id);
	nlohmann::json json_res = {
		{"question_id", answer.question_id},
		{"question_version", answer.question_ver},
		{"answer_option", answer.option}
	};
	res.set_content(json_res.dump(), "application/json");
}

void Api_resAnswers::update_answer(const httplib::Request& req, httplib::Response& res) {
	PermissionInfo p_info = permChecker.check(req, "answer:update");
	if (p_info.status==401 || p_info.status==418) {
		res.status = p_info.status; return;
	}
	int answer_id = std::stoi(req.matches[1]);
	if (p_info.status==403 && resAnswers.get_user(answer_id)!=p_info.user_id){
		res.status = p_info.status; return;
	}
	int new_option = std::stoi(req.get_param_value("answer_option"));
	resAnswers.update_answer(answer_id, new_option);
}

void Api_resAnswers::delete_answer(const httplib::Request& req, httplib::Response& res) {
	PermissionInfo p_info = permChecker.check(req, "answer:del");
	if (p_info.status==401 || p_info.status==418) {
		res.status = p_info.status; return;
	}
	int answer_id = std::stoi(req.matches[1]);
	if (p_info.status==403 && resAnswers.get_user(answer_id)!=p_info.user_id){
		res.status = p_info.status; return;
	}
	resAnswers.delete_answer(answer_id);
}
