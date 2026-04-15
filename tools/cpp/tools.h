#pragma once
#include <string>
#include <string_view>

// C++ tool interface.
// Add new tools following this pattern.
// Expose via extern "C" for Python/Go FFI.

namespace agent_tools {

struct Result {
    std::string output;
    bool success;
    std::string error;
};

/// Echo returns the input string unchanged.
/// Useful for testing the tool pipeline.
Result echo(std::string_view input);

// TODO: add your tools here

}  // namespace agent_tools

// FFI interface — callable from Python (ctypes) and Go (cgo)
extern "C" {
int echo_ffi(const char* input, char* output, int output_len);
}
