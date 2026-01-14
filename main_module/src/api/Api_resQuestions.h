#pragma once
#include "ResourceQuestions.h"
#include "PermissionChecker.h"
#include "httplib.h"
#include "json.hpp"

class Api_resQuestions {
private:
	ResourceQuestions& resQuestions;
	PermissionChecker& permChecker;
public:
	Api_resQuestions(ResourceQuestions& resQuestions,PermissionChecker& permChecker);
	void get_all(const httplib::Request& req, httplib::Response& res);
	void get_info(const httplib::Request& req, httplib::Response& res);
	void update_question(const httplib::Request& req, httplib::Response& res);
	void create_question(const httplib::Request& req, httplib::Response& res);
	void delete_question(const httplib::Request& req, httplib::Response& res);
};