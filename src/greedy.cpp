#include "solver.h"
#include <algorithm>
#include <climits>
#include <iostream>

// 实现 GreedySolver 的 solve 方法
Solution GreedySolver::solve(const Case& c) {
    Solution sol;
    sol.assign.resize(c.K, -1);
    
    // 记录每个机位已经被占用的时间段
    std::vector<std::vector<std::pair<int, int>>> schedules(c.N + c.M);
    
    std::vector<int> pIdx(c.K);
    for (int i = 0; i < c.K; ++i) pIdx[i] = i;

    // 排序策略
    if (strategyType == 1) {
        std::sort(pIdx.begin(), pIdx.end(), [&](int a, int b) {
            return c.planes[a].passengers > c.planes[b].passengers;
        });
    } else {
        std::sort(pIdx.begin(), pIdx.end(), [&](int a, int b) {
            return c.planes[a].arrive < c.planes[b].arrive;
        });
    }

    // 分配
    for (int i : pIdx) {
        const auto& p = c.planes[i];
        int bestStand = -1;
        int minUnloadTime = INT_MAX;
        
        for (int s = 0; s < c.N + c.M; ++s) {
            const auto& stand = c.stands[s];
            if (p.isLarge && !stand.isLarge) continue;
            if (!isStandAvailable(schedules[s], p.arrive, p.depart)) continue;
            
            if (stand.unloadTime < minUnloadTime) {
                minUnloadTime = stand.unloadTime;
                bestStand = s;
            }
        }
        
        if (bestStand != -1) {
            sol.assign[i] = bestStand;
            schedules[bestStand].push_back({p.arrive, p.depart});
        }
    }
    
    // 计算总成本
    sol.objective = calculateObjective(c, sol.assign);
    sol.feasible = true;
    return sol;
}
