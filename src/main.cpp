#include "Core/Logger.h"
#include "Client/ClientProcess.h"

int main() {
    core::Logger::info("STONEBOTTRY starting...");

    client::ClientProcess clientProcess;
    if (!clientProcess.find("AlcazarMeta.exe")) {
        core::Logger::warn("AlcazarMeta.exe is not running.");
        return 0;
    }

    core::Logger::info("AlcazarMeta.exe detected.");

    if (!clientProcess.openReadOnly()) {
        core::Logger::error("Could not open the client with read-only access.");
        return 1;
    }

    core::Logger::info("Client opened with read-only access.");

    for (const auto& module : clientProcess.modules()) {
        core::Logger::info(
            module.name + " base=0x" +
            std::to_string(static_cast<unsigned long long>(module.baseAddress)) +
            " size=" + std::to_string(module.size));
    }

    core::Logger::info("Client module map initialized.");
    return 0;
}
