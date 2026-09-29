#pragma once

#include <cstdint>
#include <string>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#endif

namespace client {

struct ModuleInfo {
    std::string name;
    std::uintptr_t baseAddress{0};
    std::uint32_t size{0};
};

struct SectionInfo {
    std::string name;
    std::uint32_t virtualAddress{0};
    std::uint32_t virtualSize{0};
    std::uint32_t rawSize{0};
    std::uint32_t characteristics{0};
};

class ClientProcess {
public:
    ClientProcess() = default;
    ~ClientProcess();

    ClientProcess(const ClientProcess&) = delete;
    ClientProcess& operator=(const ClientProcess&) = delete;

    bool find(const std::string& executableName);
    bool openReadOnly();
    void close() noexcept;

    bool isAttached() const noexcept;
    std::uint32_t processId() const noexcept;
    const std::string& executableName() const noexcept;

    bool refreshModules();
    const std::vector<ModuleInfo>& modules() const noexcept;
    const ModuleInfo* findModule(const std::string& moduleName) const noexcept;

#ifdef _WIN32
    HANDLE nativeHandle() const noexcept;
#endif

    static std::vector<SectionInfo> inspectPeSections(
        const std::string& executablePath);

private:
    bool attached_{false};
    std::uint32_t processId_{0};
    std::string executableName_;
    std::vector<ModuleInfo> modules_;

#ifdef _WIN32
    HANDLE processHandle_{nullptr};
#endif
};

}
