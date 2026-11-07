#include "case.h"
#include "io.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <tuple>
#include <vector>

namespace {

using Combo = std::tuple<int, int, int>;  // N, M, K

// 生成 100 种不同的 (N, M, K) 组合：
//   小规模 30 组：N=1..5，K=5..15
//   中规模 40 组：N=5..20，K=20..80
//   大规模 30 组：N=20..50，K=100..500
// 每组 M 均不小于 K，保证远端机位数量足够，案例一定存在可行分配。
std::vector<Combo> makeCombos() {
    std::vector<Combo> combos;
    combos.reserve(100);
    std::mt19937 rng(12345);

    for (int i = 0; i < 30; ++i) {
        const int N = rng() % 5 + 1;
        const int K = rng() % 11 + 5;
        const int M = K + (rng() % 10);
        combos.emplace_back(N, M, K);
    }
    for (int i = 0; i < 40; ++i) {
        const int N = rng() % 16 + 5;
        const int K = rng() % 61 + 20;
        const int M = K + (rng() % 20);
        combos.emplace_back(N, M, K);
    }
    for (int i = 0; i < 30; ++i) {
        const int N = rng() % 31 + 20;
        const int K = rng() % 401 + 100;
        const int M = K + (rng() % 50);
        combos.emplace_back(N, M, K);
    }
    return combos;
}

Case generateCase(int caseId, int N, int M, int K) {
    // 固定种子保证任何一个案例都可以由 (caseId) 独立复现。
    std::mt19937 rng(20260000u + static_cast<unsigned>(caseId));

    Case c;
    c.caseId = caseId;
    c.N = N;
    c.M = M;
    c.K = K;

    // 靠桥机位：下机时间 [10, 30]，大小随机。
    std::uniform_int_distribution<int> bridgeTime(10, 30);
    for (int i = 0; i < N; ++i) {
        c.stands.push_back({i, true, (rng() % 2 == 0), bridgeTime(rng)});
    }

    // 远端机位：全为大机位，下机时间 [35, 60]，严格大于靠桥机位。
    std::uniform_int_distribution<int> remoteTime(35, 60);
    for (int i = 0; i < M; ++i) {
        c.stands.push_back({N + i, false, true, remoteTime(rng)});
    }

    // 飞机：一天按 1440 分钟计，到达限制在 [0, 1200]，
    // 停靠时长 30..180 分钟，乘客人数 20..300，40% 为大飞机。
    std::uniform_int_distribution<int> arr(0, 1200);
    std::uniform_int_distribution<int> dur(30, 180);
    std::uniform_int_distribution<int> pax(20, 300);
    for (int i = 0; i < K; ++i) {
        Plane p;
        p.id = i;
        p.arrive = arr(rng);
        p.depart = p.arrive + dur(rng);
        p.isLarge = (rng() % 100 < 40);
        p.passengers = pax(rng);
        c.planes.push_back(p);
    }
    return c;
}

void printUsage(const char* argv0) {
    std::cout << "用法: " << argv0 << " [--out-dir 目录]\n"
              << "  默认输出到 data/，生成 data/combos.csv 和 data/cases/*.bin\n";
}

}  // namespace

int main(int argc, char** argv) {
    std::string outDir = "data";
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--out-dir" && i + 1 < argc) {
            outDir = argv[++i];
        } else if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            return 0;
        } else {
            std::cerr << "未知参数: " << arg << "\n";
            printUsage(argv[0]);
            return 2;
        }
    }

    const std::filesystem::path root(outDir);
    const std::filesystem::path casesDir = root / "cases";
    std::error_code ec;
    std::filesystem::create_directories(casesDir, ec);
    if (ec) {
        std::cerr << "无法创建目录: " << casesDir << " (" << ec.message() << ")\n";
        return 1;
    }

    std::ofstream meta(root / "combos.csv", std::ios::trunc);
    if (!meta) {
        std::cerr << "无法创建 " << (root / "combos.csv") << "\n";
        return 1;
    }
    meta << "comboId,N,M,K\n";

    const std::vector<Combo> combos = makeCombos();
    int generated = 0;
    for (int comboId = 0; comboId < static_cast<int>(combos.size()); ++comboId) {
        const auto [N, M, K] = combos[comboId];
        meta << comboId << ',' << N << ',' << M << ',' << K << '\n';

        for (int j = 0; j < 100; ++j) {
            const int caseId = comboId * 100 + j;
            const Case c = generateCase(caseId, N, M, K);

            std::string err;
            if (!validateCase(c, err)) {
                std::cerr << "案例 " << caseId << " 校验失败: " << err << "\n";
                return 1;
            }

            const std::string path =
                (casesDir / ("case_" + pad5(caseId) + ".bin")).string();
            if (!saveCase(c, path)) {
                std::cerr << "写入案例失败: " << path << "\n";
                return 1;
            }
            ++generated;
        }

        if (comboId % 10 == 0) {
            std::cout << "已处理 " << comboId << " / 100 组参数，累计生成 "
                      << generated << " 个案例\n";
        }
    }

    std::cout << "生成完成: " << generated << " 个案例，输出目录 " << root << "\n";
    std::cout << "参数表: " << (root / "combos.csv") << "\n";
    return 0;
}
