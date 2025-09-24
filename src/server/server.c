#include "server/common/common.h"
#include "server/common/debug.h"
#include "server/common/error.h"
#include "server/core/server.h"
#include "server/core/commands.h"
#include "server/utils/utils.h"
#include "server/server_conf.h"
#include "server_internals.h"

static struct server_context g_server_context;

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

static enum server_status handle_reset_state_request(IN struct server_request *request, OUT struct server_response *response)
{
#ifndef DROP_EXECUTE_SUPPORT
    enum server_status status = SERVER_UNKNOWN;

#ifdef ALLOCATE_SHELLCODE_BUFFER
    if ((TRANSFER_STATE_TRANSFERRING_DATA == g_server_context.transfer_state) &&
        (NULL != g_server_context.shellcode_buffer)) {
            utils__free_memory(g_server_context.shellcode_buffer);
            g_server_context.shellcode_buffer = NULL;
    }
#else /* ALLOCATE_SHELLCODE_BUFFER */
    utils__memset(g_server_context.shellcode_buffer, 0, sizeof(g_server_context.shellcode_buffer));
#endif /* !ALLOCATE_SHELLCODE_BUFFER*/

    g_server_context.transfer_state = TRANSFER_STATE_NONE;
    g_server_context.shellcode_size = 0;

    status = SERVER_SUCCESS;

    return status;
#else /* !DROP_EXECUTE_SUPPORT */
    return SERVER_UNIMPLEMENTED;
#endif /* DROP_EXECUTE_SUPPORT */
}

static enum server_status handle_transfer_initiate_request(IN struct server_request *request, OUT struct server_response *response)
{
#ifndef DROP_EXECUTE_SUPPORT
    enum server_status status = SERVER_UNKNOWN;
    uint32_t length = request->header.length;
    uint32_t transfer_size = 0;
#ifdef ALLOCATE_SHELLCODE_BUFFER
    void *shellcode_buffer = NULL;
#endif /* ALLOCATE_SHELLCODE_BUFFER */

    if (length != sizeof(request->data.as_transfer_initiate_request)) {
        DEBUG_LOG("Length parameter (%08x) in header is incorrect!\n", length);
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

    transfer_size = request->data.as_transfer_initiate_request.shellcode_size;
    if (0 == transfer_size) {
        DEBUG_LOG("Cannot have zero size for shellcode!\n");
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

#ifdef ALLOCATE_SHELLCODE_BUFFER
    shellcode_buffer = utils__allocate_memory(transfer_size);
    if (NULL == shellcode_buffer) {
        DEBUG_LOG("Memory allocation for shellcode failed!\n");
        g_server_context.shellcode_buffer = NULL;
        status = SERVER_INTERNAL_ERROR;
        goto cleanup;
    }

    g_server_context.shellcode_buffer = shellcode_buffer;
#else /* ALLOCATE_SHELLCODE_BUFFER */
    if (transfer_size > SERVER_SHELLCODE_BUFFER_SIZE) {
        DEBUG_LOG("Transfer size exceeds the shellcode buffer size!\n");
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }
#endif /* !ALLOCATE_SHELLCODE_BUFFER */

    g_server_context.shellcode_size = transfer_size;
    g_server_context.transfer_state = TRANSFER_STATE_TRANSFERRING_DATA;
    utils__memset(g_server_context.shellcode_buffer, 0, transfer_size);
    
    status = SERVER_SUCCESS;
cleanup:
    return status;
#else /* !DROP_EXECUTE_SUPPORT */
    return SERVER_UNIMPLEMENTED;
#endif /* DROP_EXECUTE_SUPPORT */
}

static enum server_status handle_transfer_data_request(IN struct server_request *request, OUT struct server_response *response)
{
#ifndef DROP_EXECUTE_SUPPORT
    enum server_status status = SERVER_UNKNOWN;
    uint32_t length = request->header.length;
    uint32_t chunk_offset = 0;
    uint32_t chunk_length = 0;
    uint64_t next_offset = 0;

    if (TRANSFER_STATE_TRANSFERRING_DATA != g_server_context.transfer_state) {
        DEBUG_LOG("Data transfer has not been initiated yet!\n");
        status = SERVER_INVALID_STATE;
        goto cleanup;
    }

    if ((length < sizeof(request->data.as_transfer_data_request)) ||
        (length > SERVER_MAX_DATA_SIZE)) {
        DEBUG_LOG("Length parameter (%08x) in header is incorrect!\n", length);
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

    chunk_offset = request->data.as_transfer_data_request.offset;
    if (chunk_offset >= g_server_context.shellcode_size) {
        DEBUG_LOG("Invalid offset (%08x) provided!\n", chunk_offset)
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

    chunk_length = request->header.length - offsetof(struct transfer_data_request, data);

    next_offset = chunk_offset + chunk_length;
    if (next_offset > g_server_context.shellcode_size) {
        DEBUG_LOG("The given offset (%08x) with size (%08x) would overflow the shellcode buffer!\n", chunk_offset, chunk_length);
        status = SERVER_INVALID_PARAMETER;
        goto cleanup;
    }

    DEBUG_LOG("Transferring shellcode chunk of size %08x bytes...\n", chunk_length);

    utils__memcpy((uint8_t *)g_server_context.shellcode_buffer + chunk_offset, request->data.as_transfer_data_request.data, chunk_length);

    status = SERVER_SUCCESS;
cleanup:
    return status;
#else /* !DROP_EXECUTE_SUPPORT */
    return SERVER_UNIMPLEMENTED;
#endif /* DROP_EXECUTE_SUPPORT */
}

static enum server_status handle_execute_request(IN struct server_request *request, OUT struct server_response *response)
{
#ifndef DROP_EXECUTE_SUPPORT
    enum server_status status = SERVER_UNKNOWN;
    shellcode_t shellcode_entry = NULL;
    value_t return_value = 0;

    if (TRANSFER_STATE_TRANSFERRING_DATA != g_server_context.transfer_state) {
        DEBUG_LOG("Data transfer has not been initiated yet!\n");
        status = SERVER_INVALID_STATE;
        goto cleanup;
    }

    arch__clear_cache_range((address_t)g_server_context.shellcode_buffer, g_server_context.shellcode_size);

    shellcode_entry = (shellcode_t)g_server_context.shellcode_buffer;
    return_value = shellcode_entry();

    response->data.as_execute_response.return_value = return_value;

    status = SERVER_SUCCESS;
cleanup:
    return status;
#else /* !DROP_EXECUTE_SUPPORT */
    return SERVER_UNIMPLEMENTED;
#endif /* DROP_EXECUTE_SUPPORT */
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
        case SERVER_OPCODE_RESET_STATE:
            status = handle_reset_state_request(request, response);
            break;
        case SERVER_OPCODE_TRANSFER_INITIATE:
            status = handle_transfer_initiate_request(request, response);
            break;
        case SERVER_OPCODE_TRANSFER_DATA:
            status = handle_transfer_data_request(request, response);
            break;
        case SERVER_OPCODE_EXECUTE:
            status = handle_execute_request(request, response);
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

void server__handle_request(IN struct server_request *request, OUT struct server_response *response)
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
