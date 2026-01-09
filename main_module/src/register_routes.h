#pragma once
#include <httplib.h>

#include "Api_resUsers.h"
#include "Api_resCourse.h"
#include "Api_resQuestions.h"
#include "Api_resTests.h"
#include "Api_resAnswers.h"
#include "Api_resAttempt.h"

void register_routes(httplib::Server& svr,
	Api_resUsers& api_users, Api_resCourse& api_course, Api_resQuestions& api_questions,
	Api_resTests& api_tests, Api_resAnswers& api_answers, Api_resAttempt& api_attempt);