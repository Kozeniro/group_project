#include <iostream>
#include <pqxx/pqxx>

#include "Api_resUsers.h"
#include "Api_resCourse.h"
#include "Api_resQuestions.h"
#include "Api_resTests.h"
#include "Api_resAnswers.h"
#include "Api_resAttempt.h"

int main()
{
    std::string connection_string = "postgres://bf39575214c9189fa70701554b75ce7dd71cc18accecae236c76748378e000a8:sk_keRvGx-d9MLa5h3yNF3Pk@db.prisma.io:5432/postgres?sslmode=require";
    pqxx::connection conn(connection_string);

    pqxx::work worker(conn);

    pqxx::result response = worker.exec("SELECT * FROM users");
    for (size_t i = 0; i < response.size(); i++)
    {
        std::cout << "id: " << response[i][0] << " full_name: " << response[i][1] << " is_blocked: " << response[i][2] << std::endl;
    }
    
}