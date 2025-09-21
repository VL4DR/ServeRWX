#pragma once

#include "common/common.h"

#define SERVER_ENTRY_ABI        __attribute__((pcs("aapcs")))

typedef uint32_t address_t;
typedef uint32_t value_t;

struct register_context
{
    uint32_t sp;
    uint32_t lr;
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t r8;
    uint32_t r9;
    uint32_t r10;
    uint32_t r11;
    uint32_t r12;
};
