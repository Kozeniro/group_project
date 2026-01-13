#pragma once
#include <jwt-cpp/jwt.h>
#include "ResourceUsers.h"
#include "httplib.h"

struct PermissionInfo{
    int status;
    int user_id;
};

class PermissionChecker{
private:
    ResourceUsers& resUsers;
public:
    PermissionChecker(ResourceUsers& resUsers);
    PermissionInfo check(const httplib::Request& req, const std::string& permission);
};