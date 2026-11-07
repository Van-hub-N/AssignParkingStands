# 停机位调度实验：贪心、回溯与分支限界

本工程对应《算法分析与设计综合实验：停机位调度问题》的实验一、实验二和实验三：

- **实验一**：用固定随机种子生成 100 种 `(N, M, K)` 参数组合、共 10000 个案例，实现两种停机位分配贪心策略，统计总下机时间并比较；
- **实验二**：实现回溯法，在贪心初始解的基础上搜索更优分配，与贪心法对比，并分析 N/M/K 较大时的搜索规模问题与改进方向；
- **实验三**：实现分支限界法，使用双贪心初始上界、静态后缀下界和动态可用机位下界，与回溯法在 10000 个案例上对比，并分析大规模问题的改进方案。

问题目标为最小化总下机时间（单位：人·分钟）：

```text
min Σ p_i * u_{s(i)}
```

其中 `p_i` 为飞机 `i` 的乘客数，`u_{s(i)}` 为飞机 `i` 所分配机位的每人下机时间。

## 结果速览

### 实验一：两种贪心策略

- 数据集：100 种参数组合 × 100 个案例 = 10000 个案例，K=5..499；
- 策略 1（乘客优先）总目标值：3,114,966,033 人·分钟；
- 策略 2（到达优先）总目标值：3,439,405,896 人·分钟，比策略 1 高 10.42%；
- 逐案例：策略 1 严格胜出 8,983 次，策略 2 胜出 297 次，持平 720 次；
- 全量案例校验：不合法案例 0，非法解 0，不可行解 0。

### 实验二：回溯法

- **精确/近精确组**（K≤11，2000 个案例，结点上限 1000 万、时间上限 2 s）：
  - 1986 个案例完成搜索并证明最优（99.3%），14 个案例达到结点上限；
  - 回溯优于贪心 291 个，持平 1709 个，更差 0 个；
  - 贪心总目标值 50,384,448，回溯 50,026,159，下降 0.711%；
  - 改进案例的平均改进幅度为 4.80%，单案例最大改进 32.23%。
- **可扩展性抽样**（K=13..499，100 个案例，结点上限 500 万、时间上限 1 s）：
  - 26 个案例完成搜索，74 个达到结点上限；
  - 贪心总目标值 31,611,061，回溯 31,528,951，下降 0.260%；
  - K=13-15 时仍有 24/30 个案例完成搜索；K=16-80 为 2/40，K=81-499 为 0/30。
- **全量压力测试**（10000 个案例，结点上限 20 万、时间上限 200 ms）：
  - 全部返回可行解，非法解 0、不可行解 0；
  - 2288 个案例完成搜索，7712 个案例达到结点上限；
  - 贪心总目标值 3,114,966,033，回溯 3,103,259,200，下降 0.376%；
  - 回溯优于贪心 3713 个，持平 6287 个，更差 0 个。

### 实验三：分支限界法

- **精确/近精确组**（K≤11，2000 个案例，结点上限 500 万、时间上限 2 s）：
  - 分支限界法证明最优 1995 个，回溯法 1982 个；分支限界法仅 5 个结点受限，回溯法 18 个；
  - 分支限界法相对回溯法改进 3 个、持平 1997 个、更差 0 个；
  - 回溯总目标值 50,028,729，分支限界 50,023,905，下降 0.0096%；
  - 总搜索结点从 183,300,067 降至 66,569,454，减少 63.68%；总耗时从 5,635.83 ms 降至 5,580.93 ms。
- **可扩展性抽样**（K=13..499，100 个案例，结点上限 500 万、时间上限 2 s）：
  - 分支限界法证明最优 30 个，回溯法 26 个；改进 2 个、持平 98 个、更差 0 个；
  - 总目标值 31,528,405 对 31,528,951，下降 0.0017%；总耗时 15,292.04 ms 对 14,206.32 ms，增加 7.64%。
- **全量压力测试**（10000 个案例，结点上限 20 万、时间上限 200 ms）：
  - 分支限界法证明最优 2523 个，回溯法 2288 个；改进 134 个、持平 9866 个、更差 0 个；
  - 总目标值 3,103,139,828 对 3,103,259,200，下降 0.0038%；总耗时 89,742.56 ms 对 77,940.85 ms，增加 15.14%。

> 回溯法以贪心策略 1 的可行解作为初始上界，只接受严格更优的完整解，因此不会比该贪心解更差；`Complete=0` 表示未证明最优，返回的仍是当前最好的可行解。

完整数据见 `results/`，分析见 `docs/` 中的三份实验报告。

## 目录结构

```text
.
├── CMakeLists.txt
├── include/
│   ├── case.h                 # 案例、机位、飞机数据结构
│   ├── io.h                   # 案例读写接口
│   └── solver.h               # 求解器接口、解结构与公共函数声明
├── src/
│   ├── greedy.cpp             # 两种贪心策略
│   ├── backtracking.cpp       # 回溯法：排序、下界、DFS、时间/结点上限
│   ├── branch_bound.cpp       # 分支限界：双贪心上界、静态/动态下界、剪枝与回滚
│   ├── io.cpp                 # 二进制案例读写与案例合法性检查
│   └── utils.cpp              # 目标值计算、解合法性检查
├── tools/
│   ├── generate_cases.cpp     # 生成 data/combos.csv 与 10000 个案例
│   ├── dump_case.cpp          # 查看单个案例
│   ├── validate_all.cpp       # 批量校验案例和两种贪心解
│   ├── benchmark.cpp          # 10000 案例贪心对比
│   ├── backtracking_benchmark.cpp # 回溯法与贪心逐案例对比
│   ├── branch_bound_benchmark.cpp # 贪心/回溯/分支限界三方对比
│   └── solve_case.cpp         # 打印单案例的贪心/回溯/分支限界分配过程
├── data/
│   ├── combos.csv             # 100 种参数组合
│   ├── cases/                 # 完整案例（可由生成器重建，约 59 MB）
│   └── sample_cases/          # 提交包保留的 13 个代表性样例
├── results/                   # 实测 CSV、统计 JSON 与校验摘要
├── docs/                      # 实验报告、图表与生成脚本
│   ├── 2024303425-范劲庚-实验一报告.docx
│   ├── 2024303425-范劲庚-实验二报告.docx
│   ├── 2024303425-范劲庚-实验三报告.docx
│   ├── make_exp2_figures.py
│   ├── make_exp2_report.py
│   ├── make_exp3_stats.py
│   ├── make_exp3_figures.py
│   ├── make_exp3_report.py
│   └── figures/
└── tests/                     # CTest 说明
```

## 构建

要求：CMake >= 3.16、支持 C++17 的编译器。

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

构建目标位于 `build/bin/`。工程同时提供 `prepare_data` 目标：若存在 `data/cases`，会在构建目录建立软链接，便于从构建目录直接运行。

## 复现实验

在项目根目录执行：

```bash
# 1. 重新生成 10000 个案例和参数表
./build/bin/generate_cases --out-dir data

# 2. 校验全部案例及两种贪心解
./build/bin/validate_all --start 0 --count 10000 --data-dir data/cases

# 3. 两种贪心策略的完整对比
./build/bin/benchmark --start 0 --count 10000 \
    --data-dir data/cases --out results/greedy_benchmark.csv

# 4. 回溯法精确/近精确组：K<=11，取前 3000 个案例中满足条件的 2000 个
./build/bin/backtrack_benchmark --start 0 --count 3000 \
    --min-k 0 --max-k 11 \
    --time-limit-ms 2000 --node-limit 10000000 \
    --data-dir data/cases --out results/backtracking_benchmark.csv

# 5. 全量压力测试：10000 个案例，受限搜索
./build/bin/backtrack_benchmark --start 0 --count 10000 \
    --min-k 0 --max-k 1000 \
    --time-limit-ms 200 --node-limit 200000 \
    --data-dir data/cases --out results/backtracking_stress_all.csv

# 6. 分支限界法精确/近精确组：扫描全部案例，按 K<=11 过滤
./build/bin/branch_bound_benchmark --start 0 --count 10000 \
    --min-k 0 --max-k 11 \
    --time-limit-ms 2000 --node-limit 5000000 \
    --data-dir data/cases --out results/branch_bound_benchmark.csv

# 7. 分支限界法全量压力测试
./build/bin/branch_bound_benchmark --start 0 --count 10000 \
    --min-k 0 --max-k 1000 \
    --time-limit-ms 200 --node-limit 200000 \
    --data-dir data/cases --out results/branch_bound_stress_all.csv

# 8. CTest 冒烟测试
ctest --test-dir build --output-on-failure
```

查看典型案例 2081 和 325 的完整分配过程：

```bash
./build/bin/solve_case --case 2081 \
    --time-limit-ms 5000 --node-limit 10000000 --data-dir data/cases
./build/bin/solve_case --case 325 \
    --time-limit-ms 5000 --node-limit 5000000 --data-dir data/cases
```

可扩展性抽样结果 `results/backtracking_scalability.csv` 由 K=13、14、15 各 10 个案例，K=16..80 每 100 个取 1 个共 40 个案例，以及 K=81..499 每 100 个取 1 个共 30 个案例组成；具体命令见实验二报告附录。

## 两种贪心策略

两种策略采用相同的“单步选择规则”：对当前飞机，在所有满足机型要求且时间段不冲突的机位中，选择下机时间最短的机位。区别仅在处理顺序：

| 策略 | 排序键 | 设计意图 |
|---|---|---|
| 策略 1 `Greedy_ByPassengers` | 乘客人数降序，人数相同按飞机编号升序 | 优先把“乘客多、对目标值影响大”的飞机安排到下机快的机位 |
| 策略 2 `Greedy_ByArrival` | 到达时刻升序，时刻相同按飞机编号升序 | 按时间顺序安排，贴近实际调度员的在线处理方式 |

机位时间轴使用 `std::map<到达时刻, 离开时刻>` 维护，通过前驱和后继区间判断 `[arrive, depart)` 是否冲突；前一架飞机离开时刻等于后一架到达时刻时允许复用。

## 回溯法要点

- **搜索顺序**：大飞机优先（可选机位少）→ 兼容机位数少优先 → 乘客数降序 → 飞机编号；
- **初始上界**：先运行贪心策略 1，得到一个可行解，作为 `bestCost`；
- **下界**：`suffixLB[d]` 为剩余飞机“乘客数 × 该飞机兼容机位最小下机时间”的和，忽略时间冲突，因此是宽松下界；
- **剪枝**：`cost >= bestCost` 或 `cost + suffixLB[d] >= bestCost` 时回溯；
- **候选顺序**：兼容且时间空闲的机位按 `unloadTime` 升序尝试；
- **时间轴**：每个机位用半开区间 `[arrive, depart)` 维护，加入/撤销均为 `O(log K)`；
- **anytime**：结点数每步检查，时间每 1024 个结点检查；触发上限后返回当前最好可行解，并令 `complete=false`。

## 分支限界法要点

- **搜索顺序**：大飞机优先（兼容机位少）→ 兼容机位数少 → 乘客数降序 → 飞机编号；
- **初始上界**：同时运行两种贪心策略，取目标值较小者，比实验二只用策略 1 更紧；
- **静态下界**：`suffixLB[d]` 为剩余飞机“乘客数 × 兼容机位最小下机时间”的和；
- **动态下界**：为每架未分配飞机维护“未被已分配且时间重叠的飞机占用”的兼容机位集合 `A_i`；
- **动态维护**：集合元素为 `(unloadTime, standId)`，选择机位时对时间重叠的剩余飞机删除该机位，回溯时按记录插回；
- **剪枝**：`cost >= best`、`cost + LB >= best`、存在空 `A_i` 时回溯；
- **阈值**：`K <= 15` 使用动态下界，`K > 15` 退回静态下界，避免动态集合维护成本压过收益；
- **anytime**：结点/时间上限触发时返回当前最好可行解，`complete=false` 表示未证明最优。

## 输出说明

### 贪心结果 `results/greedy_benchmark.csv`

| 字段 | 含义 |
|---|---|
| `CaseId,N,M,K,Scale` | 案例编号、靠桥/远端机位数、飞机数、规模分组 |
| `Strategy1_Cost` | 策略 1 的总下机时间 |
| `Strategy1_Time(ms)` | 策略 1 的单案例耗时（毫秒） |
| `Strategy1_Feasible` | 是否所有飞机均得到合法分配 |
| `Strategy2_*` | 策略 2 的对应字段 |
| `Winner` | `strategy1`、`strategy2` 或 `tie` |

### 回溯结果 `results/backtracking_*.csv`

| 字段 | 含义 |
|---|---|
| `CaseId,N,M,K,Scale` | 案例编号、机位数、飞机数、规模分组 |
| `Greedy_Cost` | 贪心策略 1 的目标值（初始上界） |
| `Backtracking_Cost` | 回溯法返回的最好目标值 |
| `GapPercent` | 相对贪心的变化百分比，负值表示改进 |
| `Backtracking_TimeMs` | 单案例耗时（毫秒） |
| `Nodes` | 展开的搜索结点数 |
| `Complete` | 1 表示搜索完整结束并证明最优；0 表示触发上限 |
| `Status` | `optimal`、`node_limit`、`time_limit`、`infeasible` 或 `invalid` |

`results/backtracking_stats.json` 是上述 CSV 的汇总，`results/backtracking_validation_summary.txt` 记录三组实验的校验结果。

### 分支限界结果 `results/branch_bound_*.csv`

| 字段 | 含义 |
|---|---|
| `CaseId,N,M,K,Scale` | 案例编号、机位数、飞机数、规模分组 |
| `Greedy_Cost` | 贪心策略 1 的目标值 |
| `Backtracking_Cost` | 回溯法返回的最好目标值 |
| `BranchBound_Cost` | 分支限界法返回的最好目标值 |
| `Backtracking_Nodes` / `BranchBound_Nodes` | 两种算法展开的结点数 |
| `*_TimeMs` | 单案例耗时（毫秒） |
| `*_Complete` / `*_Status` | 是否证明最优、`optimal`/`node_limit`/`time_limit` 等状态 |
| `GapPercent_vs_Greedy` / `GapPercent_vs_Backtracking` | 相对贪心、相对回溯的变化百分比（负值表示更好） |

## 实验报告

- 实验一报告：`docs/2024303425-范劲庚-实验一报告.docx`
- 实验二报告：`docs/2024303425-范劲庚-实验二报告.docx`
- 实验三报告：`docs/2024303425-范劲庚-实验三报告.docx`

实验一报告包含案例生成、两种贪心策略伪代码与流程图、10000 案例实验结果、复杂度分析和改进方向；实验二报告包含回溯法设计、剪枝与 anytime 机制、精确组/可扩展性/全量压力实验、典型案例、复杂度分析和大规模问题改进方案。实验三报告包含分支限界法的双贪心上界、静态/动态下界、正确性证明、与回溯法的三组对比、动态阈值实验、典型案例 325，以及大规模问题的改进算法框架。

图表和报告生成脚本位于 `docs/`，可选依赖 Python 3、matplotlib 和 python-docx；提交包不包含虚拟环境。实验二、实验三脚本分别读取 `results/backtracking_stats.json` 和 `results/branch_bound_stats.json`，重新生成前需先安装上述依赖。

## 复现性说明

- 参数组合种子：`12345`；
- 第 `caseId` 个案例的种子：`20260000 + caseId`；
- 二进制格式固定使用 4 字节 `int` 和 1 字节 `bool`，并在 `src/io.cpp` 中用 `static_assert` 检查；
- 完整 10000 个案例约 59 MB，压缩包中只放 13 个代表性样例案例；执行 `generate_cases` 可完整重建；
- 回溯法和分支限界法都使用固定搜索顺序和固定上限，结果可重复；耗时受机器负载影响，目标值与结点数稳定；
- 分支限界法的动态下界阈值固定为 `K <= 15`，可用 `branch_bound_benchmark` 的 `--min-k/--max-k` 复现阈值两侧的对比。

## 当前范围

实验一（贪心）、实验二（回溯）和实验三（分支限界）均已实现。实验三报告第 5 节给出大规模问题的改进算法框架（匹配下界、对称性消除、有界最佳优先、LNS/列生成），并明确说明这些改进未作为主算法实现；后续工作可在现有 `BranchBoundSolver` 上继续扩展。
