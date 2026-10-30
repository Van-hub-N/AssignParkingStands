#pragma once
#include "case.h"
#include <string>

bool validateCase(const Case& c, std::string& err);
void saveCase(const Case& c, const std::string& path);
std::string pad5(int x);
Case loadCase(int caseId, const std::string& dir = "../data/cases");
