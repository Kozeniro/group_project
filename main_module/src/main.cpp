#include <iostream>
#include <pqxx/pqxx>
#include "httplib.h"
#include <register_routes.h>

int main()
{
    std::string connection_string = "postgres://bf39575214c9189fa70701554b75ce7dd71cc18accecae236c76748378e000a8:sk_keRvGx-d9MLa5h3yNF3Pk@db.prisma.io:5432/postgres?sslmode=require";
    pqxx::connection conn(connection_string);

    ResourceUsers resUsers(conn); ResourceCourse resCourse(conn); ResourceQuestions resQuestions(conn); 
    ResourceTests resTests(conn); ResourceAnswers resAnswers(conn); ResourceAttempt resAttempt(conn, resAnswers);

    Api_resUsers api_users(resUsers); Api_resCourse api_course(resCourse); Api_resQuestions api_questions(resQuestions);
    Api_resTests api_tests(resTests); Api_resAnswers api_answers(resAnswers); Api_resAttempt api_attempt(resAttempt);

    httplib::Server svr;
    register_routes(svr, api_users, api_course, api_questions, api_tests, api_answers, api_attempt);
    
    svr.listen("0.0.0.0", 8080);
}