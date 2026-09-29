#include "Core/Logger.h"
#include "Client/ClientProcess.h"

#include <iomanip>
#include <sstream>

namespace {

std::string hexAddress(std::uintptr_t value) {
    std::ostringstream out;
    out << "0x" << std::hex << std::uppercase << value;
    return out.str();
}

}

int main() {
    core::Logger::info("STONEBOTTRY diagnostic starting...");

    client::ClientProcess clientProcess;
    if (!clientProcess.find("AlcazarMeta.exe")) {
        core::Logger::warn("AlcazarMeta.exe is not running.");
        return 0;
    }

    core::Logger::info("PID: " + std::to_string(clientProcess.processId()));

    if (!clientProcess.openReadOnly()) {
        core::Logger::error("Could not open the client with read-only access.");
        return 1;
    }

    core::Logger::info("Loaded modules:");
    for (const auto& module : clientProcess.modules()) {
        core::Logger::info(
            "  " + module.name +
            " | base=" + hexAddress(module.baseAddress) +
            " | size=" + std::to_string(module.size));
    }

    core::Logger::info("Diagnostic module map ready.");
    core::Logger::info(
        "Next step: use this output to identify the client modules relevant to GameState.");

    return 0;
}
