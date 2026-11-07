#pragma once

#include "case.h"

#include <string>

// 检查案例是否满足题目假设，失败时通过 err 返回原因。
bool validateCase(const Case& c, std::string& err);

// 将案例写入二进制文件。成功返回 true。
bool saveCase(const Case& c, const std::string& path);

// 从 dir 目录读取指定编号的案例。成功返回 true，并通过 out 返回案例。
bool loadCase(int caseId, const std::string& dir, Case& out, std::string& err);

// 便捷重载：读取失败时返回一个 K=0 的空案例。
Case loadCase(int caseId, const std::string& dir = "data/cases");

// 将编号补零为 5 位，例如 7 -> "00007"。
std::string pad5(int x);
