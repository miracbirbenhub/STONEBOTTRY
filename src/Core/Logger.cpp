#include "Core/Logger.h"
#include <iostream>

namespace core {

void Logger::info(std::string_view message)  { std::cout << "[INFO] "  << message << '\\n'; }
void Logger::warn(std::string_view message)  { std::cout << "[WARN] "  << message << '\\n'; }
void Logger::error(std::string_view message) { std::cerr << "[ERROR] " << message << '\\n'; }

}
