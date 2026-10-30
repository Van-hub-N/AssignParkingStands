#include "case.h"
#include "io.h"
#include <iostream>
#include <fstream>
#include <random>
#include <vector>
#include <tuple>
#include <string>
#include <iomanip>



// 生成 100 种 (N, M, K) 组合
std::vector<std::tuple<int,int,int>> makeCombos() {
    std::vector<std::tuple<int,int,int>> combos;
    std::mt19937 rng(12345); 

    // 小规模 30 组：N 1~5, K 5~15
    for (int i = 0; i < 30; ++i) {
        int N = rng() % 5 + 1;
        int K = rng() % 11 + 5;
        int M = K + (rng() % 10); // 保证 M >= K，且多出 0~9 个冗余远端机位
        combos.push_back({N, M, K});
    }
    // 中规模 40 组：N 5~20, K 20~80
    for (int i = 0; i < 40; ++i) {
        int N = rng() % 16 + 5;
        int K = rng() % 61 + 20;
        int M = K + (rng() % 20); // 保证 M >= K
        combos.push_back({N, M, K});
    }
    // 大规模 30 组：N 20~50, K 100~500
    for (int i = 0; i < 30; ++i) {
        int N = rng() % 31 + 20;
        int K = rng() % 401 + 100;
        int M = K + (rng() % 50); // 保证 M >= K
        combos.push_back({N, M, K});
    }

    return combos;
}

Case generateCase(int caseId, int N, int M, int K) {
    std::mt19937 rng(20260000u + caseId);
    Case c;
    c.caseId = caseId; c.N = N; c.M = M; c.K = K;

    // 1. 靠桥机位：下机时间 [10, 30] 分钟，大小随机
    std::uniform_int_distribution<int> bridgeTime(10, 30);
    for (int i = 0; i < N; ++i) {
        c.stands.push_back({i, true, (rng() % 2 == 0), bridgeTime(rng)});
    }

    // 2. 远端机位：全大机位，下机时间 [35, 60] 分钟（区间不重叠，严格大于靠桥）
    std::uniform_int_distribution<int> remoteTime(35, 60);
    for (int i = 0; i < M; ++i) {
        c.stands.push_back({N + i, false, true, remoteTime(rng)});
    }

    // 3. 飞机停靠时间段与人数随机生成
    // 假设一天 1440 分钟，为了不让飞机跨天，到达时间限制在 [0, 1200]
    std::uniform_int_distribution<int> arr(0, 1200); 
    std::uniform_int_distribution<int> dur(30, 180); // 停靠时长 30 分钟到 3 小时
    std::uniform_int_distribution<int> pax(20, 300); // 乘客人数 20 到 300

    for (int i = 0; i < K; ++i) {
        Plane p;
        p.id = i;
        p.arrive = arr(rng);
        p.depart = p.arrive + dur(rng); 
        p.isLarge = (rng() % 100 < 40); // 40% 概率为大飞机
        p.passengers = pax(rng);
        c.planes.push_back(p);
    }
    return c;
}

int main() {
    std::vector<std::tuple<int,int,int>> combos = makeCombos();
    
    std::ofstream meta("../data/combos.csv");
    if (!meta) { std::cerr << "无法创建 data/combos.csv，请确保目录存在\n"; return 1; }
    meta << "comboId,N,M,K\n";

    for (int comboId = 0; comboId < 100; ++comboId) {
        auto [N, M, K] = combos[comboId];
        meta << comboId << "," << N << "," << M << "," << K << "\n";
        
        for (int j = 0; j < 100; ++j) {
            int caseId = comboId * 100 + j;

            Case c = generateCase(caseId, N, M, K);
            
            std::string err;
            if (!validateCase(c, err)) {
                std::cerr << "案例 " << caseId << " 校验失败: " << err << "\n";
                return 1;
            }
            
            saveCase(c, "../data/cases/case_" + pad5(caseId) + ".bin");
        }
        if (comboId % 10 == 0) {
            std::cout << "已生成 " << comboId * 100 << " 个案例...\n";
        }
    }
    std::cout << "成功生成 10000 个案例！\n";
    return 0;
}
