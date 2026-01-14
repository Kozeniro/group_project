#include "ResourceCourse.h"

ResourceCourse::ResourceCourse(pqxx::connection& conn) :conn(conn) {}

// 1.Посмотреть список дисциплин
std::vector<CourseLine> ResourceCourse::get_all() {
    std::vector<CourseLine> courses;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec("SELECT id, name, description FROM courses WHERE is_exists = TRUE");
    for (const auto& row : res) {
        courses.push_back({ row["id"].as<int>(), row["name"].as<std::string>(), row["description"].as<std::string>() });
    }
    return courses;
}

// 2.Посмотреть информацию о дисциплине (название, описание, ID преподавателя)
CourseInfo ResourceCourse::get_info(int course_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT name, description, instructor_id FROM courses WHERE id = $1 AND is_exists = TRUE",
        course_id
    );
	if (res.empty()) return {"","",-1};
	std::string description = (!res[0]["description"].is_null() ? res[0]["description"].as<std::string>() : "");
    return {res[0]["name"].as<std::string>(),description,res[0]["instructor_id"].as<int>()};
}

// 3.Изменить информацию о дисциплине
void ResourceCourse::update_info(int course_id, const std::string& name, const std::string& description) {
    pqxx::work txn(conn);
    txn.exec_params(
        "UPDATE courses SET name = $1, description = $2 WHERE id = $3 AND is_exists = TRUE",
        name, description, course_id
    );
    txn.commit();
}

// 4.Посмотреть тесты дисциплины
std::vector<TestLine> ResourceCourse::get_tests(int course_id) {
    std::vector<TestLine> tests;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT name, id FROM tests WHERE course_id = $1 AND is_exists = TRUE",
        course_id
    );
    for (const auto& row : res) {
        tests.push_back({ row["name"].as<std::string>(),row["id"].as<int>() });
    }
    return tests;
}

// 5.Посмотреть активность теста
bool ResourceCourse::is_test_active(int course_id, int test_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT is_active FROM tests WHERE id = $1 AND course_id = $2 AND is_exists = TRUE",
        test_id, course_id
    );
	if (!res.empty()) return res[0]["is_active"].as<bool>();
    return false;
}

// 6.Активировать/Деактивировать тест
void ResourceCourse::set_test_active(int course_id, int test_id, bool active) {
    pqxx::work txn(conn);
    txn.exec_params(
        "UPDATE tests SET is_active = $1 WHERE id = $2 AND course_id = $3",
        active, test_id, course_id
    );
    if (!active) {
        txn.exec_params(
            "UPDATE attempts SET status = 'completed' WHERE test_id = $1 AND status = 'active'",
            test_id
        );
    }
    txn.commit();
}

// 7.Добавить тест в дисциплину
int ResourceCourse::add_test(int course_id, const std::string& test_name) {
    pqxx::work txn(conn);
	try{
    pqxx::result res = txn.exec_params(
        "INSERT INTO tests (course_id, name, is_active, is_exists) VALUES ($1, $2, FALSE, TRUE) RETURNING id",
        course_id, test_name
    );
    txn.commit();
	return res[0]["id"].as<int>();
	}
	catch(...) {return -1;}
    
}

// 8.Удалить тест из дисциплины 
void ResourceCourse::remove_test(int course_id, int test_id) {
    pqxx::work txn(conn);
    txn.exec_params(
        "UPDATE tests SET is_exists = FALSE WHERE id = $1 AND course_id = $2",
        test_id, course_id
    );
    txn.commit();
}

// 9.Посмотреть список студентов дисциплины
std::vector<int> ResourceCourse::get_students(int course_id) {
    std::vector<int> students;
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "SELECT user_id FROM courses_users WHERE course_id = $1",
        course_id
    );
    for (const auto& row : res) {
        students.push_back(row["user_id"].as<int>());
    }
    return students;
}

// 10.Записать пользователя на дисциплину
void ResourceCourse::add_user(int user_id, int course_id) {
    pqxx::work txn(conn);
    txn.exec_params(
        "INSERT INTO courses_users (course_id, user_id) VALUES ($1, $2)",
        course_id, user_id
    );
    txn.commit();
}

// 11.Отчислить пользователя с дисциплины
void ResourceCourse::remove_user(int user_id, int course_id) {
    pqxx::work txn(conn);
    txn.exec_params(
        "DELETE FROM courses_users WHERE course_id = $1 AND user_id = $2",
        course_id, user_id
    );
    txn.commit();
}

// 12.Создать дисциплину
int ResourceCourse::create_course(const std::string& name, const std::string& description, int instructor_id) {
    pqxx::work txn(conn);
    pqxx::result res = txn.exec_params(
        "INSERT INTO courses (name, description, instructor_id, is_exists) VALUES ($1, $2, $3, TRUE) RETURNING id",
        name, description, instructor_id
    );
    txn.commit();
    return res[0]["id"].as<int>();
}

// 13.Удалить дисциплину
void ResourceCourse::delete_course(int course_id) {
    pqxx::work txn(conn);
    txn.exec_params("UPDATE courses SET is_exists = FALSE WHERE id = $1", course_id);
    txn.commit();
}
