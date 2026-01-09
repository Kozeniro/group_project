#include "Api_resQuestions.h"

Api_resQuestions::Api_resQuestions(ResourceQuestions& resQuestions) : resQuestions(resQuestions) {};

void Api_resQuestions::get_all(const httplib::Request&, httplib::Response& res) {
	auto questions = resQuestions.get_all();
	nlohmann::json json_res = nlohmann::json::array();
	for (const auto& q : questions) {
		json_res.push_back(
			{ {"name", q.name},{"version", q.version},{"author_id", q.author_id} }
		);
	}
	res.set_content(json_res.dump(), "application/json");
}

void Api_resQuestions::get_info(const httplib::Request& req, httplib::Response& res) {
	int question_id = std::stoi(req.matches[1]);
	int version = std::stoi(req.get_param_value("version"));
	QuestionInfo info = resQuestions.get_info(question_id, version);
	nlohmann::json json_res = {
		{"name", info.name},
		{"text", info.text},
		{"options", info.options},
		{"correct_option", info.correct_option}
	};
	res.set_content(json_res.dump(), "application/json");
}

void Api_resQuestions::update_question(const httplib::Request& req, httplib::Response& res) {
	int question_id = std::stoi(req.matches[1]);
	std::string name = req.get_param_value("name");
	std::string text = req.get_param_value("text");
	nlohmann::json options = nlohmann::json::parse(req.get_param_value("options"));
	int correct_option = std::stoi(req.get_param_value("correct_option"));
	int author_id = std::stoi(req.get_param_value("author_id"));
	resQuestions.update_question(question_id, name, text, options, correct_option, author_id);
}


void Api_resQuestions::create_question(const httplib::Request& req, httplib::Response& res) {
	std::string name = req.get_param_value("name");
	std::string text = req.get_param_value("text");
	nlohmann::json options = nlohmann::json::parse(req.get_param_value("options"));
	int correct_option = std::stoi(req.get_param_value("correct_option"));
	int author_id = std::stoi(req.get_param_value("author_id"));
	int new_question_id = resQuestions.create_question(name, text, options, correct_option, author_id);
	res.set_content(std::to_string(new_question_id), "text/plain");
}

void Api_resQuestions::delete_question(const httplib::Request& req, httplib::Response& res) {
	int question_id = std::stoi(req.matches[1]);
	resQuestions.delete_question(question_id);
}
