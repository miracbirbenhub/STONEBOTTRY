#include "Client/ClientProcess.h"

#ifdef _WIN32
#include <tlhelp32.h>
#include <windows.h>
#include <winnt.h>
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

std::vector<SectionInfo> ClientProcess::inspectPeSections(
    const std::string& executablePath) {
    std::vector<SectionInfo> sections;

#ifdef _WIN32
    HANDLE file = CreateFileA(executablePath.c_str(), GENERIC_READ,
                              FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                              nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file == INVALID_HANDLE_VALUE) return sections;

    HANDLE mapping = CreateFileMappingA(file, nullptr, PAGE_READONLY, 0, 0, nullptr);
    if (!mapping) {
        CloseHandle(file);
        return sections;
    }

    const auto* base = static_cast<const std::uint8_t*>(
        MapViewOfFile(mapping, FILE_MAP_READ, 0, 0, 0));

    if (base) {
        const auto* dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(base);
        if (dos->e_magic == IMAGE_DOS_SIGNATURE) {
            const auto* nt = reinterpret_cast<const IMAGE_NT_HEADERSA*>(
                base + dos->e_lfanew);

            if (nt->Signature == IMAGE_NT_SIGNATURE) {
                const auto* firstSection = IMAGE_FIRST_SECTION(nt);
                for (unsigned i = 0; i < nt->FileHeader.NumberOfSections; ++i) {
                    char name[9]{};
                    for (int j = 0; j < 8 && firstSection[i].Name[j]; ++j)
                        name[j] = static_cast<char>(firstSection[i].Name[j]);

                    SectionInfo section;
                    section.name = name;
                    section.virtualAddress = firstSection[i].VirtualAddress;
                    section.virtualSize = firstSection[i].Misc.VirtualSize;
                    section.rawSize = firstSection[i].SizeOfRawData;
                    section.characteristics = firstSection[i].Characteristics;
                    sections.push_back(std::move(section));
                }
            }
        }

        UnmapViewOfFile(base);
    }

    CloseHandle(mapping);
    CloseHandle(file);
#else
    (void)executablePath;
#endif

    return sections;
}

#ifdef _WIN32
HANDLE ClientProcess::nativeHandle() const noexcept {
    return processHandle_;
}
#endif

bool ClientProcess::isAttached() const noexcept {
    return attached_;
}

std::uint32_t ClientProcess::processId() const noexcept {
    return processId_;
}

const std::string& ClientProcess::executableName() const noexcept {
    return executableName_;
}

}
