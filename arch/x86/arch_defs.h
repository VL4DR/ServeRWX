#pragma once

#include "common.h"

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
