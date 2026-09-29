#pragma once

#include <cstdint>
#include <string>

#ifdef _WIN32
#include <windows.h>
#endif

namespace client {

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

private:
    bool attached_{false};
    std::uint32_t processId_{0};
    std::string executableName_;

#ifdef _WIN32
    HANDLE processHandle_{nullptr};
#endif
};

}
