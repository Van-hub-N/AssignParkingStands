#include "solver.h"
#include <algorithm>

// 判断时间段是否冲突
bool isStandAvailable(const std::vector<std::pair<int, int>>& schedules, int arrive, int depart) {
    for (const auto& interval : schedules) {
        // 有交集则冲突
        if (std::max(arrive, interval.first) < std::min(depart, interval.second)) {
            return false;
        }
    }
    return true;
}

// 计算总下机时间
long long calculateObjective(const Case& c, const std::vector<int>& assign) {
    long long total = 0;
    for (int i = 0; i < c.K; ++i) {
        if (assign[i] != -1) {
            total += (long long)c.planes[i].passengers * c.stands[assign[i]].unloadTime;
        }
    }
    return total;
}

// 校验解是否合法
bool validateSolution(const Case& c, const Solution& sol, std::string& err) {
    if (sol.assign.size() != (size_t)c.K) { err = "分配数组大小错误"; return false; }
    
    std::vector<std::vector<std::pair<int, int>>> schedules(c.N + c.M);
    for (int i = 0; i < c.K; ++i) {
        int s = sol.assign[i];
        if (s < 0 || s >= c.N + c.M) { err = "机位编号越界"; return false; }
        
        const auto& p = c.planes[i];
        const auto& stand = c.stands[s];
        
        if (p.isLarge && !stand.isLarge) { err = "大飞机被分配到了小机位"; return false; }
        
        if (!isStandAvailable(schedules[s], p.arrive, p.depart)) {
            err = "飞机 " + std::to_string(i) + " 在机位 " + std::to_string(s) + " 发生时间冲突";
            return false;
        }
        schedules[s].push_back({p.arrive, p.depart});
    }
    return true;
}
