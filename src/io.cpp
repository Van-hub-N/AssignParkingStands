#include "io.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
bool validateCase(const Case& c, std::string& err) {
    if (c.stands.size() != static_cast<size_t>(c.N + c.M)) { err = "停机位数量不匹配"; return false; }
    if (c.planes.size() != static_cast<size_t>(c.K)) { err = "飞机数量不匹配"; return false; }

    int maxBridgeTime = 0;
    for (int i = 0; i < c.N; ++i) {
        if (!c.stands[i].isBridge) { err = "前N个必须是靠桥机位"; return false; }
        if (c.stands[i].unloadTime > maxBridgeTime) maxBridgeTime = c.stands[i].unloadTime;
    }
    
    for (int i = c.N; i < c.N + c.M; ++i) {
        if (c.stands[i].isBridge) { err = "远端机位不能靠桥"; return false; }
        if (!c.stands[i].isLarge) { err = "远端机位必须是全大机位"; return false; }
        if (c.stands[i].unloadTime <= maxBridgeTime) { err = "远端下机时间必须大于靠桥"; return false; }
    }

    for (const auto& p : c.planes) {
        if (p.arrive >= p.depart) { err = "飞机到达时间不能晚于离开时间"; return false; }
        if (p.passengers <= 0) { err = "乘客人数必须大于0"; return false; }
    }
    return true;
}
void saveCase(const Case& c, const std::string& path) {
    std::ofstream out(path, std::ios::binary);
    if (!out) { std::cerr << "无法写入文件: " << path << "\n"; return; }

    out.write((char*)&c.caseId, sizeof(int));
    out.write((char*)&c.N, sizeof(int));
    out.write((char*)&c.M, sizeof(int));
    out.write((char*)&c.K, sizeof(int));

    for (const auto& s : c.stands) {
        out.write((char*)&s.id, sizeof(int));
        out.write((char*)&s.isBridge, sizeof(bool));
        out.write((char*)&s.isLarge, sizeof(bool));
        out.write((char*)&s.unloadTime, sizeof(int));
    }

    for (const auto& p : c.planes) {
        out.write((char*)&p.id, sizeof(int));
        out.write((char*)&p.arrive, sizeof(int));
        out.write((char*)&p.depart, sizeof(int));
        out.write((char*)&p.isLarge, sizeof(bool));
        out.write((char*)&p.passengers, sizeof(int));
    }
}

// 辅助补零函数
std::string pad5(int x) {
    std::ostringstream oss;
    oss << std::setw(5) << std::setfill('0') << x;
    return oss.str();
}

Case loadCase(int caseId, const std::string& dir) {
    std::string path = dir + "/case_" + pad5(caseId) + ".bin";
    std::ifstream in(path, std::ios::binary);
    Case c;
    if (!in) {
        std::cerr << "无法打开案例文件: " << path << "\n";
        return c;
    }

    in.read((char*)&c.caseId, sizeof(int));
    in.read((char*)&c.N, sizeof(int));
    in.read((char*)&c.M, sizeof(int));
    in.read((char*)&c.K, sizeof(int));

    c.stands.resize(c.N + c.M);
    for (auto& s : c.stands) {
        in.read((char*)&s.id, sizeof(int));
        in.read((char*)&s.isBridge, sizeof(bool));
        in.read((char*)&s.isLarge, sizeof(bool));
        in.read((char*)&s.unloadTime, sizeof(int));
    }

    c.planes.resize(c.K);
    for (auto& p : c.planes) {
        in.read((char*)&p.id, sizeof(int));
        in.read((char*)&p.arrive, sizeof(int));
        in.read((char*)&p.depart, sizeof(int));
        in.read((char*)&p.isLarge, sizeof(bool));
        in.read((char*)&p.passengers, sizeof(int));
    }

    return c;
}
