#pragma once
#include <httplib.h>

#include "Api_resUsers.h"
#include "Api_resCourse.h"
#include "Api_resQuestions.h"
#include "Api_resTests.h"
#include "Api_resAnswers.h"
#include "Api_resAttempt.h"


void register_routes(httplib::Server& svr, 
	Api_resUsers& api_users, Api_resCourse& api_course, Api_resQuestions& api_questions, 
	Api_resTests& api_tests, Api_resAnswers& api_answers, Api_resAttempt& api_attempt)
{
	//CORS
	svr.set_pre_routing_handler([](const httplib::Request& req, httplib::Response& res) {
    res.set_header("Access-Control-Allow-Origin", "*");
    res.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    res.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization");

    if (req.method == "OPTIONS") {
        res.status = 200;
        return httplib::Server::HandlerResponse::Handled;
    }

    return httplib::Server::HandlerResponse::Unhandled;
});
	//Resource USERS
	svr.Get(R"(/api/user_id)", [&](const httplib::Request& req, httplib::Response& res) {api_users.get_user_id(req, res);});
	svr.Get(R"(/api/auth_id)", [&](const httplib::Request& req, httplib::Response& res) {api_users.get_auth_id(req, res);});
	svr.Get(R"(/notifications)", [&](const httplib::Request& req, httplib::Response& res) {api_users.get_notifications(req, res);});
	svr.Delete(R"(/notifications)", [&](const httplib::Request& req, httplib::Response& res) {api_users.delete_notifications(req, res);});
	svr.Get(R"(/api/users)", [&](const httplib::Request& req, httplib::Response& res) {api_users.get_all(req, res);});
	svr.Get(R"(/api/users/(\d+)/name)", [&](const httplib::Request& req, httplib::Response& res) {api_users.get_name(req, res);});
	svr.Put(R"(/api/users/(\d+)/name)", [&](const httplib::Request& req, httplib::Response& res) {api_users.update_name(req, res);});
	svr.Get(R"(/api/users/(\d+)/info)", [&](const httplib::Request& req, httplib::Response& res) {api_users.get_info(req, res);});
	svr.Get(R"(/api/users/(\d+)/roles)", [&](const httplib::Request& req, httplib::Response& res) {api_users.get_roles(req, res);});
	svr.Post(R"(/api/users/(\d+)/roles)", [&](const httplib::Request& req, httplib::Response& res) {api_users.set_roles(req, res);});
	svr.Get(R"(/api/users/(\d+)/blocked)", [&](const httplib::Request& req, httplib::Response& res) {api_users.check_user_blocked(req, res);});
	svr.Post(R"(/api/users/(\d+)/blocked)", [&](const httplib::Request& req, httplib::Response& res) {api_users.set_user_blocked(req, res);});
	//Resource COURSE
	svr.Get(R"(/api/course)", [&](const httplib::Request& req, httplib::Response& res) {api_course.get_all(req, res);});
	svr.Get(R"(/api/course/(\d+)/info)", [&](const httplib::Request& req, httplib::Response& res) {api_course.get_info(req, res);});
	svr.Put(R"(/api/course/(\d+)/info)", [&](const httplib::Request& req, httplib::Response& res) {api_course.update_info(req, res);});
	svr.Get(R"(/api/course/(\d+)/tests)", [&](const httplib::Request& req, httplib::Response& res) {api_course.get_tests(req, res);});
	svr.Get(R"(/api/course/(\d+)/tests/(\d+)/active)", [&](const httplib::Request& req, httplib::Response& res) {api_course.is_test_active(req, res);});
	svr.Post(R"(/api/course/(\d+)/tests/(\d+)/active)", [&](const httplib::Request& req, httplib::Response& res) {api_course.set_test_active(req, res);});
	svr.Post(R"(/api/course/(\d+)/tests)", [&](const httplib::Request& req, httplib::Response& res) {api_course.add_test(req, res);});
	svr.Delete(R"(/api/course/(\d+)/tests/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_course.remove_test(req, res);});
	svr.Get(R"(/api/course/(\d+)/students)", [&](const httplib::Request& req, httplib::Response& res) {api_course.get_students(req, res);});
	svr.Post(R"(/api/course/(\d+)/students)", [&](const httplib::Request& req, httplib::Response& res) {api_course.add_user(req, res);});
	svr.Delete(R"(/api/course/(\d+)/students)", [&](const httplib::Request& req, httplib::Response& res) {api_course.remove_user(req, res);});
	svr.Post(R"(/api/course)", [&](const httplib::Request& req, httplib::Response& res) {api_course.create_course(req, res);});
	svr.Delete(R"(/api/course/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_course.delete_course(req, res);});
	//Resource QUESTIONS
	svr.Get(R"(/api/questions)", [&](const httplib::Request& req, httplib::Response& res) {api_questions.get_all(req, res);});
	svr.Get(R"(/api/questions/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_questions.get_info(req, res);});
	svr.Put(R"(/api/questions/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_questions.update_question(req, res);});
	svr.Post(R"(/api/questions)", [&](const httplib::Request& req, httplib::Response& res) {api_questions.create_question(req, res);});
	svr.Delete(R"(/api/questions/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_questions.delete_question(req, res);});
	//Resource TESTS
	svr.Get(R"(/api/tests/(\d+)/questions)", [&](const httplib::Request& req, httplib::Response& res) {api_tests.get_questions(req, res);});
	svr.Delete(R"(/api/tests/(\d+)/questions/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_tests.remove_question(req, res);});
	svr.Post(R"(/api/tests/(\d+)/questions)", [&](const httplib::Request& req, httplib::Response& res) {api_tests.add_question(req, res);});
	svr.Put(R"(/api/tests/(\d+)/questions)", [&](const httplib::Request& req, httplib::Response& res) {api_tests.set_question_order(req, res);});
	svr.Get(R"(/api/tests/(\d+)/users)", [&](const httplib::Request& req, httplib::Response& res) {api_tests.get_users_completed(req, res);});
	svr.Get(R"(/api/tests/(\d+)/scores)", [&](const httplib::Request& req, httplib::Response& res) {api_tests.get_users_scores(req, res);});
	svr.Get(R"(/api/tests/(\d+)/answers)", [&](const httplib::Request& req, httplib::Response& res) {api_tests.get_users_answers(req, res);});
	//Resource ATTEMPT
	svr.Post(R"(/api/attempt)", [&](const httplib::Request& req, httplib::Response& res) {api_attempt.create_attempt(req, res);});
	svr.Put(R"(/api/attempt/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_attempt.update_answer(req, res);});
	svr.Delete(R"(/api/attempt/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_attempt.finish_attempt(req, res);});
	svr.Get(R"(/api/attempt)", [&](const httplib::Request& req, httplib::Response& res) {api_attempt.get_info(req, res);});
	//Resource ANSWERS
	svr.Post(R"(/api/answers)", [&](const httplib::Request& req, httplib::Response& res) {api_answers.create_answer(req, res);});
	svr.Get(R"(/api/answers/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_answers.get_answer(req, res);});
	svr.Put(R"(/api/answers/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_answers.update_answer(req, res);});
	svr.Delete(R"(/api/answers/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {api_answers.delete_answer(req, res);});
	
}