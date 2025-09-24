#pragma once

#include "server/common/common.h"

void *utils__memcpy(OUT void *dst, IN void *src, IN uint32_t size);

void *utils__memset(OUT void *memory, IN uint8_t value, IN uint32_t size);
