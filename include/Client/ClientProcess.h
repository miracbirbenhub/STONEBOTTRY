#pragma once

#include <string>
#include <cstdint>

namespace client {

class ClientProcess {
public:
    bool find(const std::string& executableName);
    bool isAttached() const noexcept;
    std::uint32_t processId() const noexcept;
    const std::string& executableName() const noexcept;

private:
    bool attached_{false};
    std::uint32_t processId_{0};
    std::string executableName_;
};

}
