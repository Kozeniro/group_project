#pragma once
#include "ResourceAttempt.h"
#include "PermissionChecker.h"
#include "httplib.h"
#include "json.hpp"

class Api_resAttempt {
private:
	ResourceAttempt& resAttempt;
	PermissionChecker& permChecker;
public:
	Api_resAttempt(ResourceAttempt& resAttempt, PermissionChecker& permChecker);
	void create_attempt(const httplib::Request& req, httplib::Response& res);
	void update_answer(const httplib::Request& req, httplib::Response& res);
	void finish_attempt(const httplib::Request& req, httplib::Response& res);
	void get_info(const httplib::Request& req, httplib::Response& res);
};

