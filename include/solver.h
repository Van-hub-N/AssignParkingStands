#pragma once
#include "case.h"
#include <string>
#include <vector>

// ==========================================
// 1. 统一的算法结果结构体
// ==========================================
struct Solution {
    std::vector<int> assign;     // assign[i] = 飞机 i 分配的机位 id，-1 表示未分配
    long long objective = 0;     // 目标函数值：总下机时间 (人·分钟)
    bool feasible = false;       // 是否找到了可行解
    double timeMs = 0.0;         // 算法运行耗时（毫秒），用于实验对比
    long long nodesExpanded = 0; // 搜索节点数（用于回溯/分支限界分析）
};

// ==========================================
// 2. 算法统一抽象基类 (Solver)
// ==========================================
class Solver {
public:
    virtual ~Solver() = default;
    
    // 获取算法名称（用于日志和结果输出）
    virtual std::string getName() const = 0;
    
    // 核心求解接口，所有算法都必须实现这个函数
    virtual Solution solve(const Case& c) = 0;
};

// ==========================================
// 3. 具体算法类的声明
// ==========================================

// 3.1 贪心算法
class GreedySolver : public Solver {
private:
    int strategyType;
public:
    explicit GreedySolver(int type) : strategyType(type) {}
    ~GreedySolver() override = default; // 确保加上 override
    
    std::string getName() const override {
        return "Greedy_Strategy_" + std::to_string(strategyType);
    }
    Solution solve(const Case& c) override;
};
// 3.2 回溯法
class BacktrackingSolver : public Solver {
public:
    std::string getName() const override { return "Backtracking"; }
    Solution solve(const Case& c) override;
};

// 3.3 分支限界法
class BranchBoundSolver : public Solver {
public:
    std::string getName() const override { return "Branch_and_Bound"; }
    Solution solve(const Case& c) override;
};

// 3.4 启发式算法（如遗传算法）
class HeuristicSolver : public Solver {
public:
    std::string getName() const override { return "Genetic_Algorithm"; }
    Solution solve(const Case& c) override;
};

// ==========================================
// 4. 公共辅助函数声明
// ==========================================

// 计算分配方案的目标值（总下机时间），防止算法内部算错
long long calculateObjective(const Case& c, const std::vector<int>& assign);

// 校验一个分配方案是否合法（时间冲突、机型匹配等）
bool validateSolution(const Case& c, const Solution& sol, std::string& err);

// 检查给定机位在时间段 [arrive, depart] 内是否可用
bool isStandAvailable(const std::vector<std::pair<int, int>>& schedules, int arrive, int depart);
