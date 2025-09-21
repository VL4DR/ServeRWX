#pragma once

#include "common/common.h"

#define SERVER_ENTRY_ABI        __attribute__((sysv_abi))

#ifdef COMPILE_X64
typedef uint64_t address_t;
typedef uint64_t value_t;

struct register_context
{
    uint64_t rsp;
    uint64_t r15;
    uint64_t r14;
    uint64_t r13;
    uint64_t r12;
    uint64_t r11;
    uint64_t r10;
    uint64_t r9;
    uint64_t r8;
    uint64_t rsi;
    uint64_t rdi;
    uint64_t rdx;
    uint64_t rcx;
    uint64_t rbx;
    uint64_t rax;
};
#else
typedef uint32_t address_t;
typedef uint32_t value_t;

struct register_context
{
    uint32_t esp;
    uint32_t esi;
    uint32_t edi;
    uint32_t edx;
    uint32_t ecx;
    uint32_t ebx;
    uint32_t eax;
};
#endif
