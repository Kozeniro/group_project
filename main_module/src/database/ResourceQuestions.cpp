#include "ResourceQuestions.h"

ResourceQuestions::ResourceQuestions(pqxx::connection& conn) : conn(conn) {}

// 0.Проверить наличие вопроса у пользователя
bool ResourceQuestions::check_presence(int question_id, int user_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params("SELECT EXISTS (SELECT 1 FROM attempts a \
        JOIN tests_questions tq ON a.test_id = tq.test_id WHERE a.user_id = $1 AND tq.question_id = $2);",
        user_id, question_id
    );
    return res[0][0].as<bool>();
}

// 1.Посмотреть список вопросов 
std::vector<QuestionLine> ResourceQuestions::get_all() {
    std::vector<QuestionLine> questions;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec(
        "SELECT DISTINCT ON (local_id) local_id, name, version, author_id FROM questions WHERE is_exists = TRUE \
        ORDER BY local_id, version DESC;"
    );
    for (const auto& row : res) {
        questions.push_back({ row["local_id"].as<int>(), row["name"].as<std::string>(), row["version"].as<int>(), row["author_id"].as<int>() });
    }
    return questions;
}

// 2.Посмотреть информацию о вопросе
QuestionInfo ResourceQuestions::get_info(int question_id, int version) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT name, text, options, correct_option, author_id FROM questions \
        WHERE local_id = $1 AND version = $2 AND is_exists = TRUE",
        question_id, version
    );
	if (res.empty()) throw std::runtime_error("No question");
    return {
        res[0]["name"].as<std::string>(),
        res[0]["text"].as<std::string>(),
        nlohmann::json::parse(res[0]["options"].as<std::string>()),
        res[0]["correct_option"].as<int>(),

        res[0]["author_id"].as<int>() //system
    };
}

// 3.Редактировать вопрос
void ResourceQuestions::update_question(int question_id, const std::string& name, const std::string& text, const nlohmann::json& options, int correct_option, int author_id) {
    pqxx::work txn(conn);
	pqxx::result exists = txn.exec_params("SELECT EXISTS (SELECT 1 FROM questions WHERE local_id = $1)",question_id);
	if (exists[0][0].as<bool>()){
		txn.exec_params(
			"INSERT INTO questions (local_id, version, name, text, options, correct_option, author_id, is_exists) \
			VALUES ($1, (SELECT MAX(version)+1 FROM questions WHERE local_id = $1), $2, $3, $4, $5, $6, TRUE)",
			question_id, name, text, options.dump(), correct_option, author_id
		);
		txn.commit();
	}
	else throw std::runtime_error("No question");
}

// 4.Создать вопрос
int ResourceQuestions::create_question(const std::string& name, const std::string& text, const nlohmann::json& options, int correct_option, int author_id) {
    pqxx::work txn(conn);
	try{
    pqxx::result res = txn.exec_params(
        "INSERT INTO questions (local_id, version, name, text, options, correct_option, author_id, is_exists) \
        VALUES ((SELECT COALESCE(MAX(local_id),0)+1 FROM questions), 1, $1, $2, $3, $4, $5, TRUE) RETURNING local_id",
        name, text, options.dump(), correct_option, author_id
    );
    txn.commit();
    return res[0]["local_id"].as<int>();
	} catch(...) {return -1;}
}

// 5.Удалить вопрос
bool ResourceQuestions::delete_question(int question_id) {
    pqxx::work txn(conn);
    pqxx::result is_in_tests = txn.exec_params(
        "SELECT EXISTS (SELECT 1 FROM tests_questions WHERE question_id = $1)",
        question_id
    );
    if (!(is_in_tests[0][0].as<bool>())) {
        auto res = txn.exec_params(
            "UPDATE questions SET is_exists = FALSE WHERE local_id = $1",
            question_id
        );
		if (res.affected_rows() == 0) return false;
    }
	else return false;
	txn.commit();
	return true;
}
