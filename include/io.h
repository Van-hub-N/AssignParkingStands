#pragma once
#include "case.h"
#include <string>

bool validateCase(const Case& c, std::string& err);
void saveCase(const Case& c, const std::string& path);
