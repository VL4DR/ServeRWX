#pragma once

#include "server/common/common.h"
#include "commands.h"

#pragma pack(push, 1)
/* The request header which holds all the metadata needed to process an incoming request
    to the server. Every server requests begins with this header.
*/
struct request_header
{
    uint32_t magic;
    uint32_t opcode;
    uint32_t length;
    uint32_t subcommand;
    uint32_t integrity;
};

/* The response header which holds all the metadata needed to process a returned response
    from the server. Every server response begins with this header.
*/
struct response_header
{
    uint32_t magic;
    uint32_t opcode;
    uint32_t length;
    uint32_t status;
    uint32_t integrity;
};

/* A structure describing the contents of an entire server request (header and data combined). */
struct server_request
{
    struct request_header header;
    union request_data data;
};

/* A structure describing the contents of an entire server response (header and data combined). */
struct server_response
{
    struct response_header header;
    union response_data data;
};
#pragma pack(pop)

/* Handle a single request to the server and fill the appropriate response information.
    @param request - the incoming request for the server to process.
    @param response - an output parameter that will be filled with the response data after processing
    the given request by the server.
*/
void server__handle_request(IN struct server_request *request, OUT struct server_response *response);
