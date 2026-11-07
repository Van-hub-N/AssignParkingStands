#include "solver.h"

#include <algorithm>
#include <climits>
#include <map>
#include <numeric>

namespace {

// 用一个有序区间集合维护单个机位已占用的时间段。
// 由于飞机并不是按到达时间依次处理的，不能只记录最后一个离开时刻；
// 这里使用 map<到达, 离开>，每次用前驱/后继判断是否与新区间相交。
class StandTimeline {
public:
    bool available(int arrive, int depart) const {
        auto next = intervals_.lower_bound(arrive);
        if (next != intervals_.end() && next->first < depart) {
            return false;
        }
        if (next != intervals_.begin()) {
            auto prev = std::prev(next);
            if (prev->second > arrive) {
                return false;
            }
        }
        return true;
    }

    void add(int arrive, int depart) {
        intervals_.emplace(arrive, depart);
    }

private:
    std::map<int, int> intervals_;
};

}  // namespace

std::string GreedySolver::getName() const {
    if (strategy_ == GreedyStrategy::ByPassengers) {
        return "Greedy_ByPassengers";
    }
    return "Greedy_ByArrival";
}

Solution GreedySolver::solve(const Case& c) {
    Solution sol;
    sol.assign.assign(c.K, -1);

    if (c.K == 0) {
        sol.feasible = true;
        return sol;
    }

    std::vector<int> order(c.K);
    std::iota(order.begin(), order.end(), 0);

    // 两种策略的差别只在“处理飞机的顺序”上；每一步都采用相同的
    // “在可兼容且空闲的机位中选择下机时间最小者”的贪心选择。
    if (strategy_ == GreedyStrategy::ByPassengers) {
        std::stable_sort(order.begin(), order.end(), [&](int a, int b) {
            if (c.planes[a].passengers != c.planes[b].passengers) {
                return c.planes[a].passengers > c.planes[b].passengers;
            }
            // 只把乘客人数作为主排序键；同人数的飞机按编号稳定处理，
            // 避免隐式引入第二种策略的信息。
            return a < b;
        });
    } else {
        std::stable_sort(order.begin(), order.end(), [&](int a, int b) {
            if (c.planes[a].arrive != c.planes[b].arrive) {
                return c.planes[a].arrive < c.planes[b].arrive;
            }
            return a < b;
        });
    }

    const int standCount = c.N + c.M;
    std::vector<StandTimeline> timelines(standCount);

    for (int planeIndex : order) {
        const Plane& p = c.planes[planeIndex];
        int bestStand = -1;
        int bestUnload = INT_MAX;

        for (int s = 0; s < standCount; ++s) {
            const Stand& stand = c.stands[s];

            // 大飞机只能停大机位；小飞机可以停大机位或小机位。
            if (p.isLarge && !stand.isLarge) {
                continue;
            }
            if (!timelines[s].available(p.arrive, p.depart)) {
                continue;
            }

            if (stand.unloadTime < bestUnload ||
                (stand.unloadTime == bestUnload && s < bestStand)) {
                bestUnload = stand.unloadTime;
                bestStand = s;
            }
        }

        if (bestStand != -1) {
            sol.assign[planeIndex] = bestStand;
            timelines[bestStand].add(p.arrive, p.depart);
        }
    }

    sol.objective = calculateObjective(c, sol.assign);
    sol.feasible = std::all_of(sol.assign.begin(), sol.assign.end(),
                               [](int s) { return s != -1; });
    return sol;
}
