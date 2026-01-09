#pragma once

#include <pqxx/pqxx>
#include <vector>
#include <string>
#include "ResourceAnswers.h"

struct AttemptInfo {
    std::string status;
    std::vector<AnswerLine> answers;
};

class ResourceAttempt {
private:
    pqxx::connection& conn;
    ResourceAnswers& resource_answers;
public:
    ResourceAttempt(pqxx::connection& conn, ResourceAnswers& resource_answers);
    int create(int user_id, int test_id);
    void update_answer(int attempt_id, int answer_id, int answer_option);
    void finish(int attempt_id);
    AttemptInfo get_info(int user_id, int test_id);
};