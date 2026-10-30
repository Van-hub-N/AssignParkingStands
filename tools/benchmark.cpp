#include "io.h"
#include "solver.h"
#include <iostream>
#include <chrono>
#include <fstream>

int main() {
    // 打开一个 CSV 文件用来记录实验结果
    std::ofstream out("greedy_benchmark_results.csv");
    out << "CaseId,N,M,K,Strategy1_Cost,Strategy1_Time(ms),Strategy2_Cost,Strategy2_Time(ms)\n";

    // 为了节省时间，这里可以先测试前 100 个案例，全测可以改成 10000
    int totalCases = 10000; 
    long long totalCost1 = 0, totalCost2 = 0;
    double totalTime1 = 0, totalTime2 = 0;

    std::cout << "开始测试贪心算法...\n";

    for (int caseId = 0; caseId < totalCases; ++caseId) {
        Case c = loadCase(caseId);
        if (c.K == 0) {
            std::cerr << "案例读取失败，跳过: " << caseId << "\n";
            continue;
        }

        // 实例化两种贪心策略
        GreedySolver greedy1(1); // 策略1：乘客优先
        GreedySolver greedy2(2); // 策略2：到达时间优先

        // --- 测试策略 1 ---
        auto start1 = std::chrono::high_resolution_clock::now();
        Solution sol1 = greedy1.solve(c);
        auto end1 = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> time1 = end1 - start1;
        
        // 校验结果是否合法
        std::string err1;
        if (!validateSolution(c, sol1, err1)) {
            std::cerr << "策略1 结果非法 (Case " << caseId << "): " << err1 << "\n";
        }

        // --- 测试策略 2 ---
        auto start2 = std::chrono::high_resolution_clock::now();
        Solution sol2 = greedy2.solve(c);
        auto end2 = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> time2 = end2 - start2;

        std::string err2;
        if (!validateSolution(c, sol2, err2)) {
            std::cerr << "策略2 结果非法 (Case " << caseId << "): " << err2 << "\n";
        }

        // 记录数据
        out << caseId << "," << c.N << "," << c.M << "," << c.K << ","
            << sol1.objective << "," << time1.count() << ","
            << sol2.objective << "," << time2.count() << "\n";

        totalCost1 += sol1.objective;
        totalCost2 += sol2.objective;
        totalTime1 += time1.count();
        totalTime2 += time2.count();

        // 每 1000 个案例打印一次进度
        if ((caseId + 1) % 1000 == 0) {
            std::cout << "已处理 " << (caseId + 1) << " 个案例...\n";
        }
    }

    std::cout << "\n===== 测试结果汇总 =====\n";
    std::cout << "策略1 (乘客优先): 总成本 = " << totalCost1 << " | 总耗时 = " << totalTime1 << " ms\n";
    std::cout << "策略2 (到达优先): 总成本 = " << totalCost2 << " | 总耗时 = " << totalTime2 << " ms\n";
    std::cout << "详细结果已保存到 greedy_benchmark_results.csv\n";

    return 0;
}
