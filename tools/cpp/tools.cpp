#include "tools.h"

#include <cstring>

namespace agent_tools {

Result echo(std::string_view input) { return Result{std::string(input), true, ""}; }

}  // namespace agent_tools

extern "C" {

int echo_ffi(const char* input, char* output, int output_len) {
    if (!input || !output || output_len <= 0) return -1;
    auto result = agent_tools::echo(input);
    std::strncpy(output, result.output.c_str(), static_cast<size_t>(output_len) - 1);
    output[output_len - 1] = '\0';
    return static_cast<int>(result.output.size());
}

}  // extern "C"
