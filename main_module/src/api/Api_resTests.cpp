#include "Api_resTests.h"

Api_resTests::Api_resTests(ResourceTests& resTests, PermissionChecker& permChecker) : resTests(resTests), permChecker(permChecker) {};


void Api_resTests::remove_question(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "test:quest:del");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int test_id = std::stoi(req.matches[1]);
    if (p_info.status==403 && resTests.get_instructor(test_id) != p_info.user_id){
        res.status = p_info.status; return;
    }
    int question_id = std::stoi(req.matches[2]);
    if(!resTests.remove_question(test_id, question_id))res.status = 403;
}

void Api_resTests::add_question(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "test:quest:add");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int test_id = std::stoi(req.matches[1]);
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!body_json.contains("question_id")) {
        res.status = 400; return;
    }
    int question_id = body_json["question_id"].get<int>();
    if (p_info.status==403 && resTests.get_instructor(test_id) != p_info.user_id && resTests.get_author(question_id)!=p_info.user_id){
        res.status = p_info.status; return;
    }
    if(!resTests.add_question(test_id, question_id))res.status = 403;
}

void Api_resTests::set_question_order(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "test:quest:update");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int test_id = std::stoi(req.matches[1]);
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!body_json.contains("question_ids")) {
        res.status = 400; return;
    }
    std::vector<int> question_ids = body_json["question_ids"].get<std::vector<int>>();
    if (p_info.status==403 && resTests.get_instructor(test_id) != p_info.user_id){
        res.status = p_info.status; return;
    }
    if(!resTests.set_question_order(test_id, question_ids))res.status = 403;
}

void Api_resTests::get_users_completed(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "test:answer:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int test_id = std::stoi(req.matches[1]);
    if (p_info.status==403 && resTests.get_instructor(test_id) != p_info.user_id){
        res.status = p_info.status; return;
    }
    auto user_ids = resTests.get_users_completed(test_id);
    nlohmann::json json_res = user_ids;
    res.set_content(json_res.dump(), "application/json");
}

void Api_resTests::get_users_scores(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "test:answer:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int test_id = std::stoi(req.matches[1]);
    auto scores = resTests.get_users_scores(test_id);
    nlohmann::json json_res = nlohmann::json::array();
    for (const auto& s : scores) {
        if (p_info.status==200 || resTests.get_instructor(test_id) == p_info.user_id || s.user_id == p_info.user_id)
        json_res.push_back({ {"user_id", s.user_id}, {"score", s.score} });
    }
    res.set_content(json_res.dump(), "application/json");
}

void Api_resTests::get_users_answers(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "test:answer:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int test_id = std::stoi(req.matches[1]);
    auto users_answers = resTests.get_users_answers(test_id);
    nlohmann::json json_res = nlohmann::json::array();
    for (const auto& user_answer : users_answers) {
        if (p_info.status==200 || resTests.get_instructor(test_id) == p_info.user_id || user_answer.user_id == p_info.user_id){
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
    }
    res.set_content(json_res.dump(), "application/json");
}
