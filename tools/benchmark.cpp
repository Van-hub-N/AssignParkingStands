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
    std::string dataDir = "data/cases";
    std::string outPath = "results/greedy_benchmark.csv";
};

struct Totals {
    long long cases = 0;
    long long invalidCases = 0;
    long long invalidSolutions = 0;
    long long infeasible = 0;
    long long cost1 = 0;
    long long cost2 = 0;
    long long wins1 = 0;
    long long wins2 = 0;
    long long ties = 0;
    double time1 = 0.0;
    double time2 = 0.0;
};

enum class Scale { Small = 0, Medium = 1, Large = 2 };

Scale scaleOf(int K) {
    if (K <= 15) {
        return Scale::Small;
    }
    if (K <= 80) {
        return Scale::Medium;
    }
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
              << " [--start 起始编号] [--count 案例数]"
                 " [--data-dir 案例目录] [--out 结果CSV]\n"
              << "示例: " << argv0 << " --start 0 --count 10000"
                 " --data-dir data/cases --out results/greedy_benchmark.csv\n";
}

enum class ParseStatus { Ok, Help, Error };

ParseStatus parseArgs(int argc, char** argv, Options& opt) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto needValue = [&](const char* name) -> const char* {
            if (i + 1 >= argc) {
                std::cerr << "参数 " << name << " 缺少取值\n";
                return nullptr;
            }
            return argv[++i];
        };

        if (arg == "--start") {
            const char* v = needValue("--start");
            if (!v) return ParseStatus::Error;
            opt.start = std::stoi(v);
        } else if (arg == "--count") {
            const char* v = needValue("--count");
            if (!v) return ParseStatus::Error;
            opt.count = std::stoi(v);
        } else if (arg == "--data-dir") {
            const char* v = needValue("--data-dir");
            if (!v) return ParseStatus::Error;
            opt.dataDir = v;
        } else if (arg == "--out") {
            const char* v = needValue("--out");
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
    if (opt.start < 0 || opt.count <= 0) {
        std::cerr << "start 必须 >= 0，count 必须 > 0\n";
        return ParseStatus::Error;
    }
    return ParseStatus::Ok;
}

void printTotals(const Totals& t) {
    const double gap = t.cost1 == 0
        ? 0.0
        : (static_cast<double>(t.cost2 - t.cost1) / t.cost1 * 100.0);
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "  案例数: " << t.cases
              << "，无效案例: " << t.invalidCases
              << "，非法解: " << t.invalidSolutions
              << "，不可行解: " << t.infeasible << "\n";
    std::cout << "  策略1 总目标值: " << t.cost1
              << "，总耗时: " << t.time1 << " ms\n";
    std::cout << "  策略2 总目标值: " << t.cost2
              << "，总耗时: " << t.time2 << " ms\n";
    std::cout << "  策略2 相对策略1 的目标值差: " << gap << " %\n";
    std::cout << "  策略1 胜/策略2 胜/持平: " << t.wins1 << " / "
              << t.wins2 << " / " << t.ties << "\n";
}

}  // namespace

int main(int argc, char** argv) {
    Options opt;
    const ParseStatus status = parseArgs(argc, argv, opt);
    if (status == ParseStatus::Help) {
        return 0;
    }
    if (status == ParseStatus::Error) {
        return 2;
    }

    const std::filesystem::path outPath(opt.outPath);
    if (!outPath.parent_path().empty()) {
        std::error_code ec;
        std::filesystem::create_directories(outPath.parent_path(), ec);
        if (ec) {
            std::cerr << "无法创建结果目录: " << outPath.parent_path()
                      << " (" << ec.message() << ")\n";
            return 1;
        }
    }

    std::ofstream out(outPath, std::ios::trunc);
    if (!out) {
        std::cerr << "无法写入结果文件: " << outPath << "\n";
        return 1;
    }
    out << "CaseId,N,M,K,Scale,"
           "Strategy1_Cost,Strategy1_Time(ms),Strategy1_Feasible,"
           "Strategy2_Cost,Strategy2_Time(ms),Strategy2_Feasible,Winner\n";

    Totals all;
    Totals byScale[3];
    auto addTotals = [](Totals& dst, const Totals& src) {
        dst.cases += src.cases;
        dst.invalidCases += src.invalidCases;
        dst.invalidSolutions += src.invalidSolutions;
        dst.infeasible += src.infeasible;
        dst.cost1 += src.cost1;
        dst.cost2 += src.cost2;
        dst.wins1 += src.wins1;
        dst.wins2 += src.wins2;
        dst.ties += src.ties;
        dst.time1 += src.time1;
        dst.time2 += src.time2;
    };

    std::cout << "开始测试两种贪心策略，共 " << opt.count << " 个案例...\n";
    for (int offset = 0; offset < opt.count; ++offset) {
        const int caseId = opt.start + offset;
        Case c;
        std::string loadErr;
        if (!loadCase(caseId, opt.dataDir, c, loadErr)) {
            std::cerr << "读取失败: " << loadErr << "\n";
            return 1;
        }

        Totals row;
        std::string caseErr;
        if (!validateCase(c, caseErr)) {
            ++row.invalidCases;
            std::cerr << "案例 " << caseId << " 不合法: " << caseErr << "\n";
        }

        GreedySolver g1(GreedyStrategy::ByPassengers);
        GreedySolver g2(GreedyStrategy::ByArrival);

        auto t1 = std::chrono::steady_clock::now();
        Solution s1 = g1.solve(c);
        auto t2 = std::chrono::steady_clock::now();
        s1.timeMs = std::chrono::duration<double, std::milli>(t2 - t1).count();

        auto t3 = std::chrono::steady_clock::now();
        Solution s2 = g2.solve(c);
        auto t4 = std::chrono::steady_clock::now();
        s2.timeMs = std::chrono::duration<double, std::milli>(t4 - t3).count();

        std::string err1;
        std::string err2;
        const bool valid1 = validateSolution(c, s1, err1);
        const bool valid2 = validateSolution(c, s2, err2);
        if (!valid1) {
            ++row.invalidSolutions;
            std::cerr << "案例 " << caseId << " 策略1 非法: " << err1 << "\n";
        }
        if (!valid2) {
            ++row.invalidSolutions;
            std::cerr << "案例 " << caseId << " 策略2 非法: " << err2 << "\n";
        }
        if (!s1.feasible || !valid1) ++row.infeasible;
        if (!s2.feasible || !valid2) ++row.infeasible;

        if (s1.feasible && s2.feasible) {
            if (s1.objective < s2.objective) {
                ++row.wins1;
            } else if (s2.objective < s1.objective) {
                ++row.wins2;
            } else {
                ++row.ties;
            }
        }

        row.cases = 1;
        row.cost1 = s1.objective;
        row.cost2 = s2.objective;
        row.time1 = s1.timeMs;
        row.time2 = s2.timeMs;

        const Scale scale = scaleOf(c.K);
        addTotals(all, row);
        addTotals(byScale[static_cast<int>(scale)], row);

        out << caseId << ',' << c.N << ',' << c.M << ',' << c.K << ','
            << scaleName(scale) << ','
            << s1.objective << ',' << std::fixed << std::setprecision(6)
            << s1.timeMs << ',' << (s1.feasible && valid1 ? 1 : 0) << ','
            << s2.objective << ',' << s2.timeMs << ','
            << (s2.feasible && valid2 ? 1 : 0) << ',';
        if (!s1.feasible || !s2.feasible) {
            out << "none";
        } else if (s1.objective < s2.objective) {
            out << "strategy1";
        } else if (s2.objective < s1.objective) {
            out << "strategy2";
        } else {
            out << "tie";
        }
        out << '\n';

        if ((offset + 1) % 1000 == 0) {
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
        const Totals& t = byScale[i];
        if (t.cases == 0) continue;
        std::cout << "\n[" << scaleName(static_cast<Scale>(i)) << "] 规模\n";
        printTotals(t);
    }
    std::cout << "\n详细结果: " << outPath << "\n";

    return (all.invalidCases == 0 && all.invalidSolutions == 0 &&
            all.infeasible == 0) ? 0 : 2;
}
