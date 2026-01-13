#include <iostream>
#include <pqxx/pqxx>
#include "httplib.h"
#include "register_routes.hpp"
#include "PermissionChecker.h"
#include "create_tables.h"

#include <cstdlib> // for getenv
int main()
{
    

	const char* host = std::getenv("POSTGRES_HOST");
	const char* port = std::getenv("POSTGRES_PORT");
	const char* dbname = std::getenv("POSTGRES_DB");
	const char* user = std::getenv("POSTGRES_USER");
	const char* password = std::getenv("POSTGRES_PASSWORD");


	std::string connection_str = "host=" + std::string(host) +
								 " port=" + std::string(port) +
								 " dbname=" + std::string(dbname) +
								 " user=" + std::string(user) +
								 " password=" + std::string(password);


	pqxx::connection conn(connection_str);
	create_tables(conn);
	
    ResourceUsers resUsers(conn); ResourceCourse resCourse(conn); ResourceQuestions resQuestions(conn); 
    ResourceTests resTests(conn); ResourceAnswers resAnswers(conn); ResourceAttempt resAttempt(conn, resAnswers);
    PermissionChecker permChecker(resUsers);

    Api_resUsers api_users(resUsers, permChecker); Api_resCourse api_course(resCourse, permChecker); Api_resQuestions api_questions(resQuestions, permChecker);
    Api_resTests api_tests(resTests, permChecker); Api_resAnswers api_answers(resAnswers, permChecker); Api_resAttempt api_attempt(resAttempt, permChecker);

    httplib::Server svr;
    register_routes(svr, api_users, api_course, api_questions, api_tests, api_answers, api_attempt);
    
    svr.listen("0.0.0.0", 8080);
}