#include "Client/ClientProcess.h"

#ifdef _WIN32
#include <tlhelp32.h>
#endif

namespace client {

ClientProcess::~ClientProcess() {
    close();
}

bool ClientProcess::find(const std::string& executableName) {
    close();

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

bool ClientProcess::openReadOnly() {
#ifdef _WIN32
    if (!attached_ || processId_ == 0) return false;
    if (processHandle_) return true;

    processHandle_ = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                 FALSE, processId_);
    if (!processHandle_) return false;

    return refreshModules();
#else
    return false;
#endif
}

void ClientProcess::close() noexcept {
#ifdef _WIN32
    if (processHandle_) {
        CloseHandle(processHandle_);
        processHandle_ = nullptr;
    }
#endif
    modules_.clear();
    attached_ = false;
    processId_ = 0;
    executableName_.clear();
}

bool ClientProcess::refreshModules() {
#ifdef _WIN32
    if (!processHandle_ || processId_ == 0) return false;

    HANDLE snapshot = CreateToolhelp32Snapshot(
        TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, processId_);
    if (snapshot == INVALID_HANDLE_VALUE) return false;

    modules_.clear();

    MODULEENTRY32A entry{};
    entry.dwSize = sizeof(entry);

    if (Module32FirstA(snapshot, &entry)) {
        do {
            ModuleInfo info;
            info.name = entry.szModule;
            info.baseAddress = reinterpret_cast<std::uintptr_t>(entry.modBaseAddr);
            info.size = entry.modBaseSize;
            modules_.push_back(std::move(info));
        } while (Module32NextA(snapshot, &entry));
    }

    CloseHandle(snapshot);
    return !modules_.empty();
#else
    return false;
#endif
}

const std::vector<ModuleInfo>& ClientProcess::modules() const noexcept {
    return modules_;
}

const ModuleInfo* ClientProcess::findModule(
    const std::string& moduleName) const noexcept {
    for (const auto& module : modules_) {
        if (module.name == moduleName) return &module;
    }
    return nullptr;
}

bool ClientProcess::isAttached() const noexcept {
    return attached_;
}

std::uint32_t ClientProcess::processId() const noexcept {
    return processId_;
}

const std::string& ClientProcess::executableName() const noexcept {
    return executableName_;
}

#ifdef _WIN32
HANDLE ClientProcess::nativeHandle() const noexcept {
    return processHandle_;
}
#endif

}
