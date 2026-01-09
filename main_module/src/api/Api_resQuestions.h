#pragma once
#include "ResourceQuestions.h"
#include "httplib.h"

class Api_resQuestions {
private:
	ResourceQuestions& resQuestions;
public:
	Api_resQuestions(ResourceQuestions& resQuestions);
	void get_all(const httplib::Request&, httplib::Response& res);
	void get_info(const httplib::Request& req, httplib::Response& res);
	void update_question(const httplib::Request& req, httplib::Response& res);
	void create_question(const httplib::Request& req, httplib::Response& res);
	void delete_question(const httplib::Request& req, httplib::Response& res);
};