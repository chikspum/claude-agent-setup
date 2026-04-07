#include "tools.h"
#include <cassert>
#include <iostream>

void test_echo() {
    auto result = agent_tools::echo("hello");
    assert(result.success);
    assert(result.output == "hello");
    assert(result.error.empty());
    std::cout << "PASS: test_echo\n";
}

void test_echo_ffi() {
    char buf[256];
    int n = echo_ffi("hello ffi", buf, sizeof(buf));
    assert(n > 0);
    assert(std::string(buf) == "hello ffi");
    std::cout << "PASS: test_echo_ffi\n";
}

int main() {
    test_echo();
    test_echo_ffi();
    std::cout << "All tests passed.\n";
    return 0;
}
