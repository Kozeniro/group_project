#pragma once
#include "ResourceCourse.h"

#include "httplib.h"
#include "json.hpp"

class Api_resCourse {
private:
	ResourceCourse& resCourse;
public:
	Api_resCourse(ResourceCourse& resCourse);
	void get_all(const httplib::Request& req, httplib::Response& res);
	void get_info(const httplib::Request& req, httplib::Response& res);
	void update_info(const httplib::Request& req, httplib::Response& res);
	void get_tests(const httplib::Request& req, httplib::Response& res);
	void is_test_active(const httplib::Request& req, httplib::Response& res);
	void set_test_active(const httplib::Request& req, httplib::Response& res);
	void add_test(const httplib::Request& req, httplib::Response& res);
	void remove_test(const httplib::Request& req, httplib::Response& res);
	void get_students(const httplib::Request& req, httplib::Response& res);
	void add_user(const httplib::Request& req, httplib::Response& res);
	void remove_user(const httplib::Request& req, httplib::Response& res);
	void create_course(const httplib::Request& req, httplib::Response& res);
	void delete_course(const httplib::Request& req, httplib::Response& res);
};

