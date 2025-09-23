#pragma once

#include "server/common/common.h"
#include "server/server_exports.h"
#include "commands.h"

typedef value_t (*function_t)(value_t arg1, value_t arg2, value_t arg3, value_t arg4);

struct server_context
{
    void *shellcode_buffer;
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
