#pragma once

#include <vector>

// 一个停机位。前 N 个是靠桥机位，后 M 个是远端机位。
struct Stand {
    int id;             // 机位编号：0 .. N+M-1
    bool isBridge;      // true=靠桥机位，false=远端机位
    bool isLarge;       // 是否为大机位
    int unloadTime;     // 该机位每位乘客的下机时间（分钟）
};

// 一架需要分配机位的飞机。
struct Plane {
    int id;             // 飞机编号：0 .. K-1
    int arrive;         // 计划到达时刻（分钟）
    int depart;         // 计划离开时刻（分钟）
    bool isLarge;       // 是否为大飞机
    int passengers;     // 乘客人数
};

// 一个完整的停机位调度案例。
struct Case {
    int caseId = -1;
    int N = 0;          // 靠桥机位数量
    int M = 0;          // 远端机位数量
    int K = 0;          // 飞机数量
    std::vector<Stand> stands;    // 长度为 N+M
    std::vector<Plane> planes;    // 长度为 K
};
