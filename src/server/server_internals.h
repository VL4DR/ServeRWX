#pragma once

#include "server/common/common.h"
#include "server/server_conf.h"

typedef uint64_t (*function_t)(value_t arg1, value_t arg2, value_t arg3, value_t arg4);
typedef uint64_t (*shellcode_t)(void);

enum server_transfer_state
{
    TRANSFER_STATE_NONE = 0,
    /* Don't assume bss is actually zeroed-out, use magic value for indication that 
        data is indeed being transferred.
    */
    TRANSFER_STATE_TRANSFERRING_DATA = 0xCAFEBABE,
};

struct server_context
{
#ifdef ALLOCATE_SHELLCODE_BUFFER
    void *shellcode_buffer;
#else
    uint8_t shellcode_buffer[SERVER_SHELLCODE_BUFFER_SIZE];
#endif
    uint32_t shellcode_size;
    enum server_transfer_state transfer_state;
};
