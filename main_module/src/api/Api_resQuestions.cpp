#include "Api_resQuestions.h"

Api_resQuestions::Api_resQuestions(ResourceQuestions& resQuestions, PermissionChecker& permChecker) : resQuestions(resQuestions), permChecker(permChecker) {};

void Api_resQuestions::get_all(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "quest:list:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    auto questions = resQuestions.get_all();
    nlohmann::json json_res = nlohmann::json::array();
    for (const auto& q : questions) {
        if (p_info.status==200 || p_info.user_id == q.author_id){
            json_res.push_back(
                { {"id",q.id},{"name", q.name},{"version", q.version},{"author_id", q.author_id} }
            );
        }
    }
    res.set_content(json_res.dump(), "application/json");
}

void Api_resQuestions::get_info(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "quest:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int question_id = std::stoi(req.matches[1]);
    int version = std::stoi(req.get_param_value("version"));
	try{
    QuestionInfo info = resQuestions.get_info(question_id, version);
    if (p_info.status==403 && 
        (info.author_id != p_info.user_id && (!resQuestions.check_presence(question_id, p_info.user_id)))){
        res.status = p_info.status; return;
    }

    nlohmann::json json_res = {
        {"name", info.name},
        {"text", info.text},
        {"options", info.options},
        {"correct_option", info.correct_option}
    };
    res.set_content(json_res.dump(), "application/json");
	}catch(...){res.status = 404;}
}

void Api_resQuestions::update_question(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "quest:update");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int question_id = std::stoi(req.matches[1]);
    QuestionInfo info = resQuestions.get_info(question_id, 1);
    int author_id = info.author_id;
    if (p_info.status==403 && author_id != p_info.user_id){
        res.status = p_info.status; return;
    }

    nlohmann::json json_body;
    try {
        json_body = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!json_body.contains("name") || !json_body.contains("text") || !json_body.contains("options") || !json_body.contains("correct_option")) {
        res.status = 400; return;
    }
    std::string name = json_body["name"].get<std::string>();
    std::string text = json_body["text"].get<std::string>();
    nlohmann::json options = json_body["options"];
    int correct_option = json_body["correct_option"].get<int>();
	try{
    resQuestions.update_question(question_id, name, text, options, correct_option, author_id);
	}catch(...){res.status = 404;}
}


void Api_resQuestions::create_question(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "quest:create");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }
    nlohmann::json json_body;
    try {
        json_body = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    if (!json_body.contains("name") || !json_body.contains("text") || !json_body.contains("options") || !json_body.contains("correct_option")) {
        res.status = 400; return;
    }
    int author_id = p_info.user_id;
    std::string name = json_body["name"].get<std::string>();
    std::string text = json_body["text"].get<std::string>();
    nlohmann::json options = json_body["options"];
    int correct_option = json_body["correct_option"].get<int>();
    int new_question_id = resQuestions.create_question(name, text, options, correct_option, author_id);
	if (new_question_id ==-1) {res.status = 404; return;}
    res.set_content(std::to_string(new_question_id), "text/plain");
}

void Api_resQuestions::delete_question(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "quest:del");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    int question_id = std::stoi(req.matches[1]);
    QuestionInfo info = resQuestions.get_info(question_id, 1);
    if (p_info.status==403 && info.author_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    if(!resQuestions.delete_question(question_id)) res.status = 403;
}