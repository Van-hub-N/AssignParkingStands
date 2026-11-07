#include "io.h"

#include <iomanip>
#include <iostream>
#include <string>

namespace {
void printUsage(const char* argv0) {
    std::cout << "用法: " << argv0
              << " [caseId] [--data-dir 目录]\n";
}
}

int main(int argc, char** argv) {
    int caseId = 0;
    std::string dataDir = "data/cases";
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--data-dir" && i + 1 < argc) {
            dataDir = argv[++i];
        } else if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            return 0;
        } else {
            try {
                caseId = std::stoi(arg);
            } catch (...) {
                std::cerr << "案例编号必须是整数: " << arg << "\n";
                return 2;
            }
        }
    }

    Case c;
    std::string err;
    if (!loadCase(caseId, dataDir, c, err)) {
        std::cerr << err << "\n";
        return 1;
    }
    if (!validateCase(c, err)) {
        std::cerr << "案例不合法: " << err << "\n";
        return 2;
    }

    std::cout << "案例 " << c.caseId << ": N=" << c.N << ", M=" << c.M
              << ", K=" << c.K << "\n\n";
    std::cout << "机位（前 N 个为靠桥机位，后 M 个为远端机位）:\n";
    std::cout << std::left << std::setw(8) << "id"
              << std::setw(10) << "类型"
              << std::setw(10) << "大小"
              << "下机时间(分钟)\n";
    for (const Stand& s : c.stands) {
        std::cout << std::left << std::setw(8) << s.id
                  << std::setw(10) << (s.isBridge ? "靠桥" : "远端")
                  << std::setw(10) << (s.isLarge ? "大" : "小")
                  << s.unloadTime << '\n';
    }

    std::cout << "\n飞机:\n";
    std::cout << std::left << std::setw(8) << "id"
              << std::setw(10) << "到达"
              << std::setw(10) << "离开"
              << std::setw(10) << "大小"
              << "乘客数\n";
    for (const Plane& p : c.planes) {
        std::cout << std::left << std::setw(8) << p.id
                  << std::setw(10) << p.arrive
                  << std::setw(10) << p.depart
                  << std::setw(10) << (p.isLarge ? "大" : "小")
                  << p.passengers << '\n';
    }
    return 0;
}
