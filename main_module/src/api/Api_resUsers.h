#pragma once
#include "ResourceUsers.h"
#include "PermissionChecker.h"
#include "httplib.h"
#include "json.hpp"

class Api_resUsers {
private:
	ResourceUsers& resUsers;
	PermissionChecker& permChecker;
public:
	Api_resUsers(ResourceUsers& resUsers, PermissionChecker& permChecker);
	void create(const httplib::Request& req, httplib::Response& res);
	void get_all(const httplib::Request& req, httplib::Response& res);
	void get_name(const httplib::Request& req, httplib::Response& res);
	void update_name(const httplib::Request& req, httplib::Response& res);
	void get_info(const httplib::Request& req, httplib::Response& res);
	void get_roles(const httplib::Request& req, httplib::Response& res);
	void set_roles(const httplib::Request& req, httplib::Response& res);
	void check_user_blocked(const httplib::Request& req, httplib::Response& res);
	void set_user_blocked(const httplib::Request& req, httplib::Response& res);
};

