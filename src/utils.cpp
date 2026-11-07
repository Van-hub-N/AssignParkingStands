#include "solver.h"

#include <algorithm>
#include <map>

bool isStandAvailable(const std::vector<std::pair<int, int>>& schedules,
                      int arrive, int depart) {
    for (const auto& interval : schedules) {
        // 半开区间 [arrive, depart) 有交集则冲突；前一架离开时刻
        // 等于后一架到达时刻是允许的。
        if (std::max(arrive, interval.first) < std::min(depart, interval.second)) {
            return false;
        }
    }
    return true;
}

long long calculateObjective(const Case& c, const std::vector<int>& assign) {
    long long total = 0;
    const int standCount = c.N + c.M;
    const int n = std::min(static_cast<int>(assign.size()), c.K);
    for (int i = 0; i < n; ++i) {
        const int s = assign[i];
        if (s < 0 || s >= standCount) {
            continue;
        }
        total += static_cast<long long>(c.planes[i].passengers) *
                 c.stands[s].unloadTime;
    }
    return total;
}

bool validateSolution(const Case& c, const Solution& sol, std::string& err) {
    if (sol.assign.size() != static_cast<std::size_t>(c.K)) {
        err = "分配数组大小错误";
        return false;
    }
    if (c.stands.size() != static_cast<std::size_t>(c.N + c.M)) {
        err = "案例机位数量不一致";
        return false;
    }

    const int standCount = c.N + c.M;
    std::vector<std::map<int, int>> timelines(standCount);

    for (int i = 0; i < c.K; ++i) {
        const int s = sol.assign[i];
        if (s < 0 || s >= standCount) {
            err = "飞机 " + std::to_string(i) + " 未分配或机位编号越界";
            return false;
        }

        const Plane& p = c.planes[i];
        const Stand& stand = c.stands[s];
        if (p.isLarge && !stand.isLarge) {
            err = "飞机 " + std::to_string(i) + " 为大飞机，却分配到小机位";
            return false;
        }

        // 用有序区间表检查冲突，复杂度 O(log n)。
        auto& intervals = timelines[s];
        auto next = intervals.lower_bound(p.arrive);
        bool conflict = false;
        if (next != intervals.end() && next->first < p.depart) {
            conflict = true;
        }
        if (next != intervals.begin()) {
            auto prev = std::prev(next);
            if (prev->second > p.arrive) {
                conflict = true;
            }
        }
        if (conflict) {
            err = "飞机 " + std::to_string(i) + " 在机位 " +
                  std::to_string(s) + " 发生时间冲突";
            return false;
        }
        intervals.emplace(p.arrive, p.depart);
    }
    return true;
}
