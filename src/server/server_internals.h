#pragma once

#include "server/common/common.h"
#include "server/server_conf.h"

/* Convenience macros to convert values to the server's endianess.*/
#ifdef SERVER_BIG_ENDIAN
#define CONVERT_ENDIANESS16(_value) ((((_value) >> 8)) | (((_value) & 0xFF) << 8))
#define CONVERT_ENDIANESS32(_value) ((((_value) >> 24)) | ((((_value) >> 16) & 0xFF) << 8) | ((((_value) >> 8) & 0xFF) << 16) | (((_value) & 0xFF) << 24))
#define CONVERT_ENDIANESS64(_value) ((((_value) >> 56)) | ((((_value) >> 48) & 0xFF) << 8) | ((((_value) >> 40) & 0xFF) << 16) | ((((_value) >> 32) & 0xFF) << 24) |\
                                    ((((_value) >> 24) & 0xFF) << 32) | ((((_value) >> 16) & 0xFF) << 40) | ((((_value) >> 8) & 0xFF) << 48) | (((_value) & 0xFF) << 56))
#else
#define CONVERT_ENDIANESS16(_value) (_value)
#define CONVERT_ENDIANESS32(_value) (_value)
#define CONVERT_ENDIANESS64(_value) (_value)
#endif /* SERVER_BIG_ENDIAN */


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
