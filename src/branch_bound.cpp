#include "solver.h"

#include <algorithm>
#include <chrono>
#include <climits>
#include <map>
#include <numeric>
#include <set>
#include <vector>

namespace {

constexpr long long kInf = LLONG_MAX / 4;

// 单个机位的时间轴。查询、加入和回滚都在 O(log K) 内完成。
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

    void remove(int arrive) {
        intervals_.erase(arrive);
    }

private:
    std::map<int, int> intervals_;
};

struct Candidate {
    int stand = -1;
    int unloadTime = 0;
};

class BranchBoundSearch {
public:
    BranchBoundSearch(const Case& c, double timeLimitMs, long long nodeLimit)
        : c_(c),
          timeLimitMs_(timeLimitMs),
          nodeLimit_(nodeLimit),
          order_(c.K),
          minUnload_(c.K, kInf),
          suffixLowerBound_(c.K + 1, 0),
          candidates_(c.K),
          removedAtDepth_(c.K),
          timelines_(c.stands.size()),
          current_(c.K, -1),
          dynamicBoundEnabled_(c.K <= 15) {
        start_ = std::chrono::steady_clock::now();
    }

    Solution run() {
        Solution result;
        result.assign.assign(c_.K, -1);

        if (c_.K == 0) {
            result.feasible = true;
            result.complete = true;
            return result;
        }

        prepareOrderAndBounds();

        // 分支限界从两个贪心解中取较优者作为初始上界。它保证算法在
        // 任何时候中断都能返回一个可行解，而且上界越紧，剪枝越早生效。
        GreedySolver byPassengers(GreedyStrategy::ByPassengers);
        GreedySolver byArrival(GreedyStrategy::ByArrival);
        considerIncumbent(byPassengers.solve(c_));
        considerIncumbent(byArrival.solve(c_));

        if (dynamicBoundEnabled_) {
            initializeDynamicBound();
        }

        const long long rootBound =
            dynamicBoundEnabled_ ? dynamicSum_ : suffixLowerBound_[0];
        if (bestCost_ < kInf && rootBound >= bestCost_) {
            return makeResult(true);
        }

        if (timeLimitMs_ > 0 && elapsedMs() >= timeLimitMs_) {
            timeLimitReached_ = true;
            return makeResult(false);
        }

        dfs(0, 0);
        return makeResult(!timeLimitReached_ && !nodeLimitReached_);
    }

private:
    void prepareOrderAndBounds() {
        std::vector<int> compatibleCount(c_.K, 0);

        for (int i = 0; i < c_.K; ++i) {
            const Plane& p = c_.planes[i];
            for (const Stand& s : c_.stands) {
                if (p.isLarge && !s.isLarge) {
                    continue;
                }
                ++compatibleCount[i];
                minUnload_[i] = std::min<long long>(minUnload_[i], s.unloadTime);
            }
        }

        std::iota(order_.begin(), order_.end(), 0);
        std::stable_sort(order_.begin(), order_.end(), [&](int a, int b) {
            const Plane& pa = c_.planes[a];
            const Plane& pb = c_.planes[b];

            // 大飞机可选机位少，优先安排；其余按候选数和乘客数排序。
            if (pa.isLarge != pb.isLarge) {
                return pa.isLarge;
            }
            if (compatibleCount[a] != compatibleCount[b]) {
                return compatibleCount[a] < compatibleCount[b];
            }
            if (pa.passengers != pb.passengers) {
                return pa.passengers > pb.passengers;
            }
            return a < b;
        });

        // 静态后缀下界：每架剩余飞机独立选择兼容机位中下机时间最小者，
        // 忽略时间冲突。它是动态下界不可用时的安全退化。
        for (int d = c_.K - 1; d >= 0; --d) {
            const int plane = order_[d];
            const long long contribution =
                minUnload_[plane] >= kInf
                    ? kInf
                    : static_cast<long long>(c_.planes[plane].passengers) *
                          minUnload_[plane];
            if (suffixLowerBound_[d + 1] >= kInf || contribution >= kInf) {
                suffixLowerBound_[d] = kInf;
            } else {
                suffixLowerBound_[d] = suffixLowerBound_[d + 1] + contribution;
            }
        }
    }

    void considerIncumbent(const Solution& sol) {
        if (!sol.feasible || sol.assign.size() != static_cast<std::size_t>(c_.K)) {
            return;
        }
        std::string err;
        if (!validateSolution(c_, sol, err)) {
            return;
        }
        if (sol.objective < bestCost_) {
            bestCost_ = sol.objective;
            bestAssign_ = sol.assign;
        }
    }

    void initializeDynamicBound() {
        availableUnloads_.resize(c_.K);
        for (int i = 0; i < c_.K; ++i) {
            const Plane& plane = c_.planes[i];
            for (int s = 0; s < static_cast<int>(c_.stands.size()); ++s) {
                if (!compatible(i, s)) {
                    continue;
                }
                availableUnloads_[i].insert({c_.stands[s].unloadTime, s});
            }
            if (availableUnloads_[i].empty()) {
                ++emptyAvailable_;
            } else {
                dynamicSum_ +=
                    static_cast<long long>(plane.passengers) *
                    availableUnloads_[i].begin()->first;
            }
        }
    }

    bool compatible(int planeIndex, int standIndex) const {
        return !c_.planes[planeIndex].isLarge ||
               c_.stands[standIndex].isLarge;
    }

    bool overlaps(int a, int b) const {
        const Plane& pa = c_.planes[a];
        const Plane& pb = c_.planes[b];
        return pa.arrive < pb.depart && pb.arrive < pa.depart;
    }

    void eraseAvailable(int planeIndex, int standIndex) {
        auto& values = availableUnloads_[planeIndex];
        const auto key = std::make_pair(c_.stands[standIndex].unloadTime, standIndex);
        auto it = values.find(key);
        if (it == values.end()) {
            return;
        }

        const long long weight = c_.planes[planeIndex].passengers;
        const bool wasEmpty = values.empty();
        const int oldMin = wasEmpty ? 0 : values.begin()->first;
        values.erase(it);

        if (values.empty()) {
            // 该剩余飞机已经没有任何可用机位，当前分支不可能完成。
            if (!wasEmpty) {
                dynamicSum_ -= weight * oldMin;
            }
            ++emptyAvailable_;
            return;
        }

        const int newMin = values.begin()->first;
        dynamicSum_ += weight * (newMin - oldMin);
    }

    void insertAvailable(int planeIndex, int standIndex) {
        auto& values = availableUnloads_[planeIndex];
        const long long weight = c_.planes[planeIndex].passengers;
        const bool wasEmpty = values.empty();
        const int oldMin = wasEmpty ? 0 : values.begin()->first;
        values.insert({c_.stands[standIndex].unloadTime, standIndex});

        if (wasEmpty) {
            --emptyAvailable_;
            dynamicSum_ += weight * values.begin()->first;
            return;
        }

        const int newMin = values.begin()->first;
        dynamicSum_ += weight * (newMin - oldMin);
    }

    double elapsedMs() const {
        const auto now = std::chrono::steady_clock::now();
        return std::chrono::duration<double, std::milli>(now - start_).count();
    }

    bool stopRequested() {
        if (nodeLimit_ > 0 && nodes_ >= nodeLimit_) {
            nodeLimitReached_ = true;
            return true;
        }
        if (timeLimitMs_ > 0 && (nodes_ & 1023LL) == 0 &&
            elapsedMs() >= timeLimitMs_) {
            timeLimitReached_ = true;
            return true;
        }
        return false;
    }

    void dfs(int depth, long long cost) {
        ++nodes_;
        if (stopRequested()) {
            return;
        }

        if (depth == c_.K) {
            if (cost < bestCost_) {
                bestCost_ = cost;
                bestAssign_ = current_;
            }
            return;
        }

        // 当前代价已经不能严格改进全局上界。
        if (bestCost_ < kInf && cost >= bestCost_) {
            return;
        }

        const long long lower =
            dynamicBoundEnabled_ ? dynamicSum_ : suffixLowerBound_[depth];
        if (lower >= kInf ||
            (bestCost_ < kInf && cost + lower >= bestCost_)) {
            return;
        }

        // 若动态集合中出现空集，后续一定存在无法安排的飞机。
        if (dynamicBoundEnabled_ && emptyAvailable_ > 0) {
            return;
        }

        const int planeIndex = order_[depth];
        const Plane& plane = c_.planes[planeIndex];

        auto& candidates = candidates_[depth];
        candidates.clear();
        for (int s = 0; s < static_cast<int>(c_.stands.size()); ++s) {
            const Stand& stand = c_.stands[s];
            if (!compatible(planeIndex, s)) {
                continue;
            }
            if (!timelines_[s].available(plane.arrive, plane.depart)) {
                continue;
            }
            candidates.push_back({s, stand.unloadTime});
        }

        std::sort(candidates.begin(), candidates.end(),
                  [](const Candidate& a, const Candidate& b) {
                      if (a.unloadTime != b.unloadTime) {
                          return a.unloadTime < b.unloadTime;
                      }
                      return a.stand < b.stand;
                  });

        for (const Candidate& candidate : candidates) {
            const int standIndex = candidate.stand;
            const long long contribution =
                static_cast<long long>(plane.passengers) * candidate.unloadTime;

            long long currentContribution = 0;
            auto& removed = removedAtDepth_[depth];
            removed.clear();

            if (dynamicBoundEnabled_) {
                // 当前飞机将从“剩余飞机”变为已分配飞机，先把它自己的
                // 最小贡献从动态下界中移除。
                const auto& currentValues = availableUnloads_[planeIndex];
                if (!currentValues.empty()) {
                    currentContribution =
                        static_cast<long long>(plane.passengers) *
                        currentValues.begin()->first;
                    dynamicSum_ -= currentContribution;
                }

                // 当前飞机占用该机位后，所有与它时间重叠的剩余飞机都不能
                // 再使用这个机位；同步更新它们的可用下机时间集合。
                for (int q = depth + 1; q < c_.K; ++q) {
                    const int other = order_[q];
                    if (!compatible(other, standIndex) ||
                        !overlaps(other, planeIndex)) {
                        continue;
                    }
                    auto& values = availableUnloads_[other];
                    auto it = values.find(
                        {candidate.unloadTime, standIndex});
                    if (it == values.end()) {
                        continue;
                    }
                    eraseAvailable(other, standIndex);
                    removed.push_back({other, standIndex});
                }
            }

            current_[planeIndex] = standIndex;
            timelines_[standIndex].add(plane.arrive, plane.depart);
            dfs(depth + 1, cost + contribution);
            timelines_[standIndex].remove(plane.arrive);
            current_[planeIndex] = -1;

            if (dynamicBoundEnabled_) {
                for (auto it = removed.rbegin(); it != removed.rend(); ++it) {
                    insertAvailable(it->first, it->second);
                }
                dynamicSum_ += currentContribution;
            }

            if (timeLimitReached_ || nodeLimitReached_) {
                return;
            }
        }
    }

    Solution makeResult(bool complete) {
        Solution result;
        result.assign = bestAssign_;
        result.objective = bestCost_ < kInf ? bestCost_ : 0;
        result.feasible =
            bestCost_ < kInf &&
            result.assign.size() == static_cast<std::size_t>(c_.K) &&
            std::all_of(result.assign.begin(), result.assign.end(),
                        [](int s) { return s != -1; });
        result.complete = complete;
        result.timeLimitReached = timeLimitReached_;
        result.nodeLimitReached = nodeLimitReached_;
        result.nodesExpanded = nodes_;
        result.timeMs = elapsedMs();
        return result;
    }

    const Case& c_;
    double timeLimitMs_;
    long long nodeLimit_;

    std::vector<int> order_;
    std::vector<long long> minUnload_;
    std::vector<long long> suffixLowerBound_;
    std::vector<std::vector<Candidate>> candidates_;
    std::vector<std::vector<std::pair<int, int>>> removedAtDepth_;  // (plane, stand)
    std::vector<StandTimeline> timelines_;
    std::vector<int> current_;

    std::vector<int> bestAssign_;
    long long bestCost_ = kInf;
    long long nodes_ = 0;
    bool timeLimitReached_ = false;
    bool nodeLimitReached_ = false;

    // 动态下界：为每架尚未分配的飞机维护“当前仍可用的机位下机时间”集合。
    // 集合非空时，所有剩余飞机独立取最小值的和一定是任何完整分配的下界。
    bool dynamicBoundEnabled_ = false;
    std::vector<std::multiset<std::pair<int, int>>> availableUnloads_;  // (unload, stand)
    long long dynamicSum_ = 0;
    int emptyAvailable_ = 0;

    std::chrono::steady_clock::time_point start_;
};

}  // namespace

Solution BranchBoundSolver::solve(const Case& c) {
    BranchBoundSearch search(c, timeLimitMs_, nodeLimit_);
    return search.run();
}
