#include "Client/ClientProcess.h"

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#endif

namespace client {

bool ClientProcess::find(const std::string& executableName) {
#ifdef _WIN32
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snapshot == INVALID_HANDLE_VALUE) return false;

    PROCESSENTRY32A entry{};
    entry.dwSize = sizeof(entry);

    bool found = false;
    if (Process32FirstA(snapshot, &entry)) {
        do {
            if (executableName == entry.szExeFile) {
                processId_ = entry.th32ProcessID;
                executableName_ = entry.szExeFile;
                attached_ = true;
                found = true;
                break;
            }
        } while (Process32NextA(snapshot, &entry));
    }

    CloseHandle(snapshot);
    return found;
#else
    (void)executableName;
    return false;
#endif
}

bool ClientProcess::isAttached() const noexcept { return attached_; }
std::uint32_t ClientProcess::processId() const noexcept { return processId_; }
const std::string& ClientProcess::executableName() const noexcept { return executableName_; }

}
