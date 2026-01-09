#include "ResourceAttempt.h"

ResourceAttempt::ResourceAttempt(pqxx::connection& conn, ResourceAnswers& resource_answers) : conn(conn), resource_answers(resource_answers) {}

// 1.Создать попытку
int ResourceAttempt::create(int user_id, int test_id) {
    int attempt_id = -1;
    pqxx::work txn(conn);
    pqxx::result attempt_exists = txn.exec_params(
        "SELECT EXISTS (SELECT 1 FROM attempts WHERE user_id = $1 AND test_id = $2)",
        user_id, test_id
    );
    if (!attempt_exists[0][0].as<bool>()) {
        pqxx::result test_active = txn.exec_params(
            "SELECT is_active FROM tests WHERE id = $1", test_id
        );
        if (test_active[0][0].as<bool>()) {

            pqxx::result res = txn.exec_params(
                "INSERT INTO attempts (user_id, test_id, status, score) VALUES ($1, $2, 'active', 0) RETURNING id",
                user_id, test_id
            );
            attempt_id = res[0]["id"].as<int>();

            pqxx::result test_quests = txn.exec_params(
                "SELECT question_id FROM tests_questions WHERE test_id = $1", test_id
            );
            for (const auto& question : test_quests) {
                resource_answers.create_answer(attempt_id, question["question_id"].as<int>());
            }
        }
    }
    return attempt_id;
}

// 2.Изменить попытку (изменение ответа?)
void ResourceAttempt::update_answer(int attempt_id, int answer_id, int answer_option) {
    pqxx::work txn(conn);
    pqxx::result test_att_check = txn.exec_params(
        "SELECT t.is_active, att.status FROM attempts att JOIN tests t ON att.test_id = t.id WHERE att.id = $1",
        attempt_id
    );
    if (test_att_check[0]["status"].as<std::string>() == "active" && test_att_check[0]["is_active"].as<bool>())
    {
        txn.exec_params(
            "UPDATE answers SET answer_option = $1 WHERE id = $2",
            answer_option, answer_id
        );
        txn.commit();
    }

}

// 3.Завершить попытку
void ResourceAttempt::finish(int attempt_id) {

    pqxx::work txn(conn);
    pqxx::result test_att_check = txn.exec_params(
        "SELECT t.is_active, att.status FROM attempts att JOIN tests t ON att.test_id = t.id WHERE att.id = $1",
        attempt_id
    );
    if (test_att_check[0]["status"].as<std::string>() == "active" && test_att_check[0]["is_active"].as<bool>())
    {

        pqxx::result score = txn.exec_params("SELECT COUNT(*) FROM answers a JOIN questions q \
            ON a.question_id = q.id WHERE a.attempt_id = $1  AND a.answer_option = q.correct_option;", 
            attempt_id
        );

        txn.exec_params(
            "UPDATE attempts SET status = 'completed', score = $1 WHERE id = $2",
            score[0][0].as<int>(), attempt_id
        );

        txn.commit();
    }

}

// 4.Посмотреть попытку
AttemptInfo ResourceAttempt::get_info(int user_id, int test_id) {
    pqxx::work txn(conn);
    pqxx::result att_status = txn.exec_params(
        "SELECT status FROM attempts WHERE user_id = $1 AND test_id = $2",
        user_id, test_id
    );

    pqxx::result ans_res = txn.exec_params(
        "SELECT qusetion_id, question_version, answer_option FROM answers ans \
        JOIN attempts att ON ans.attempt_id = att.id WHERE att.user_id = $1 AND att.test_id = $2",
        user_id, test_id
    );

    std::vector<AnswerLine> ans_vec;
    for (const auto& row : ans_res) {
        ans_vec.push_back(AnswerLine{ row["question_id"].as<int>(), row["question_version"].as<int>(), row["answer_option"].as<int>() });
    }

    return { att_status[0][0].as<std::string>(), ans_vec };
}
