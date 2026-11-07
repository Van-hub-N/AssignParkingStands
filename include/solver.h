#pragma once

#include "case.h"

#include <string>
#include <vector>

// 两种贪心排序策略。
enum class GreedyStrategy {
    ByPassengers = 1,   // 乘客人数从多到少
    ByArrival = 2       // 到达时刻从早到晚
};

// 统一的算法结果。
struct Solution {
    std::vector<int> assign;      // assign[i] = 飞机 i 的机位 id，-1 表示未分配
    long long objective = 0;      // 目标值：所有已分配乘客的下机时间之和（人·分钟）
    bool feasible = false;        // 是否所有飞机都得到了合法分配
    bool complete = false;        // 搜索空间是否被完整枚举（即是否已证明最优）
    bool timeLimitReached = false;
    bool nodeLimitReached = false;
    double timeMs = 0.0;          // 求解耗时（毫秒）
    long long nodesExpanded = 0;  // 搜索节点数；贪心算法不使用
};

// 算法统一接口，便于后续实验继续扩展回溯法、分支限界法和启发式算法。
class Solver {
public:
    virtual ~Solver() = default;
    virtual std::string getName() const = 0;
    virtual Solution solve(const Case& c) = 0;
};

// 贪心求解器：按指定顺序逐架飞机选择当前可用的、下机时间最小的机位。
class GreedySolver : public Solver {
public:
    explicit GreedySolver(GreedyStrategy strategy) : strategy_(strategy) {}

    std::string getName() const override;
    Solution solve(const Case& c) override;

private:
    GreedyStrategy strategy_;
};

// 回溯求解器：按“机型受限程度 + 乘客人数”排序飞机，深度优先枚举机位，
// 使用贪心解作为初始上界，并用剩余飞机的最小可能下机时间做剪枝。
// 为应对指数级搜索空间，可设置时间上限和结点上限；触发上限时返回当前最好解，
// 并通过 Solution::complete 标记是否已经完成全搜索（即是否证明最优）。
class BacktrackingSolver : public Solver {
public:
    explicit BacktrackingSolver(double timeLimitMs = 2000.0,
                                long long nodeLimit = 5000000)
        : timeLimitMs_(timeLimitMs), nodeLimit_(nodeLimit) {}

    std::string getName() const override { return "Backtracking"; }
    Solution solve(const Case& c) override;

private:
    double timeLimitMs_;
    long long nodeLimit_;
};

// 分支限界求解器：在深度优先分支框架上维护全局上界，并用“当前可用机位”
// 动态下界和剩余飞机前向检查剪枝。与回溯法相比，它更强调用上界/下界
// 证明最优性，而不是只枚举可行分配；达到时间或结点上限时返回当前最好解。
class BranchBoundSolver : public Solver {
public:
    explicit BranchBoundSolver(double timeLimitMs = 2000.0,
                               long long nodeLimit = 5000000)
        : timeLimitMs_(timeLimitMs), nodeLimit_(nodeLimit) {}

    std::string getName() const override { return "BranchAndBound"; }
    Solution solve(const Case& c) override;

private:
    double timeLimitMs_;
    long long nodeLimit_;
};

// 计算分配方案的目标值；非法的 -1 分配不计入目标值。
long long calculateObjective(const Case& c, const std::vector<int>& assign);

// 校验分配方案：数量、越界、机型匹配、时间冲突。
bool validateSolution(const Case& c, const Solution& sol, std::string& err);

// 判断一个已经排好序的时间段集合中，[arrive, depart) 是否可用。
bool isStandAvailable(const std::vector<std::pair<int, int>>& schedules,
                      int arrive, int depart);
