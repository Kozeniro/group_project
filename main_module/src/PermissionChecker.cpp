#include "PermissionChecker.h"

PermissionChecker::PermissionChecker(ResourceUsers& resUsers): resUsers(resUsers){}

PermissionInfo PermissionChecker::check(const std::string& token, const std::string& permission){
    PermissionInfo info;
    auto decoded = jwt::decode(token);
    try {
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{"access-secret"});
        verifier.verify(decoded);

        if (decoded.get_expires_at() < std::chrono::system_clock::now()) {
            info.status = 401; 
            return info;
        }
        info.user_id = std::stoi(decoded.get_payload_claim("user_id").as_string());
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
        if (resUsers.is_blocked(info.user_id)){
            info.status = 418;
        }

        info.status = 200;
    }catch (...) {
        info.status = 401;
    }
    return info;
}