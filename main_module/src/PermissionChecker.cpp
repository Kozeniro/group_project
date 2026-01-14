#include "PermissionChecker.h"


#include <iostream>

PermissionChecker::PermissionChecker(ResourceUsers& resUsers): resUsers(resUsers){}

PermissionInfo PermissionChecker::check(const httplib::Request& req, const std::string& permission){
    PermissionInfo info;
    auto auth_header = req.get_header_value("Authorization");
    if (auth_header.substr(0, 7) != "Bearer ") {
        info.status = 401;
        return info;
    }
    std::string token = auth_header.substr(7);
    auto decoded = jwt::decode(token);
    try {
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{"access-secret"});
        verifier.verify(decoded);

        if (decoded.get_expires_at() < std::chrono::system_clock::now()) {
            info.status = 401; 
            return info;
        }
        info.user_id = resUsers.get_user_id(decoded.get_payload_claim("user_id").as_string());
        if (resUsers.is_blocked(info.user_id)){
            info.status = 418;
            return info;
        }
        if (permission!=std::string("")){
            auto permissions = decoded.get_payload_claim("permissions").as_array();
            bool has_permission = false;
            for (const auto& p : permissions) {
                if (p.get<std::string>() == permission) {
                    has_permission = true;
                    break;
                } 
            }
            if (!has_permission) {
                info.status = 403;
                return info;
            }
        }
        

        info.status = 200;
    }catch (...) {
        info.status = 401;
    }
    return info;
}