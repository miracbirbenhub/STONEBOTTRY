#include "Core/Logger.h"
#include "Client/ClientProcess.h"

int main() {
    core::Logger::info("STONEBOTTRY starting...");

    client::ClientProcess clientProcess;
    if (clientProcess.find("AlcazarMeta.exe")) {
        core::Logger::info("AlcazarMeta.exe detected.");
    } else {
        core::Logger::warn("AlcazarMeta.exe is not running.");
    }

    core::Logger::info("Client integration layer initialized.");
    return 0;
}
