# 测试说明

构建后执行：

```bash
ctest --test-dir build --output-on-failure
```

若已生成完整数据集（`data/cases/case_00000.bin` 存在），CMake 会注册三个测试：

- `validate_first_100`：校验前 100 个案例，并校验两种贪心解；
- `benchmark_first_10`：对前 10 个案例运行两种贪心策略，输出 `build/smoke_benchmark.csv`；
- `backtracking_small`：对编号 200..209、K≤6 的案例运行回溯法与贪心对比，输出 `build/smoke_backtracking.csv`。

若提交包只带样例案例，则会自动改用 `data/sample_cases`：

- `validate_sample`：校验样例案例 00000；
- `benchmark_sample`：对样例案例 7000 运行两种贪心策略；
- `backtracking_sample`：对样例案例 2500（K=7）运行回溯法与贪心对比。

这样无论是否重新生成 10000 个案例，都能完成一次构建与运行冒烟检查。测试只覆盖小规模案例，不替代报告中的完整基准。
