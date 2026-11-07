#include "io.h"
#include "solver.h"

#include <algorithm>
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
    int maxK = 11;
    int stride = 1;
    double timeLimitMs = 2000.0;
    long long nodeLimit = 5000000;
    std::string dataDir = "data/cases";
    std::string outPath = "results/branch_bound_benchmark.csv";
};

struct Totals {
    long long cases = 0;
    long long skipped = 0;
    long long invalidCases = 0;
    long long invalidSolutions = 0;
    long long greedyCost = 0;
    long long backtrackingCost = 0;
    long long branchBoundCost = 0;

    long long backtrackingOptimal = 0;
    long long backtrackingLimited = 0;
    long long backtrackingInfeasible = 0;
    long long branchBoundOptimal = 0;
    long long branchBoundLimited = 0;
    long long branchBoundInfeasible = 0;

    long long bbBetterThanGreedy = 0;
    long long bbEqualGreedy = 0;
    long long bbWorseGreedy = 0;
    long long bbBetterThanBacktracking = 0;
    long long bbEqualBacktracking = 0;
    long long bbWorseBacktracking = 0;

    double backtrackingTimeMs = 0.0;
    double branchBoundTimeMs = 0.0;
    long long backtrackingNodes = 0;
    long long branchBoundNodes = 0;
    long long maxBacktrackingNodes = 0;
    long long maxBranchBoundNodes = 0;
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
                 "       [--time-limit-ms 毫秒] [--node-limit 结点数]"
                 " [--data-dir 案例目录] [--out 结果CSV]\n"
              << "示例: " << argv0 << " --start 0 --count 3000 --max-k 11"
                 " --time-limit-ms 2000 --node-limit 10000000\n";
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
        opt.minK > opt.maxK || opt.stride <= 0 || opt.timeLimitMs < 0 ||
        opt.nodeLimit < 0) {
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
    dst.greedyCost += src.greedyCost;
    dst.backtrackingCost += src.backtrackingCost;
    dst.branchBoundCost += src.branchBoundCost;
    dst.backtrackingOptimal += src.backtrackingOptimal;
    dst.backtrackingLimited += src.backtrackingLimited;
    dst.backtrackingInfeasible += src.backtrackingInfeasible;
    dst.branchBoundOptimal += src.branchBoundOptimal;
    dst.branchBoundLimited += src.branchBoundLimited;
    dst.branchBoundInfeasible += src.branchBoundInfeasible;
    dst.bbBetterThanGreedy += src.bbBetterThanGreedy;
    dst.bbEqualGreedy += src.bbEqualGreedy;
    dst.bbWorseGreedy += src.bbWorseGreedy;
    dst.bbBetterThanBacktracking += src.bbBetterThanBacktracking;
    dst.bbEqualBacktracking += src.bbEqualBacktracking;
    dst.bbWorseBacktracking += src.bbWorseBacktracking;
    dst.backtrackingTimeMs += src.backtrackingTimeMs;
    dst.branchBoundTimeMs += src.branchBoundTimeMs;
    dst.backtrackingNodes += src.backtrackingNodes;
    dst.branchBoundNodes += src.branchBoundNodes;
    dst.maxBacktrackingNodes =
        std::max(dst.maxBacktrackingNodes, src.maxBacktrackingNodes);
    dst.maxBranchBoundNodes =
        std::max(dst.maxBranchBoundNodes, src.maxBranchBoundNodes);
    dst.improvedTotal += src.improvedTotal;
}

const char* statusOf(const Solution& sol, bool valid) {
    if (!valid || !sol.feasible) return "infeasible";
    if (sol.complete) return "optimal";
    if (sol.timeLimitReached) return "time_limit";
    if (sol.nodeLimitReached) return "node_limit";
    return "limited";
}

void printTotals(const char* name, const Totals& t) {
    std::cout << "[" << name << "]\n";
    std::cout << "  测试案例: " << t.cases << "，跳过(K 范围外): " << t.skipped
              << "，非法案例: " << t.invalidCases
              << "，非法解: " << t.invalidSolutions << "\n";
    std::cout << "  回溯: 最优 " << t.backtrackingOptimal
              << "，受限 " << t.backtrackingLimited
              << "，不可行 " << t.backtrackingInfeasible
              << "；总目标 " << t.backtrackingCost << "\n";
    std::cout << "  分支限界: 最优 " << t.branchBoundOptimal
              << "，受限 " << t.branchBoundLimited
              << "，不可行 " << t.branchBoundInfeasible
              << "；总目标 " << t.branchBoundCost << "\n";
    std::cout << "  分支限界 vs 贪心 优/平/劣: " << t.bbBetterThanGreedy << " / "
              << t.bbEqualGreedy << " / " << t.bbWorseGreedy << "\n";
    std::cout << "  分支限界 vs 回溯 优/平/劣: "
              << t.bbBetterThanBacktracking << " / "
              << t.bbEqualBacktracking << " / " << t.bbWorseBacktracking
              << "\n";
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "  回溯总耗时: " << t.backtrackingTimeMs
              << " ms，总节点: " << t.backtrackingNodes
              << "，最大节点: " << t.maxBacktrackingNodes << "\n";
    std::cout << "  分支限界总耗时: " << t.branchBoundTimeMs
              << " ms，总节点: " << t.branchBoundNodes
              << "，最大节点: " << t.maxBranchBoundNodes << "\n";
    if (t.greedyCost > 0) {
        std::cout << "  回溯目标值相对贪心: "
                  << (static_cast<double>(t.backtrackingCost - t.greedyCost) /
                      t.greedyCost * 100.0)
                  << " %\n";
        std::cout << "  分支限界目标值相对贪心: "
                  << (static_cast<double>(t.branchBoundCost - t.greedyCost) /
                      t.greedyCost * 100.0)
                  << " %\n";
    }
    if (t.backtrackingCost > 0) {
        std::cout << "  分支限界目标值相对回溯: "
                  << (static_cast<double>(t.branchBoundCost -
                                          t.backtrackingCost) /
                      t.backtrackingCost * 100.0)
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
    out << "CaseId,N,M,K,Scale,Greedy_Cost,"
           "Backtracking_Cost,Backtracking_TimeMs,Backtracking_Nodes,"
           "Backtracking_Complete,Backtracking_Status,"
           "BranchBound_Cost,BranchBound_TimeMs,BranchBound_Nodes,"
           "BranchBound_Complete,BranchBound_Status,"
           "GapPercent_vs_Greedy,GapPercent_vs_Backtracking\n";

    Totals all;
    Totals byScale[3];

    std::cout << "开始分支限界对比实验，参数: K=[" << opt.minK << ","
              << opt.maxK << "], stride=" << opt.stride
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
        const Solution btSol = backtracking.solve(c);

        BranchBoundSolver branchBound(opt.timeLimitMs, opt.nodeLimit);
        const Solution bbSol = branchBound.solve(c);

        std::string err;
        const bool greedyValid =
            greedySol.feasible && validateSolution(c, greedySol, err);
        err.clear();
        const bool btValid =
            btSol.feasible && validateSolution(c, btSol, err);
        err.clear();
        const bool bbValid =
            bbSol.feasible && validateSolution(c, bbSol, err);

        row.cases = 1;
        row.greedyCost = greedySol.objective;
        row.backtrackingCost = btSol.objective;
        row.branchBoundCost = bbSol.objective;
        row.backtrackingTimeMs = btSol.timeMs;
        row.branchBoundTimeMs = bbSol.timeMs;
        row.backtrackingNodes = btSol.nodesExpanded;
        row.branchBoundNodes = bbSol.nodesExpanded;
        row.maxBacktrackingNodes = btSol.nodesExpanded;
        row.maxBranchBoundNodes = bbSol.nodesExpanded;

        if (!greedyValid) ++row.invalidSolutions;
        if (!btValid) ++row.invalidSolutions;
        if (!bbValid) ++row.invalidSolutions;

        if (!btSol.feasible) {
            ++row.backtrackingInfeasible;
        } else if (btSol.complete) {
            ++row.backtrackingOptimal;
        } else {
            ++row.backtrackingLimited;
        }

        if (!bbSol.feasible) {
            ++row.branchBoundInfeasible;
        } else if (bbSol.complete) {
            ++row.branchBoundOptimal;
        } else {
            ++row.branchBoundLimited;
        }

        if (bbSol.objective < greedySol.objective) {
            ++row.bbBetterThanGreedy;
            row.improvedTotal += greedySol.objective - bbSol.objective;
        } else if (bbSol.objective == greedySol.objective) {
            ++row.bbEqualGreedy;
        } else {
            ++row.bbWorseGreedy;
        }

        if (bbSol.objective < btSol.objective) {
            ++row.bbBetterThanBacktracking;
        } else if (bbSol.objective == btSol.objective) {
            ++row.bbEqualBacktracking;
        } else {
            ++row.bbWorseBacktracking;
        }

        const Scale scale = scaleOf(c.K);
        addTotals(all, row);
        addTotals(byScale[static_cast<int>(scale)], row);

        auto pct = [](long long value, long long base) {
            return base > 0
                       ? static_cast<double>(value - base) / base * 100.0
                       : 0.0;
        };

        out << caseId << ',' << c.N << ',' << c.M << ',' << c.K << ','
            << scaleName(scale) << ',' << greedySol.objective << ','
            << btSol.objective << ',' << std::fixed << std::setprecision(6)
            << btSol.timeMs << ',' << btSol.nodesExpanded << ','
            << (btSol.complete ? 1 : 0) << ','
            << statusOf(btSol, btValid) << ',' << bbSol.objective << ','
            << bbSol.timeMs << ',' << bbSol.nodesExpanded << ','
            << (bbSol.complete ? 1 : 0) << ',' << statusOf(bbSol, bbValid)
            << ',' << pct(bbSol.objective, greedySol.objective) << ','
            << pct(bbSol.objective, btSol.objective) << "\n";
    }

    out.close();
    printTotals("总计", all);
    printTotals("小规模 K<=15", byScale[0]);
    printTotals("中规模 16<=K<=80", byScale[1]);
    printTotals("大规模 K>80", byScale[2]);
    std::cout << "结果已写入 " << opt.outPath << "\n";
    return 0;
}
