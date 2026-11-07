#include "solver.h"

#include <algorithm>
#include <chrono>
#include <climits>
#include <map>
#include <numeric>
#include <vector>

namespace {

constexpr long long kInf = LLONG_MAX / 4;

// 单个机位的时间轴。查询和回滚都在 O(log K) 内完成。
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

class BacktrackingSearch {
public:
    BacktrackingSearch(const Case& c, double timeLimitMs, long long nodeLimit)
        : c_(c),
          timeLimitMs_(timeLimitMs),
          nodeLimit_(nodeLimit),
          order_(c.K),
          minUnload_(c.K, kInf),
          suffixLowerBound_(c.K + 1, 0),
          candidates_(c.K),
          timelines_(c.N + c.M),
          current_(c.K, -1) {
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

        // 用乘客优先贪心解作为初始上界，既能快速得到可行解，也能让
        // 下界剪枝尽早生效。
        GreedySolver greedy(GreedyStrategy::ByPassengers);
        const Solution incumbent = greedy.solve(c_);
        if (incumbent.feasible && validateSolution(c_, incumbent, dummyErr_)) {
            bestCost_ = incumbent.objective;
            bestAssign_ = incumbent.assign;
        }

        // 若连根节点的下界都不优于当前上界，则无需展开搜索，
        // 当前贪心解已经可以证明最优。
        if (bestCost_ < kInf && suffixLowerBound_[0] >= bestCost_) {
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

            // 大飞机可选的机位更少，优先安排以尽早暴露不可行分支。
            if (pa.isLarge != pb.isLarge) {
                return pa.isLarge;
            }
            // 可选机位越少越先安排。
            if (compatibleCount[a] != compatibleCount[b]) {
                return compatibleCount[a] < compatibleCount[b];
            }
            // 目标权重越大越先安排，便于尽早找到好的可行解。
            if (pa.passengers != pb.passengers) {
                return pa.passengers > pb.passengers;
            }
            return a < b;
        });

        // suffixLowerBound_[d] 是 order_[d..K-1] 的一个宽松下界：
        // 每架飞机都独立选择兼容机位中最小的下机时间，忽略时间冲突。
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

        if (bestCost_ < kInf && cost >= bestCost_) {
            return;
        }
        const long long lower = suffixLowerBound_[depth];
        if (bestCost_ < kInf && lower < kInf && cost + lower >= bestCost_) {
            return;
        }

        const int planeIndex = order_[depth];
        const Plane& plane = c_.planes[planeIndex];

        auto& candidates = candidates_[depth];
        candidates.clear();
        for (int s = 0; s < static_cast<int>(c_.stands.size()); ++s) {
            const Stand& stand = c_.stands[s];
            if (plane.isLarge && !stand.isLarge) {
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
            current_[planeIndex] = candidate.stand;
            timelines_[candidate.stand].add(plane.arrive, plane.depart);
            dfs(depth + 1,
                cost + static_cast<long long>(plane.passengers) *
                           candidate.unloadTime);
            timelines_[candidate.stand].remove(plane.arrive);
            current_[planeIndex] = -1;

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
            bestCost_ < kInf && result.assign.size() == static_cast<std::size_t>(c_.K) &&
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
    std::vector<StandTimeline> timelines_;
    std::vector<int> current_;

    std::vector<int> bestAssign_;
    long long bestCost_ = kInf;
    long long nodes_ = 0;
    bool timeLimitReached_ = false;
    bool nodeLimitReached_ = false;
    std::string dummyErr_;

    std::chrono::steady_clock::time_point start_;
};

}  // namespace

Solution BacktrackingSolver::solve(const Case& c) {
    BacktrackingSearch search(c, timeLimitMs_, nodeLimit_);
    return search.run();
}
