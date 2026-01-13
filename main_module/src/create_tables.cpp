#include "create_tables.h"

void create_tables(pqxx::connection& conn){
	std::vector<std::string> tables {"users", "roles", "users_roles", "courses", "courses_users", "tests", "questions", "tests_questions", "attempts", "answers"};
	pqxx::work txn(conn);
	for (const auto& t : tables){
		pqxx::result exists = txn.exec_params("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = $1)", t);
		std::string query = "";
		if (!exists[0][0].as<bool>()){
			if (t=="users")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						full_name VARCHAR(255) NOT NULL,\
						is_blocked BOOLEAN NOT NULL DEFAULT FALSE\
					);";
			else if (t=="roles")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						name VARCHAR(50) NOT NULL\
					);";
			else if (t=="users_roles")
				query = "\
					CREATE TABLE "+t+" (\
						user_id INTEGER NOT NULL REFERENCES users(id),\
						role_id INTEGER NOT NULL REFERENCES roles(id),\
						PRIMARY KEY (user_id, role_id)\
					);";
			else if (t=="courses")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						name VARCHAR(255) NOT NULL,\
						description TEXT,\
						instructor_id INTEGER REFERENCES users(id),\
						is_exists BOOLEAN NOT NULL DEFAULT TRUE\
					);";
			else if (t=="courses_users")
				query = "\
					CREATE TABLE "+t+" (\
						course_id INTEGER NOT NULL REFERENCES courses(id),\
						user_id INTEGER NOT NULL REFERENCES users(id),\
						PRIMARY KEY (course_id, user_id)\
					);";
			else if (t=="tests")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						course_id INTEGER NOT NULL REFERENCES courses(id),\
						name VARCHAR(255) NOT NULL,\
						is_active BOOLEAN NOT NULL DEFAULT FALSE,\
						is_exists BOOLEAN NOT NULL DEFAULT TRUE\
					);";
			else if (t=="questions")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						local_id INTEGER NOT NULL,\
						version INTEGER NOT NULL,\
						name VARCHAR(255),\
						text TEXT,\
						options JSONB,\
						correct_option INTEGER,\
						author_id INTEGER REFERENCES users(id),\
						is_exists BOOLEAN NOT NULL DEFAULT TRUE\
					);";
			else if (t=="tests_questions")
				query = "\
					CREATE TABLE "+t+" (\
						test_id INTEGER NOT NULL REFERENCES tests(id),\
						question_id INTEGER NOT NULL REFERENCES questions(id),\
						PRIMARY KEY (test_id, question_id),\
						position INTEGER NOT NULL\
					);";
			else if (t=="attempts")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						user_id INTEGER NOT NULL REFERENCES users(id),\
						test_id INTEGER NOT NULL REFERENCES tests(id),\
						status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'completed')),\
						score INTEGER NOT NULL\
					);";
			else if (t=="answers")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						attempt_id INTEGER NOT NULL REFERENCES attempts(id),\
						question_id INTEGER NOT NULL REFERENCES questions(id),\
						question_version INTEGER NOT NULL,\
						answer_option INTEGER NOT NULL DEFAULT -1\
					);";
		}
		if (query!="") txn.exec(query);
	}
	txn.commit();
}