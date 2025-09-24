#include "server/common/common.h"
#include "server/utils/utils.h"

void *utils__memcpy(OUT void *dst, IN void *src, IN uint32_t size)
{
    uint8_t *_dst = (uint8_t *)dst;
    uint8_t *_src = (uint8_t *)src;
    uint32_t i = 0;

    for (i = 0; i < size; i++) {
        _dst[i] = _src[i];
    }

    return dst;
}

void *utils__memset(OUT void *memory, IN uint8_t value, IN uint32_t size)
{
    uint8_t *_memory = (uint8_t *)memory;
    uint32_t i = 0;

    for (i = 0; i < size; i++) {
        _memory[i] = value;
    }

    return memory;
}
