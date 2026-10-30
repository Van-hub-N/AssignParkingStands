#pragma once
#include <vector>

struct Stand {
    int id;
    bool isBridge;      // true=靠桥, false=远端
    bool isLarge;       // 是否大机位
    int unloadTime;     // 乘客下机时间（分钟）
};

struct Plane {
    int id;
    int arrive;         // 到达时刻
    int depart;         // 离开时刻
    bool isLarge;       // 是否大飞机
    int passengers;     // 乘客人数
};

struct Case {
    int caseId;
    int N, M, K;
    std::vector<Stand> stands;   // 前N个是靠桥，后M个是远端
    std::vector<Plane> planes;
};
