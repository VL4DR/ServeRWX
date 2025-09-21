#include "server/common/common.h"
#include "server/common/debug.h"
#include "server/common/error.h"
#include "server/arch_defs.h"
#include "utils/utils.h"
#include "server_internals.h"

static enum server_status handle_read_request(IN struct server_request *request, OUT struct server_response *response)
{
    enum server_status status = SERVER_UNKNOWN;
    uint32_t length = request->header.length;
    uint32_t read_size = 0;

    if (length != sizeof(request->data.as_read_request)) {
        DEBUG_LOG("Length parameter (%08x) in header is incorrect!\n", length);
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

    read_size = request->data.as_read_request.size;

    DEBUG_LOG("Reading %08x bytes from the requested address...\n", read_size);
    utils__memcpy(response->data.as_read_response.data, (void *)request->data.as_read_request.address, read_size);

    status = SERVER_SUCCESS;
cleanup:
    return status;
}

static enum server_status handle_write_request(IN struct server_request *request, OUT struct server_response *response)
{
    enum server_status status = SERVER_UNKNOWN;
    uint32_t copy_length = 0;
    uint32_t length = request->header.length;

    if ((length < sizeof(request->data.as_write_request)) ||
        (length > SERVER_MAX_DATA_SIZE)) {
        DEBUG_LOG("Length parameter (%08x) in header is incorrect!\n", length);
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

    copy_length = request->header.length - offsetof(struct write_request, data);

    DEBUG_LOG("Writing %08x bytes to the requested address...\n", copy_length);
    utils__memcpy((void *)request->data.as_write_request.address, request->data.as_write_request.data, copy_length);

    status = SERVER_SUCCESS;
cleanup:
    return status;
}

static enum server_status handle_call_request(IN struct server_request *request, OUT struct server_response *response)
{
    enum server_status status = SERVER_UNKNOWN;
    uint32_t length = request->header.length;
    function_t call_function = NULL;
    value_t return_value = 0;

    if (length != sizeof(request->data.as_call_request)) {
        DEBUG_LOG("Length parameter (%08x) in header is incorrect!\n", length);
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

    DEBUG_LOG("Executing function!\n");
    call_function = (function_t)request->data.as_call_request.address;

    /* @todo this function call's calling convention is the same as the chosen
        calling convention for the server, but there may be several functions with
        different calling conventions in the same binary, see if there's an easy
        way to have the user choose a calling convention here.
    */
    return_value = call_function(request->data.as_call_request.arg1,
                                request->data.as_call_request.arg2,
                                request->data.as_call_request.arg3,
                                request->data.as_call_request.arg4);
    
    response->data.as_call_response.return_value = return_value;

    status = SERVER_SUCCESS;
cleanup:
    return status;
}

static enum server_status dispatch_request(IN struct server_request *request, OUT struct server_response *response)
{
    enum server_status status = SERVER_UNKNOWN;
    enum server_opcode opcode = (enum server_opcode)request->header.opcode;

    DEBUG_LOG("Received opcode %08x!\n", (uint32_t)opcode);

    switch(opcode)
    {
        case SERVER_OPCODE_NOP:
            status = SERVER_SUCCESS;
            break;
        case SERVER_OPCODE_READ:
            status = handle_read_request(request, response);
            break;
        case SERVER_OPCODE_WRITE:
            status = handle_write_request(request, response);
            break;
        case SERVER_OPCODE_CALL:
            status = handle_call_request(request, response);
            break;
        case SERVER_OPCODE_EXECUTE:
        case SERVER_OPCODE_CUSTOM:
            status = SERVER_UNIMPLEMENTED;
            break;
        default:
            DEBUG_LOG("Invalid opcode %08x!\n", (uint32_t)opcode);
            status = SERVER_INVALID_PARAMETER;
            break;
    }

    return status;
}

static void initialize_response(IN struct server_request *request, OUT struct server_response *response)
{
    response->header.magic = SERVER_MAGIC;
    response->header.opcode = request->header.opcode;
    response->header.status = SERVER_UNKNOWN;
}

static void handle_server_request(IN struct server_request *request, OUT struct server_response *response)
{
    enum server_status status = SERVER_UNKNOWN;
    uint32_t magic = request->header.magic;

    initialize_response(request, response);

    if (SERVER_MAGIC == magic) {
        status = dispatch_request(request, response);
    }
    else {
        DEBUG_LOG("Invalid magic detected: %08x\n", magic);
        status = SERVER_INVALID_MAGIC;
    }

    response->header.status = status;
}

void SERVER_ENTRY_ABI server__entry(IN OUT struct register_context *context)
{
    void *input_request = NULL;
    struct server_response response;
    uint32_t response_size = 0;

    utils__memset(&response, 0, sizeof(response));

    input_request = server__extract_request_from_context(context);

    if (NULL != input_request) {
        handle_server_request((struct server_request *)input_request, &response);
        response_size = sizeof(response.header) + response.header.length;
        server__send_response(context, &response, response_size);
    }
}
