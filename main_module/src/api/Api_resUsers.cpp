#include "Api_resUsers.h"

Api_resUsers::Api_resUsers(ResourceUsers& resUsers, PermissionChecker& permChecker) : resUsers(resUsers), permChecker(permChecker) {};

void Api_resUsers::get_user_id(const httplib::Request& req, httplib::Response& res) {
	PermissionInfo p_info = permChecker.check(req, "");
	if (p_info.status==401) {
        res.status = p_info.status; return;
    }
	nlohmann::json json_response;
	json_response["user_id"] = p_info.user_id;
	res.set_content(json_response.dump(), "application/json");
}

void Api_resUsers::get_notifications(const httplib::Request& req, httplib::Response& res) {
	PermissionInfo p_info = permChecker.check(req, "");
	if (p_info.status==401) {
        res.status = p_info.status; return;
    }
	nlohmann::json j = resUsers.get_notifications(p_info.user_id);
	res.set_content(j.dump(), "application/json");
}
void Api_resUsers::delete_notifications(const httplib::Request& req, httplib::Response& res) {
	PermissionInfo p_info = permChecker.check(req, "");
	if (p_info.status==401) {
        res.status = p_info.status; return;
    }
	resUsers.delete_notifications(p_info.user_id);
}

void Api_resUsers::get_all(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "user:list:read");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }
    
    auto users = resUsers.get_all();
    nlohmann::json j = nlohmann::json::array();
    for (const auto& user : users) {
        j.push_back({ {"id",user.id},{"name",user.full_name} });
    }
    res.set_content(j.dump(), "application/json");
}

void Api_resUsers::get_name(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    
    int user_id = std::stoi(req.matches[1]);
    std::string full_name = resUsers.get_name(user_id);
	if (full_name=="") {res.status = 404; return;}
    nlohmann::json json_response;
	json_response["name"] = full_name;
	res.set_content(json_response.dump(), "application/json");
}

void Api_resUsers::update_name(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "user:fullName:write");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    
    if (!body_json.contains("new_name")) {
        res.status = 400; return;
    }
    
    int user_id = std::stoi(req.matches[1]);
    if (p_info.status==403 && user_id != p_info.user_id){
        res.status = p_info.status; return;
    }
    
    auto new_name = body_json["new_name"].get<std::string>();
    if(!resUsers.update_name(user_id, new_name)) {res.status = 404;}
}

void Api_resUsers::get_info(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "user:data:read");
    if (p_info.status==401 || p_info.status==418) {
        res.status = p_info.status; return;
    }
    
    int user_id = std::stoi(req.matches[1]);
    if (p_info.status==403 && user_id != p_info.user_id){
        res.status = p_info.status; return;
    }

    auto info_type_str = req.get_param_value("info_type");
    Info info_type;
    if (info_type_str == "courses") { info_type = Courses; }
    else if (info_type_str == "scores") { info_type = Scores; }
    else if (info_type_str == "tests") { info_type = Tests; }
    else { res.status = 400; return; }
	
	try{
    std::vector<std::string> info_list = resUsers.get_info(user_id, info_type);
		
    nlohmann::json j;
    if (info_type == Scores) {
        std::vector<int> vec_scores;
        for (const auto& score : info_list) vec_scores.push_back(stoi(score));
        j = vec_scores;
    }
    else j = info_list;
    res.set_content(j.dump(), "application/json");
	} catch(...){res.status = 404;}
}

void Api_resUsers::get_roles(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "user:roles:read");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }

    int user_id = std::stoi(req.matches[1]);
	try{
	nlohmann::json j_roles = p_info.roles;
    res.set_content(j_roles.dump(), "application/json");
	} catch(...){res.status = 404;}
}

void Api_resUsers::set_roles(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "user:roles:write");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }
    
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    
    if (!body_json.contains("roles")) {
        res.status = 400; return;
    }  
    int user_id = std::stoi(req.matches[1]);
    auto new_roles = body_json["roles"].get<std::vector<std::string>>();

    resUsers.set_roles(user_id, new_roles);

    httplib::Client cli("localhost", 8081);
    nlohmann::json json_payload;
    json_payload["roles"] = new_roles;

    httplib::Headers headers = {
		{"Content-Type", "application/json"},
		{"Authorization", "Bearer " + p_info.token}
	};
	auto resp = cli.Post(
		"/me/role",
		headers,
		json_payload.dump(),
		"application/json"
	);

    if (!resp || resp->status != 204) {
        res.status = resp ? resp->status : 500;
		res.body = "Auth server error";
    }
}

void Api_resUsers::check_user_blocked(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "user:block:read");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }
    
    int user_id = std::stoi(req.matches[1]);
    bool blocked = resUsers.is_blocked(user_id);
    nlohmann::json json_response;
    json_response["blocked"] = blocked;

    res.set_content(json_response.dump(), "application/json");
}

void Api_resUsers::set_user_blocked(const httplib::Request& req, httplib::Response& res) {
    PermissionInfo p_info = permChecker.check(req, "user:block:write");
    if (p_info.status != 200) {
        res.status = p_info.status; return;
    }
    
    nlohmann::json body_json;
    try {
        body_json = nlohmann::json::parse(req.body);
    } catch (...) {
        res.status = 400; return;
    }
    
    if (!body_json.contains("blocked")) {
        res.status = 400; return;
    }
    
    int user_id = std::stoi(req.matches[1]);
    bool blocked = body_json["blocked"].get<bool>();
    if(!resUsers.set_blocked(user_id, blocked)) {res.status = 404;}
}