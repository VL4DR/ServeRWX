#pragma once

#include "server/common/common.h"
#include "commands.h"

#pragma pack(push, 1)
struct request_header
{
    uint32_t magic;
    uint32_t opcode;
    uint32_t length;
    uint32_t subcommand;
    uint32_t integrity;
    uint32_t reserved;
};

struct response_header
{
    uint32_t magic;
    uint32_t opcode;
    uint32_t length;
    uint32_t status;
    uint32_t integrity;
    uint32_t reserved;
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

void server__handle_request(IN struct server_request *request, OUT struct server_response *response);
