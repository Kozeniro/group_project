#pragma once

#include <pqxx/pqxx>
#include <string>

struct AnswerLine {
    int question_id;
    int question_ver;
    int option;
};

class ResourceAnswers
{
private:
    pqxx::connection& conn;
public:
    ResourceAnswers(pqxx::connection& connection);
    int get_user(int answer_id);
    int get_instructor(int answer_id);
    void create_answer(int attempt_id, int question_id);
    AnswerLine get_answer(int answer_id);
    void update_answer(int answer_id, int new_option);
    void delete_answer(int answer_id);
};