#include "ResourceUsers.h"

ResourceUsers::ResourceUsers(pqxx::connection& conn):conn(conn) {};
// 0. Создать пользователя
int ResourceUsers::create(const std::string& name) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "INSERT INTO users (full_name) VALUES ($1) RETURNING id",
        name
    );
    txn.commit();
    return res[0]["id"].as<int>();
}

// 1. Посмотреть список пользователей
std::vector<UserLine> ResourceUsers::get_all() {
    std::vector<UserLine> users;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec("SELECT id, full_name FROM users");
    for (const auto& row : res) {
        users.push_back({ row["id"].as<int>(), row["full_name"].as<std::string>() });
    }
    return users;
}

// 2. Посмотреть информацию о пользователе (ФИО)
std::string ResourceUsers::get_name(int user_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params("SELECT full_name FROM users WHERE id = $1", user_id);
    return res[0]["full_name"].as<std::string>();
}

// 3. Изменить ФИО пользователя
void ResourceUsers::update_name(int user_id, const std::string& new_name) {
    pqxx::work txn(conn);
    txn.exec_params("UPDATE users SET full_name = $1 WHERE id = $2", new_name, user_id);
    txn.commit();
}

// 4. Посмотреть информацию о пользователе (курсы, оценки, тесты)
std::vector<std::string> ResourceUsers::get_info(int user_id, Info info_type) {
    std::vector<std::string> info;

    pqxx::work txn(conn);

    switch (info_type) {
        case Courses:
        {
            pqxx::result res_courses = txn.exec_params("SELECT c.name FROM courses c \
            JOIN courses_users cu ON c.id = cu.course_id WHERE cu.user_id = $1",
                user_id
            );
            for (const auto& row : res_courses) {
                info.push_back(row["name"].as<std::string>());
            }
            break;
        }
        case Scores:
        {
            pqxx::result res_tests = txn.exec_params("SELECT t.name FROM tests t \
                JOIN attempts a ON t.id = a.test_id WHERE a.user_id = $1",
                user_id
            );
            for (const auto& row : res_tests) {
                info.push_back(row["name"].as<std::string>());
            }
            break;
        }
        case Tests:
        {
            pqxx::result res_scores = txn.exec_params("SELECT score FROM attempts WHERE user_id = $1",
                user_id
            );
            for (const auto& row : res_scores) {
                info.push_back(row["score"].as<std::string>());
            }
            break;
        }
    }
    return info;
}

// 5. Посмотреть роли пользователя
std::vector<std::string> ResourceUsers::get_roles(int user_id) {
    std::vector<std::string> roles;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params("SELECT r.name FROM roles r \
        JOIN users_roles ur ON r.id = ur.role_id WHERE ur.user_id = $1",
        user_id
    );
    for (const auto& row : res) {
        roles.push_back(row["name"].as<std::string>());
    }
    return roles;
}

// 6. Изменить роли пользователя
void ResourceUsers::set_roles(int user_id, const std::vector<std::string>& new_roles) {
    pqxx::work txn(conn);

    txn.exec_params("DELETE FROM users_roles WHERE user_id = $1", user_id);
    for (const auto& role_name : new_roles) {
        pqxx::result res_role = txn.exec_params("SELECT id FROM roles WHERE name = $1", role_name);
        int role_id = res_role[0]["id"].as<int>();
        txn.exec_params("INSERT INTO users_roles (user_id, role_id) VALUES ($1, $2)", user_id, role_id);
    }

    txn.commit();
}

// 7. Проверить, заблокирован ли пользователь
bool ResourceUsers::is_blocked(int user_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params("SELECT is_blocked FROM users WHERE id = $1", user_id);
    return res[0]["is_blocked"].as<bool>();
}

// 8. Заблокировать/разблокировать пользователя
void ResourceUsers::set_blocked(int user_id, bool blocked) {
    pqxx::work txn(conn);
    txn.exec_params("UPDATE users SET is_blocked = $1 WHERE id = $2", blocked, user_id);
    txn.commit();
}
