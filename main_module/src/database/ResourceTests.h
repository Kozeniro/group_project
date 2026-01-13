#pragma once

#include "json.hpp"
#include <pqxx/pqxx>
#include <vector>
#include <string>

struct ScoresUsers {
	int score;
	int user_id;
};

struct q_a {
	std::string question_text;
	std::string answer_text;
};
struct UserAnswers {
	int user_id;
	std::vector<q_a> answers;
};

class ResourceTests {
private:
	pqxx::connection& conn;
public:
	ResourceTests(pqxx::connection& conn);
	int get_instructor(int test_id);
	int get_author(int question_id);
	void remove_question(int test_id, int question_id);
	void add_question(int test_id, int question_id);
	void set_question_order(int test_id, const std::vector<int>& question_ids);
	std::vector<int> get_users_completed(int test_id);
	std::vector<ScoresUsers> get_users_scores(int test_id);
	std::vector<UserAnswers> get_users_answers(int test_id);
};

