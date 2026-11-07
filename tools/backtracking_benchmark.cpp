#include "io.h"
#include "solver.h"

#include <algorithm>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {

struct Options {
    int start = 0;
    int count = 10000;
    int minK = 0;
    int maxK = 8;
    int stride = 1;
    double timeLimitMs = 2000.0;
    long long nodeLimit = 5000000;
    std::string dataDir = "data/cases";
    std::string outPath = "results/backtracking_benchmark.csv";
};

struct Totals {
    long long cases = 0;
    long long skipped = 0;
    long long invalidCases = 0;
    long long invalidSolutions = 0;
    long long optimal = 0;
    long long limited = 0;
    long long infeasible = 0;
    long long improved = 0;
    long long equal = 0;
    long long worse = 0;
    long long greedyCost = 0;
    long long backtrackCost = 0;
    double timeMs = 0.0;
    long long nodes = 0;
    long long maxNodes = 0;
    long long improvedTotal = 0;
};

enum class Scale { Small = 0, Medium = 1, Large = 2 };

Scale scaleOf(int K) {
    if (K <= 15) return Scale::Small;
    if (K <= 80) return Scale::Medium;
    return Scale::Large;
}

const char* scaleName(Scale s) {
    switch (s) {
        case Scale::Small: return "small";
        case Scale::Medium: return "medium";
        case Scale::Large: return "large";
    }
    return "unknown";
}

void printUsage(const char* argv0) {
    std::cout << "用法: " << argv0
              << " [--start 起始编号] [--count 案例数] [--min-k 最小K]"
                 " [--max-k 最大K] [--stride 步长]\n"
                 "       [--time-limit-ms 毫秒] [--node-limit 结点数]\n"
                 "       [--data-dir 案例目录] [--out 结果CSV]\n"
              << "示例: " << argv0 << " --start 0 --count 3000 --max-k 6"
                 " --time-limit-ms 2000 --node-limit 5000000\n";
}

enum class ParseStatus { Ok, Help, Error };

ParseStatus parseArgs(int argc, char** argv, Options& opt) {
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
            if (!v) return ParseStatus::Error;
            opt.start = std::stoi(v);
        } else if (arg == "--count") {
            const char* v = value("--count");
            if (!v) return ParseStatus::Error;
            opt.count = std::stoi(v);
        } else if (arg == "--min-k") {
            const char* v = value("--min-k");
            if (!v) return ParseStatus::Error;
            opt.minK = std::stoi(v);
        } else if (arg == "--max-k") {
            const char* v = value("--max-k");
            if (!v) return ParseStatus::Error;
            opt.maxK = std::stoi(v);
        } else if (arg == "--stride") {
            const char* v = value("--stride");
            if (!v) return ParseStatus::Error;
            opt.stride = std::stoi(v);
        } else if (arg == "--time-limit-ms") {
            const char* v = value("--time-limit-ms");
            if (!v) return ParseStatus::Error;
            opt.timeLimitMs = std::stod(v);
        } else if (arg == "--node-limit") {
            const char* v = value("--node-limit");
            if (!v) return ParseStatus::Error;
            opt.nodeLimit = std::stoll(v);
        } else if (arg == "--data-dir") {
            const char* v = value("--data-dir");
            if (!v) return ParseStatus::Error;
            opt.dataDir = v;
        } else if (arg == "--out") {
            const char* v = value("--out");
            if (!v) return ParseStatus::Error;
            opt.outPath = v;
        } else if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            return ParseStatus::Help;
        } else {
            std::cerr << "未知参数: " << arg << "\n";
            printUsage(argv[0]);
            return ParseStatus::Error;
        }
    }
    if (opt.start < 0 || opt.count <= 0 || opt.minK < 0 || opt.maxK < 0 ||
        opt.minK > opt.maxK || opt.stride <= 0 ||
        opt.timeLimitMs < 0 || opt.nodeLimit < 0) {
        std::cerr << "参数范围错误\n";
        return ParseStatus::Error;
    }
    return ParseStatus::Ok;
}

void addTotals(Totals& dst, const Totals& src) {
    dst.cases += src.cases;
    dst.skipped += src.skipped;
    dst.invalidCases += src.invalidCases;
    dst.invalidSolutions += src.invalidSolutions;
    dst.optimal += src.optimal;
    dst.limited += src.limited;
    dst.infeasible += src.infeasible;
    dst.improved += src.improved;
    dst.equal += src.equal;
    dst.worse += src.worse;
    dst.greedyCost += src.greedyCost;
    dst.backtrackCost += src.backtrackCost;
    dst.timeMs += src.timeMs;
    dst.nodes += src.nodes;
    dst.maxNodes = std::max(dst.maxNodes, src.maxNodes);
    dst.improvedTotal += src.improvedTotal;
}

void printTotals(const Totals& t) {
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "  测试案例: " << t.cases << "，跳过(K>max-k): " << t.skipped << "\n";
    std::cout << "  完成全搜索(证明最优): " << t.optimal
              << "，触发限制: " << t.limited
              << "，不可行: " << t.infeasible << "\n";
    std::cout << "  非法案例: " << t.invalidCases
              << "，非法解: " << t.invalidSolutions << "\n";
    std::cout << "  回溯优于贪心 / 持平 / 更差: "
              << t.improved << " / " << t.equal << " / " << t.worse << "\n";
    std::cout << "  贪心总目标值: " << t.greedyCost
              << "，回溯总目标值: " << t.backtrackCost << "\n";
    std::cout << "  回溯总耗时: " << t.timeMs << " ms"
              << "，总结点数: " << t.nodes
              << "，最大单案例结点数: " << t.maxNodes << "\n";
    if (t.greedyCost > 0) {
        std::cout << "  目标值相对贪心变化: "
                  << (static_cast<double>(t.backtrackCost - t.greedyCost) /
                      t.greedyCost * 100.0)
                  << " %\n";
    }
}

}  // namespace

int main(int argc, char** argv) {
    Options opt;
    const ParseStatus status = parseArgs(argc, argv, opt);
    if (status == ParseStatus::Help) return 0;
    if (status == ParseStatus::Error) return 2;

    const std::filesystem::path outPath(opt.outPath);
    if (!outPath.parent_path().empty()) {
        std::error_code ec;
        std::filesystem::create_directories(outPath.parent_path(), ec);
        if (ec) {
            std::cerr << "无法创建结果目录: " << outPath.parent_path() << "\n";
            return 1;
        }
    }

    std::ofstream out(outPath, std::ios::trunc);
    if (!out) {
        std::cerr << "无法写入结果文件: " << outPath << "\n";
        return 1;
    }
    out << "CaseId,N,M,K,Scale,Greedy_Cost,Backtracking_Cost,GapPercent,"
           "Backtracking_TimeMs,Nodes,Complete,Status\n";

    Totals all;
    Totals byScale[3];

    std::cout << "开始回溯法实验，参数: K=[" << opt.minK << "," << opt.maxK
              << "], stride=" << opt.stride
              << ", timeLimit=" << opt.timeLimitMs
              << " ms, nodeLimit=" << opt.nodeLimit << "\n";

    for (int offset = 0; offset < opt.count; offset += opt.stride) {
        const int caseId = opt.start + offset;
        Case c;
        std::string loadErr;
        if (!loadCase(caseId, opt.dataDir, c, loadErr)) {
            std::cerr << "读取失败: " << loadErr << "\n";
            ++all.invalidCases;
            continue;
        }

        Totals row;
        if (c.K < opt.minK || c.K > opt.maxK) {
            row.skipped = 1;
            addTotals(all, row);
            continue;
        }

        std::string caseErr;
        if (!validateCase(c, caseErr)) {
            std::cerr << "案例 " << caseId << " 不合法: " << caseErr << "\n";
            ++row.invalidCases;
            row.cases = 1;
            addTotals(all, row);
            addTotals(byScale[static_cast<int>(scaleOf(c.K))], row);
            continue;
        }

        GreedySolver greedy(GreedyStrategy::ByPassengers);
        const Solution greedySol = greedy.solve(c);

        BacktrackingSolver backtracking(opt.timeLimitMs, opt.nodeLimit);
        Solution btSol = backtracking.solve(c);

        std::string err;
        const bool greedyValid = greedySol.feasible &&
                                 validateSolution(c, greedySol, err);
        err.clear();
        const bool btValid = btSol.feasible &&
                             validateSolution(c, btSol, err);

        row.cases = 1;
        row.greedyCost = greedySol.objective;
        row.backtrackCost = btSol.objective;
        row.timeMs = btSol.timeMs;
        row.nodes = btSol.nodesExpanded;
        row.maxNodes = btSol.nodesExpanded;

        if (!greedyValid) {
            ++row.invalidSolutions;
        }
        if (!btValid) {
            ++row.invalidSolutions;
        }
        if (!btSol.feasible) {
            ++row.infeasible;
        } else if (btSol.complete) {
            ++row.optimal;
        } else {
            ++row.limited;
        }
        if (btSol.objective < greedySol.objective) {
            ++row.improved;
            row.improvedTotal = greedySol.objective - btSol.objective;
        } else if (btSol.objective == greedySol.objective) {
            ++row.equal;
        } else {
            ++row.worse;
        }

        const Scale scale = scaleOf(c.K);
        addTotals(all, row);
        addTotals(byScale[static_cast<int>(scale)], row);

        out << caseId << ',' << c.N << ',' << c.M << ',' << c.K << ','
            << scaleName(scale) << ',' << greedySol.objective << ','
            << btSol.objective << ',' << std::fixed << std::setprecision(6)
            << (greedySol.objective > 0
                    ? (static_cast<double>(btSol.objective - greedySol.objective) /
                       greedySol.objective * 100.0)
                    : 0.0)
            << ',' << btSol.timeMs << ',' << btSol.nodesExpanded << ','
            << (btSol.complete ? 1 : 0) << ',';
        if (!btValid) {
            out << "invalid";
        } else if (!btSol.feasible) {
            out << "infeasible";
        } else if (btSol.complete) {
            out << "optimal";
        } else if (btSol.timeLimitReached) {
            out << "time_limit";
        } else {
            out << "node_limit";
        }
        out << '\n';

        if ((offset + 1) % 100 == 0) {
            std::cout << "已处理 " << (offset + 1) << " 个案例...\n";
        }
    }

    out.flush();
    if (!out) {
        std::cerr << "写入结果文件失败: " << outPath << "\n";
        return 1;
    }

    std::cout << "\n===== 总体结果 =====\n";
    printTotals(all);
    for (int i = 0; i < 3; ++i) {
        if (byScale[i].cases == 0) continue;
        std::cout << "\n[" << scaleName(static_cast<Scale>(i)) << "] 规模\n";
        printTotals(byScale[i]);
    }
    std::cout << "\n详细结果: " << outPath << "\n";

    return (all.invalidCases == 0 && all.invalidSolutions == 0) ? 0 : 2;
}
