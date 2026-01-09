#include "ResourceQuestions.h"

ResourceQuestions::ResourceQuestions(pqxx::connection& conn) : conn(conn) {}

// 1.Посмотреть список вопросов 
std::vector<QuestionLine> ResourceQuestions::get_all() {
    std::vector<QuestionLine> questions;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec(
        "SELECT DISTINCT ON (local_id) name, version, author_id FROM questions WHERE is_exists = TRUE \
        ORDER BY local_id, version DESC;"
    );
    for (const auto& row : res) {
        questions.push_back({ row["name"].as<std::string>(), row["version"].as<int>(), row["author_id"].as<int>() });
    }
    return questions;
}

// 2.Посмотреть информацию о вопросе
QuestionInfo ResourceQuestions::get_info(int question_id, int version) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT name, text, options, correct_option FROM questions \
        WHERE id = $1 AND version = $2 AND is_exists = TRUE",
        question_id, version
    );
    return {
        res[0]["name"].as<std::string>(),
        res[0]["text"].as<std::string>(),
        nlohmann::json::parse(res[0]["options"].as<std::string>()),
        res[0]["correct_option"].as<int>()
    };
}

// 3.Редактировать вопрос
void ResourceQuestions::update_question(int question_id, const std::string& name, const std::string& text, const nlohmann::json& options, int correct_option, int author_id) {
    pqxx::work txn(conn);
    txn.exec_params(
        "INSERT INTO questions (local_id, version, name, text, options, correct_option, author_id, is_exists) \
        VALUES ($1, (SELECT MAX(version)+1 FROM questions WHERE local_id = $1), $2, $3, $4, $5, $6, TRUE)",
        question_id, name, text, options.dump(), correct_option, author_id
    );
    txn.commit();
}

// 4.Создать вопрос
int ResourceQuestions::create_question(const std::string& name, const std::string& text, const nlohmann::json& options, int correct_option, int author_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "INSERT INTO questions (local_id, version, name, text, options, correct_option, author_id, is_exists) \
        VALUES ((SELECT MAX(local_id) FROM questions), 1, $1, $2, $3, $4, $5, TRUE) RETURNING id",
        name, text, options.dump(), correct_option, author_id
    );
    txn.commit();
    return res[0]["id"].as<int>();
}

// 5.Удалить вопрос
void ResourceQuestions::delete_question(int question_id) {
    pqxx::work txn(conn);
    // Проверка на наличие в тестах
    pqxx::result is_in_tests = txn.exec_params(
        "SELECT EXISTS (SELECT 1 FROM tests_questions WHERE question_id = $1)",
        question_id
    );
    if (!(is_in_tests[0][0].as<bool>())) {
        txn.exec_params(
            "UPDATE questions SET is_exists = FALSE WHERE id = $1",
            question_id
        );
    }
    txn.commit();
}
