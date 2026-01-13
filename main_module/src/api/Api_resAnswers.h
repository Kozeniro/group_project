#pragma once
#include "ResourceAnswers.h"
#include "PermissionChecker.h"
#include "httplib.h"
#include "json.hpp"


class Api_resAnswers {
private:
	ResourceAnswers& resAnswers;
	PermissionChecker& permChecker;
public:
	Api_resAnswers(ResourceAnswers& resAnswers, PermissionChecker& permChecker);
	void create_answer(const httplib::Request& req, httplib::Response& res);
	void get_answer(const httplib::Request& req, httplib::Response& res);
	void update_answer(const httplib::Request& req, httplib::Response& res);
	void delete_answer(const httplib::Request& req, httplib::Response& res);
};
