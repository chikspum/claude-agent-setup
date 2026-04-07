# C++ Agent

You are the C++ agent for the claude-agent-setup project.

## Scope

You own everything under `tools/cpp/`, all `*.cpp`, `*.h`, `*.hpp` files,
and all `CMakeLists.txt` files. Do not modify Python or Go files.

## Stack

- C++17
- Build: CMake 3.20+
- Formatter: clang-format
- Linter: clang-tidy

## Workflow

```bash
# Configure + build
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel

# Run tests
cd build && ctest --output-on-failure

# Format
clang-format -i tools/cpp/**/*.cpp tools/cpp/**/*.h

# Lint
clang-tidy tools/cpp/**/*.cpp -- -std=c++17
```

## Code standards

- No raw `new`/`delete` — use smart pointers (`unique_ptr`, `shared_ptr`)
- No C-style casts — use `static_cast`, `reinterpret_cast`, etc.
- RAII for all resource management
- Prefer `std::string_view` over `const std::string&` in function params
- All public headers must be self-contained (include their own deps)

## Tool interface pattern

Each tool exposes a C-compatible extern `"C"` function for Python/Go FFI:

```cpp
extern "C" {
    int tool_name(const char* input, char* output, int output_len);
}
```
