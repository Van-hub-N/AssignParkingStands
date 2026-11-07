#include "io.h"
#include "solver.h"

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {

void printUsage(const char* argv0) {
    std::cout << "用法: " << argv0
              << " [--case 案例编号] [--data-dir 案例目录]\n"
                 "       [--time-limit-ms 回溯时间上限] [--node-limit 回溯结点上限]\n";
}

void printSolution(const Case& c, const Solution& sol, const char* title) {
    std::cout << "\n=== " << title << " ===\n";
    std::cout << "目标值: " << sol.objective << " 人·分钟"
              << "，可行: " << (sol.feasible ? "是" : "否")
              << "，完整搜索: " << (sol.complete ? "是" : "否")
              << "，结点数: " << sol.nodesExpanded
              << "，耗时: " << std::fixed << std::setprecision(6)
              << sol.timeMs << " ms\n";

    std::cout << std::left << std::setw(8) << "飞机"
              << std::setw(8) << "机位"
              << std::setw(8) << "类型"
              << std::setw(12) << "下机时间"
              << "贡献\n";
    for (int i = 0; i < c.K; ++i) {
        const int s = sol.assign[i];
        if (s < 0 || s >= static_cast<int>(c.stands.size())) {
            std::cout << std::left << std::setw(8) << i
                      << std::setw(8) << "-" << std::setw(8) << "-"
                      << std::setw(12) << "-" << "0\n";
            continue;
        }
        const Stand& stand = c.stands[s];
        const long long contribution =
            static_cast<long long>(c.planes[i].passengers) * stand.unloadTime;
        std::cout << std::left << std::setw(8) << i
                  << std::setw(8) << s
                  << std::setw(8) << (stand.isBridge ? "靠桥" : "远端")
                  << std::setw(12) << stand.unloadTime
                  << contribution << "\n";
    }

    std::cout << "机位时间轴:\n";
    for (int s = 0; s < static_cast<int>(c.stands.size()); ++s) {
        std::vector<int> planes;
        for (int i = 0; i < c.K; ++i) {
            if (sol.assign[i] == s) planes.push_back(i);
        }
        if (planes.empty()) continue;
        std::sort(planes.begin(), planes.end(), [&](int a, int b) {
            return c.planes[a].arrive < c.planes[b].arrive;
        });
        std::cout << "  机位 " << s << " ("
                  << (c.stands[s].isBridge ? "靠桥" : "远端") << ", u="
                  << c.stands[s].unloadTime << "): ";
        for (int i : planes) {
            std::cout << "飞机" << i << " [" << c.planes[i].arrive << ","
                      << c.planes[i].depart << ") ";
        }
        std::cout << "\n";
    }
}

}  // namespace

int main(int argc, char** argv) {
    int caseId = 2081;
    double timeLimitMs = 5000.0;
    long long nodeLimit = 10000000;
    std::string dataDir = "data/cases";

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto value = [&](const char* name) -> const char* {
            if (i + 1 >= argc) {
                std::cerr << "参数 " << name << " 缺少取值\n";
                return nullptr;
            }
            return argv[++i];
        };
        if (arg == "--case") {
            const char* v = value("--case");
            if (!v) return 2;
            caseId = std::stoi(v);
        } else if (arg == "--data-dir") {
            const char* v = value("--data-dir");
            if (!v) return 2;
            dataDir = v;
        } else if (arg == "--time-limit-ms") {
            const char* v = value("--time-limit-ms");
            if (!v) return 2;
            timeLimitMs = std::stod(v);
        } else if (arg == "--node-limit") {
            const char* v = value("--node-limit");
            if (!v) return 2;
            nodeLimit = std::stoll(v);
        } else if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            return 0;
        } else {
            std::cerr << "未知参数: " << arg << "\n";
            printUsage(argv[0]);
            return 2;
        }
    }

    Case c;
    std::string err;
    if (!loadCase(caseId, dataDir, c, err)) {
        std::cerr << err << "\n";
        return 1;
    }
    if (!validateCase(c, err)) {
        std::cerr << "案例不合法: " << err << "\n";
        return 2;
    }

    std::cout << "案例 " << c.caseId << ": N=" << c.N << ", M=" << c.M
              << ", K=" << c.K << "\n";
    std::cout << "机位下机时间:";
    for (const Stand& s : c.stands) {
        std::cout << " " << s.id << "(" << (s.isBridge ? "桥" : "远")
                  << "," << s.unloadTime << ")";
    }
    std::cout << "\n";

    GreedySolver greedy1(GreedyStrategy::ByPassengers);
    GreedySolver greedy2(GreedyStrategy::ByArrival);
    const Solution g1 = greedy1.solve(c);
    const Solution g2 = greedy2.solve(c);
    printSolution(c, g1, "贪心策略 1（乘客优先）");
    printSolution(c, g2, "贪心策略 2（到达优先）");

    BacktrackingSolver backtracking(timeLimitMs, nodeLimit);
    const Solution bt = backtracking.solve(c);
    printSolution(c, bt, "回溯法");

    BranchBoundSolver branchBound(timeLimitMs, nodeLimit);
    const Solution bb = branchBound.solve(c);
    printSolution(c, bb, "分支限界法");
    return 0;
}
