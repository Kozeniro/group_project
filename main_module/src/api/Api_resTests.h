#pragma once
#include "ResourceTests.h"
#include "httplib.h"
class Api_resTests {
private:
	ResourceTests& resTests;
public:
	Api_resTests(ResourceTests& resTests);
	void remove_question(const httplib::Request& req, httplib::Response& res);
	void add_question(const httplib::Request& req, httplib::Response& res);
	void set_question_order(const httplib::Request& req, httplib::Response& res);
	void get_users_completed(const httplib::Request& req, httplib::Response& res);
	void get_users_scores(const httplib::Request& req, httplib::Response& res);
	void get_users_answers(const httplib::Request& req, httplib::Response& res);

};