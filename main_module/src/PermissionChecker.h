#pragma once
#include <jwt-cpp/jwt.h>
#include "ResourceUsers.h"

struct PermissionInfo{
    int status = 0;
    int user_id;
};

class PermissionChecker{
private:
    ResourceUsers& resUsers;
public:
    PermissionChecker(ResourceUsers& resUsers);
    PermissionInfo check(const std::string& token, const std::string& permission);
};