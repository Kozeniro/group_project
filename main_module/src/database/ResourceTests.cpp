#include "ResourceTests.h"

ResourceTests::ResourceTests(pqxx::connection& conn) :conn(conn) {}

// 0.0. Получить id преподавателя курса с данным тестом
int ResourceTests::get_instructor(int test_id){
    pqxx::work txn(conn);
    pqxx::result instructor_id = txn.exec_params("SELECT c.instructor_id FROM tests t \
        JOIN courses c ON t.course_id = c.id WHERE t.id = $1",
        test_id
    );
    return instructor_id[0][0].as<int>();
}
// 0.0.0. Получить id автора вопроса
int ResourceTests::get_author(int question_id){
    pqxx::work txn(conn);
    pqxx::result author_id = txn.exec_params("SELECT author_id FROM questions WHERE local_id = $1",
        question_id
    );
    return author_id[0][0].as<int>();
}


// 1.Удалить вопрос из теста
void ResourceTests::remove_question(int test_id, int question_id) {
    pqxx::work txn(conn);
    pqxx::result was_attempted = txn.exec_params(
        "SELECT EXISTS (SELECT 1 FROM attempts WHERE test_id = $1)",
        test_id
    );
    if (!was_attempted[0][0].as<bool>()) {
        txn.exec_params(
            "DELETE FROM tests_questions WHERE test_id = $1 AND question_id = $2",
            test_id, question_id
        );
    }
    txn.commit();
}

// 2.Добавить вопрос в тест 
void ResourceTests::add_question(int test_id, int question_id) {
    pqxx::work txn(conn);

    pqxx::result was_attempted = txn.exec_params(
        "SELECT EXISTS (SELECT 1 FROM attempts WHERE test_id = $1)",
        test_id
    );
    if (!was_attempted[0][0].as<bool>()) {
        txn.exec_params(
            "INSERT INTO tests_questions (test_id, question_id, position) VALUES \
        ($1, $2, (SELECT COALESCE(MAX(position), 0)+1 FROM tests_questions WHERE test_id = $1))",
            test_id, question_id
        );
    }

    txn.commit();
}

// 3.Изменить порядок вопросов в тесте
void ResourceTests::set_question_order(int test_id, const std::vector<int>& question_ids) {
    pqxx::work txn(conn);

    pqxx::result was_attempted = txn.exec_params(
        "SELECT EXISTS (SELECT 1 FROM attempts WHERE test_id = $1)",
        test_id
    );
    if (!was_attempted[0][0].as<bool>()){
        int pos = 1;
        for (int q_id : question_ids) {
            txn.exec_params(
                "UPDATE tests_questions SET position = $1 WHERE test_id = $2 AND question_id = $3",
                pos++, test_id, q_id
            );
        }
    }
    txn.commit();
}

// 4.Посмотреть список пользователей, прошедших тест
std::vector<int> ResourceTests::get_users_completed(int test_id) {
    std::vector<int> user_ids;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT user_id FROM attempts WHERE test_id = $1",
        test_id
    );
    for (const auto& row : res) {
        user_ids.push_back(row["user_id"].as<int>());
    }
    return user_ids;
}

// 5.Посмотреть оценку пользователя
std::vector<ScoresUsers> ResourceTests::get_users_scores(int test_id) {
    std::vector<ScoresUsers> results;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT user_id, score FROM attempts WHERE test_id = $1 AND score IS NOT NULL",
        test_id
    );
    for (const auto& row : res) {
        results.push_back({ row["user_id"].as<int>(), row["score"].as<int>() });
    }
    return results;
}

// 6.Посмотреть ответы пользователя
std::vector<UserAnswers> ResourceTests::get_users_answers(int test_id) {
    std::vector<UserAnswers> users_answers;
    pqxx::work txn(conn);
    pqxx::result attempts_res = txn.exec_params(
        "SELECT id, user_id FROM attempts WHERE test_id = $1",
        test_id
    );
    for (const auto& attempt : attempts_res) {
        UserAnswers u_answers;
        u_answers.user_id = attempt["user_id"].as<int>();

        int attempt_id = attempt["id"].as<int>();

        pqxx::result q_a_res = txn.exec_params("SELECT q.text, q.options, answer_option FROM answers \
            JOIN questions q ON question_id = q.local_id AND question_version = q.version WHERE attempt_id = $1",
            attempt_id
        );

        std::vector<q_a> q_a_vec;
        for (const auto& q_a_line : q_a_res) {
            nlohmann::json options = nlohmann::json::parse(q_a_line["options"].as<std::string>());
                int answer_option = q_a_line["answer_option"].as<int>();
                std::string ans_text = "";
                if (answer_option != -1) ans_text = options[answer_option];
                q_a_vec.push_back(q_a{ q_a_line["text"].as<std::string>(), ans_text });

        }
        u_answers.answers = q_a_vec;

        users_answers.push_back(u_answers);
    }
    return users_answers;
}
