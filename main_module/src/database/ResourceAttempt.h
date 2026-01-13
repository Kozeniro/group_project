#pragma once

#include <pqxx/pqxx>
#include <vector>
#include <string>
#include "ResourceAnswers.h"

struct AttemptInfo {
    std::string status;
    std::vector<AnswerLine> answers;

    int instructor_id; //system
};

class ResourceAttempt {
private:
    pqxx::connection& conn;
    ResourceAnswers& resource_answers;
public:
    ResourceAttempt(pqxx::connection& conn, ResourceAnswers& resource_answers);
    bool user_has_test(int user_id, int test_id);
    int get_user(int attempt_id);
    int create_attempt(int user_id, int test_id);
    void update_answer(int attempt_id, int answer_id, int answer_option);
    void finish_attempt(int attempt_id);
    AttemptInfo get_info(int user_id, int test_id);
};