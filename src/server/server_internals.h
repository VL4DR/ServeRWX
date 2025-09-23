#pragma once

#include "server/common/common.h"
#include "server/server_exports.h"
#include "commands.h"

typedef value_t (*function_t)(value_t arg1, value_t arg2, value_t arg3, value_t arg4);
typedef value_t (*shellcode_t)(void);

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

/* @todo some (or all) of these structs are likely to be exported later on to allow users
    to extend the server's functionality.
*/
#pragma pack(push, 1)
struct request_header
{
    uint32_t magic;
    uint32_t opcode;
    uint32_t length;
};

struct response_header
{
    uint32_t magic;
    uint32_t opcode;
    uint32_t length;
    uint32_t status;
};

struct server_request
{
    struct request_header header;
    union request_data data;
};

struct server_response
{
    struct response_header header;
    union response_data data;
};
#pragma pack(pop)
