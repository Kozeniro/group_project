#include "ResourceAnswers.h"

ResourceAnswers::ResourceAnswers(pqxx::connection& connection) : conn(connection) {}

// 1. Создать ответ
void ResourceAnswers::create_answer(int attempt_id, int question_id) {
    pqxx::work txn(conn);
    txn.exec_params(
        "INSERT INTO answers (attempt_id, question_id, question_version, answer_option) \
        VALUES ($1, $2,(SELECT MAX(version) FROM questions WHERE id = $2), -1)",
        attempt_id, question_id
    );
    txn.commit();
}

// 2. Посмотреть ответ (ID вопроса выбранный вариант)
AnswerLine ResourceAnswers::get_answer(int answer_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT question_id, question_version, answer_option FROM answers WHERE id = $1",
        answer_id
    );
    return { res[0]["question_id"].as<int>(), res[0]["question_version"].as<int>(), res[0]["answer_option"].as<int>() };
}

// 3. Изменить ответ
void ResourceAnswers::update_answer(int answer_id, int new_option) {
    pqxx::work txn(conn);
    pqxx::result att_status = txn.exec_params(
        "SELECT att.status FROM answers ans JOIN attempts att ON att.id=ans.attempt_id WHERE ans.id = $1",
        answer_id
    );
    if (att_status[0][0].as<std::string>() == "active")
    {
        txn.exec_params(
            "UPDATE answers SET answer_option = $1 WHERE id = $2",
            new_option, answer_id
        );
        txn.commit();
    }
}

// 4. Удалить ответ (answer_option = -1)
void ResourceAnswers::delete_answer(int answer_id) {
    pqxx::work txn(conn);
    pqxx::result att_status = txn.exec_params(
        "SELECT att.status FROM answers ans JOIN attempts att ON att.id=ans.attempt_id WHERE ans.id = $1",
        answer_id
    );
    if (att_status[0][0].as<std::string>() == "active")
    {
        txn.exec_params(
            "UPDATE answers SET answer_option = -1 WHERE id = $1",
            answer_id
        );
    }
    txn.commit();
}
