#pragma once

#include "json.hpp"
#include <pqxx/pqxx>
#include <string>
#include <vector>

struct QuestionLine {
    std::string name;
    int version;
    int author_id;
};

struct QuestionInfo {
    std::string name;
    std::string text;
    nlohmann::json options;
    int correct_option;

    int author_id; //system
};

class ResourceQuestions {
private:
    pqxx::connection& conn;
public:
    ResourceQuestions(pqxx::connection& conn);
    bool check_presence(int question_id, int user_id);
    std::vector<QuestionLine> get_all();
    QuestionInfo get_info(int question_id, int version);
    void update_question(int question_id, const std::string& name, const std::string& text, const nlohmann::json& options, int correct_option, int author_id);
    int create_question(const std::string& name, const std::string& text, const nlohmann::json& options, int correct_option, int author_id);
    void delete_question(int question_id);
};

