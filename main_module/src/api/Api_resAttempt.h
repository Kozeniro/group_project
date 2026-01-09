#pragma once
#include "ResourceAttempt.h"
#include "httplib.h"
#include "json.hpp"

class Api_resAttempt {
private:
	ResourceAttempt& resAttempt;
public:
	Api_resAttempt(ResourceAttempt& resAttempt);
	void create_attempt(const httplib::Request& req, httplib::Response& res);
	void update_answer(const httplib::Request& req, httplib::Response& res);
	void finish_attempt(const httplib::Request& req, httplib::Response& res);
	void get_info(const httplib::Request& req, httplib::Response& res);
};

