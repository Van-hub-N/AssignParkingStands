#include "io.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <utility>

namespace {

// 案例文件采用本机的小端二进制布局：4 个 int 头 + 每个机位
// (int, bool, bool, int) + 每架飞机 (int, int, int, bool, int)。
// 这些静态断言保证当前平台的布局与生成器一致。
static_assert(sizeof(int) == 4, "案例格式要求 32 位 int");
static_assert(sizeof(bool) == 1, "案例格式要求单字节 bool");

bool ensureParentDirectory(const std::string& path) {
    const std::filesystem::path p(path);
    const auto parent = p.parent_path();
    if (parent.empty()) {
        return true;
    }
    std::error_code ec;
    std::filesystem::create_directories(parent, ec);
    return !ec;
}

std::string casePath(const std::string& dir, int caseId) {
    return dir + "/case_" + pad5(caseId) + ".bin";
}

}  // namespace

bool validateCase(const Case& c, std::string& err) {
    if (c.N < 0 || c.M < 0 || c.K < 0) {
        err = "N、M、K 不能为负数";
        return false;
    }
    if (c.stands.size() != static_cast<std::size_t>(c.N + c.M)) {
        err = "停机位数量与 N+M 不匹配";
        return false;
    }
    if (c.planes.size() != static_cast<std::size_t>(c.K)) {
        err = "飞机数量与 K 不匹配";
        return false;
    }

    int maxBridgeTime = 0;
    for (int i = 0; i < c.N; ++i) {
        const Stand& s = c.stands[i];
        if (!s.isBridge) {
            err = "前 N 个机位必须都是靠桥机位";
            return false;
        }
        if (s.unloadTime <= 0) {
            err = "机位下机时间必须为正数";
            return false;
        }
        maxBridgeTime = std::max(maxBridgeTime, s.unloadTime);
    }

    for (int i = c.N; i < c.N + c.M; ++i) {
        const Stand& s = c.stands[i];
        if (s.isBridge) {
            err = "远端机位不能标记为靠桥机位";
            return false;
        }
        if (!s.isLarge) {
            err = "远端机位必须全部为大机位";
            return false;
        }
        if (s.unloadTime <= 0) {
            err = "机位下机时间必须为正数";
            return false;
        }
        if (s.unloadTime <= maxBridgeTime) {
            err = "远端机位的下机时间必须严格大于靠桥机位";
            return false;
        }
    }

    for (const Plane& p : c.planes) {
        if (p.arrive < 0) {
            err = "飞机到达时刻不能为负数";
            return false;
        }
        if (p.arrive >= p.depart) {
            err = "飞机到达时刻必须早于离开时刻";
            return false;
        }
        if (p.passengers <= 0) {
            err = "乘客人数必须大于 0";
            return false;
        }
    }
    return true;
}

bool saveCase(const Case& c, const std::string& path) {
    if (!ensureParentDirectory(path)) {
        return false;
    }

    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) {
        return false;
    }

    out.write(reinterpret_cast<const char*>(&c.caseId), sizeof(c.caseId));
    out.write(reinterpret_cast<const char*>(&c.N), sizeof(c.N));
    out.write(reinterpret_cast<const char*>(&c.M), sizeof(c.M));
    out.write(reinterpret_cast<const char*>(&c.K), sizeof(c.K));

    for (const Stand& s : c.stands) {
        out.write(reinterpret_cast<const char*>(&s.id), sizeof(s.id));
        out.write(reinterpret_cast<const char*>(&s.isBridge), sizeof(s.isBridge));
        out.write(reinterpret_cast<const char*>(&s.isLarge), sizeof(s.isLarge));
        out.write(reinterpret_cast<const char*>(&s.unloadTime), sizeof(s.unloadTime));
    }

    for (const Plane& p : c.planes) {
        out.write(reinterpret_cast<const char*>(&p.id), sizeof(p.id));
        out.write(reinterpret_cast<const char*>(&p.arrive), sizeof(p.arrive));
        out.write(reinterpret_cast<const char*>(&p.depart), sizeof(p.depart));
        out.write(reinterpret_cast<const char*>(&p.isLarge), sizeof(p.isLarge));
        out.write(reinterpret_cast<const char*>(&p.passengers), sizeof(p.passengers));
    }

    out.flush();
    return static_cast<bool>(out);
}

bool loadCase(int caseId, const std::string& dir, Case& out, std::string& err) {
    const std::string path = casePath(dir, caseId);
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        err = "无法打开案例文件: " + path;
        return false;
    }

    Case c;
    in.read(reinterpret_cast<char*>(&c.caseId), sizeof(c.caseId));
    in.read(reinterpret_cast<char*>(&c.N), sizeof(c.N));
    in.read(reinterpret_cast<char*>(&c.M), sizeof(c.M));
    in.read(reinterpret_cast<char*>(&c.K), sizeof(c.K));
    if (!in || c.N < 0 || c.M < 0 || c.K < 0 ||
        c.N + c.M > 1000000 || c.K > 1000000) {
        err = "案例头损坏或规模异常: " + path;
        return false;
    }

    c.stands.resize(static_cast<std::size_t>(c.N + c.M));
    for (Stand& s : c.stands) {
        in.read(reinterpret_cast<char*>(&s.id), sizeof(s.id));
        in.read(reinterpret_cast<char*>(&s.isBridge), sizeof(s.isBridge));
        in.read(reinterpret_cast<char*>(&s.isLarge), sizeof(s.isLarge));
        in.read(reinterpret_cast<char*>(&s.unloadTime), sizeof(s.unloadTime));
    }

    c.planes.resize(static_cast<std::size_t>(c.K));
    for (Plane& p : c.planes) {
        in.read(reinterpret_cast<char*>(&p.id), sizeof(p.id));
        in.read(reinterpret_cast<char*>(&p.arrive), sizeof(p.arrive));
        in.read(reinterpret_cast<char*>(&p.depart), sizeof(p.depart));
        in.read(reinterpret_cast<char*>(&p.isLarge), sizeof(p.isLarge));
        in.read(reinterpret_cast<char*>(&p.passengers), sizeof(p.passengers));
    }

    if (!in) {
        err = "案例数据不完整: " + path;
        return false;
    }

    out = std::move(c);
    return true;
}

Case loadCase(int caseId, const std::string& dir) {
    Case c;
    std::string err;
    if (!loadCase(caseId, dir, c, err)) {
        return Case{};
    }
    return c;
}

std::string pad5(int x) {
    std::ostringstream oss;
    oss << std::setw(5) << std::setfill('0') << x;
    return oss.str();
}
