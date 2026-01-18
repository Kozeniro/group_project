#include "Api_resAnswers.h"

Api_resAnswers::Api_resAnswers(ResourceAnswers& resAnswers, PermissionChecker& permChecker) : resAnswers(resAnswers), permChecker(permChecker) {};

void Api_resAnswers::create_answer(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "system");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }
    nlohmann::json json_body;
    try {
        json_body = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!json_body.contains("attempt_id") || !json_body.contains("question_id")) {
        res.status = 400; return;
    }
    int attempt_id = json_body["attempt_id"].get<int>();
    int question_id = json_body["question_id"].get<int>();
	try{
    resAnswers.create_answer(attempt_id, question_id);
	}catch(...){res.status = 404;}
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
    try{
    AnswerLine answer = resAnswers.get_answer(answer_id);
    nlohmann::json json_res = {
        {"question_id", answer.question_id},
        {"question_version", answer.question_ver},
        {"answer_option", answer.option}
    };
    res.set_content(json_res.dump(), "application/json");
	} catch(...){res.status = 404;}
}

void Api_resAnswers::update_answer(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "answer:update");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    nlohmann::json json_body;
    try {
        json_body = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!json_body.contains("answer_option")) {
        res.status = 400; return;
    }
    int answer_id = std::stoi(req.matches[1]);
    int answer_option = json_body["answer_option"].get<int>();
    if (p_info.status==403 && resAnswers.get_user(answer_id)!=p_info.user_id){
        res.status = p_info.status; return;
    }
	try{resAnswers.update_answer(answer_id, answer_option);}
	catch (...) {res.status = 403;}
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
    try{resAnswers.delete_answer(answer_id);}
	catch (...) {res.status = 403;}
}
