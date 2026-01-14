#pragma once
#include "ResourceTests.h"
#include "PermissionChecker.h"
#include "httplib.h"
#include "json.hpp"
class Api_resTests {
private:
	ResourceTests& resTests;
	PermissionChecker& permChecker;
public:
	Api_resTests(ResourceTests& resTests, PermissionChecker& permChecker);
	void remove_question(const httplib::Request& req, httplib::Response& res);
	void add_question(const httplib::Request& req, httplib::Response& res);
	void set_question_order(const httplib::Request& req, httplib::Response& res);
	void get_users_completed(const httplib::Request& req, httplib::Response& res);
	void get_users_scores(const httplib::Request& req, httplib::Response& res);
	void get_users_answers(const httplib::Request& req, httplib::Response& res);

};