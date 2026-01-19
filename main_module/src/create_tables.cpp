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
						auth_id VARCHAR(255) NOT NULL, \
						full_name VARCHAR(255),\
						notifications JSONB DEFAULT '[]',\
						is_blocked BOOLEAN NOT NULL DEFAULT FALSE\
					);";
			else if (t=="roles")
				query = "\
					CREATE TABLE "+t+" (\
						id SERIAL PRIMARY KEY,\
						name VARCHAR(50) NOT NULL\
					);\
					INSERT INTO roles (name) VALUES ('student'),('teacher'),('admin');\
					";
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
						question_id INTEGER NOT NULL,\
						PRIMARY KEY (test_id, question_id),\
						position INTEGER NOT NULL\
					);" + 
					R"(DROP TRIGGER IF EXISTS trg_check_question_local_id ON tests_questions;
					CREATE OR REPLACE FUNCTION check_question_local_id() RETURNS TRIGGER AS $$
					BEGIN
						IF NOT EXISTS (SELECT 1 FROM questions WHERE local_id = NEW.question_id) THEN
							RAISE EXCEPTION 'Question with local_id % does not exist', NEW.question_id;
						END IF; RETURN NEW;
					END;
					$$ LANGUAGE plpgsql;
					CREATE TRIGGER trg_check_question_local_id
					BEFORE INSERT ON tests_questions
					FOR EACH ROW EXECUTE FUNCTION check_question_local_id();)";
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
						question_id INTEGER NOT NULL,\
						question_version INTEGER NOT NULL,\
						answer_option INTEGER NOT NULL DEFAULT -1\
					);";
		}
		if (query!="") txn.exec(query);
	}
	txn.commit();
}