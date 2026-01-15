#include "Api_resAttempt.h"

Api_resAttempt::Api_resAttempt(ResourceAttempt& resAttempt, PermissionChecker& permChecker) : resAttempt(resAttempt), permChecker(permChecker) {};


void Api_resAttempt::create_attempt(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    nlohmann::json json_body;
    try {
        json_body = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!json_body.contains("user_id") || !json_body.contains("test_id")) {
        res.status = 400; return;
    }
    int user_id = json_body["user_id"].get<int>();
    int test_id = json_body["test_id"].get<int>();
    if (p_info.status==403 && (!resAttempt.user_has_test(user_id, test_id))){
        res.status = p_info.status; return;
    }
    int attempt_id = resAttempt.create_attempt(user_id, test_id);
	if (attempt_id = -1) {res.status=403; return;}
    nlohmann::json json_response;
    json_response["attempt_id"] = attempt_id;
    res.set_content(json_response.dump(), "application/json");
}

void Api_resAttempt::update_answer(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    nlohmann::json json_body;
    try {
        json_body = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!json_body.contains("answer_id") || !json_body.contains("answer_option")) {
        res.status = 400; return;
    }
    int attempt_id = std::stoi(req.matches[1]);
    if (p_info.status==403 && resAttempt.get_user(attempt_id)!=p_info.user_id){
        res.status = p_info.status; return;
    }
    int answer_id = json_body["answer_id"].get<int>();
    int answer_option = json_body["answer_option"].get<int>();
    if(!resAttempt.update_answer(attempt_id, answer_id, answer_option)) res.status = 404;
}

void Api_resAttempt::finish_attempt(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int attempt_id = std::stoi(req.matches[1]);
    if (p_info.status==403 && resAttempt.get_user(attempt_id)!=p_info.user_id){
        res.status = p_info.status; return;
    }
	try{
    resAttempt.finish_attempt(attempt_id);
	} catch(...) {res.status = 404;}
}

void Api_resAttempt::get_info(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "test:answer:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
	int user_id = std::stoi(req.get_param_value("user_id"));
    int test_id = std::stoi(req.get_param_value("test_id"));
	try{
    AttemptInfo info = resAttempt.get_info(user_id, test_id);
    if (p_info.status==403 && p_info.user_id!=user_id && p_info.user_id!=info.instructor_id){
        res.status = p_info.status; return;
    }
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
	} catch(...){res.status = 404;}
}


