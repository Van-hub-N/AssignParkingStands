#include "io.h"
#include "solver.h"

#include <iostream>
#include <string>

namespace {
struct Options {
    int start = 0;
    int count = 10000;
    std::string dataDir = "data/cases";
};
}

int main(int argc, char** argv) {
    Options opt;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto value = [&](const char* name) -> const char* {
            if (i + 1 >= argc) {
                std::cerr << "参数 " << name << " 缺少取值\n";
                return nullptr;
            }
            return argv[++i];
        };
        if (arg == "--start") {
            const char* v = value("--start");
            if (!v) return 2;
            opt.start = std::stoi(v);
        } else if (arg == "--count") {
            const char* v = value("--count");
            if (!v) return 2;
            opt.count = std::stoi(v);
        } else if (arg == "--data-dir") {
            const char* v = value("--data-dir");
            if (!v) return 2;
            opt.dataDir = v;
        } else if (arg == "--help" || arg == "-h") {
            std::cout << "用法: " << argv[0]
                      << " [--start N] [--count N] [--data-dir 目录]\n";
            return 0;
        } else {
            std::cerr << "未知参数: " << arg << "\n";
            return 2;
        }
    }

    long long checked = 0;
    long long badCases = 0;
    long long badSolutions = 0;
    long long totalCost1 = 0;
    long long totalCost2 = 0;

    for (int offset = 0; offset < opt.count; ++offset) {
        const int caseId = opt.start + offset;
        Case c;
        std::string err;
        if (!loadCase(caseId, opt.dataDir, c, err)) {
            std::cerr << err << "\n";
            ++badCases;
            continue;
        }
        ++checked;
        if (!validateCase(c, err)) {
            std::cerr << "案例 " << caseId << " 不合法: " << err << "\n";
            ++badCases;
            continue;
        }

        GreedySolver g1(GreedyStrategy::ByPassengers);
        GreedySolver g2(GreedyStrategy::ByArrival);
        Solution s1 = g1.solve(c);
        Solution s2 = g2.solve(c);
        totalCost1 += s1.objective;
        totalCost2 += s2.objective;

        std::string solErr;
        if (!s1.feasible || !validateSolution(c, s1, solErr)) {
            std::cerr << "案例 " << caseId << " 策略1 校验失败: "
                      << (solErr.empty() ? "存在未分配飞机" : solErr) << "\n";
            ++badSolutions;
        }
        if (!s2.feasible || !validateSolution(c, s2, solErr)) {
            std::cerr << "案例 " << caseId << " 策略2 校验失败: "
                      << (solErr.empty() ? "存在未分配飞机" : solErr) << "\n";
            ++badSolutions;
        }

        if ((offset + 1) % 2000 == 0) {
            std::cout << "已校验 " << (offset + 1) << " 个案例...\n";
        }
    }

    std::cout << "\n===== 校验汇总 =====\n"
              << "读取案例: " << checked << "\n"
              << "不合法案例: " << badCases << "\n"
              << "非法贪心解: " << badSolutions << "\n"
              << "策略1 总目标值: " << totalCost1 << "\n"
              << "策略2 总目标值: " << totalCost2 << "\n";
    return (badCases == 0 && badSolutions == 0) ? 0 : 2;
}
