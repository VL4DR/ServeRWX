#include "server/common/common.h"
#include "server/utils/utils.h"
#include "server/core/server.h"

#define SERVER_REQUEST_ADDRESS      	(0x51000000)
#define SERVER_REQUEST_REGION_SIZE	    (0x1000)
#define SERVER_RESPONSE_ADDRESS     	(0x52000000)
#define SERVER_RESPONSE_REGION_SIZE	    (0x1000)

static uint32_t g_current_tx_offset = 0;
static uint32_t g_current_rx_offset = 0;

static void send_response(IN struct server_response *response)
{
    uint8_t *current_tx_ptr = NULL;
    uint8_t *end_tx_buffer = (uint8_t *)SERVER_RESPONSE_ADDRESS + SERVER_RESPONSE_REGION_SIZE;
    uint32_t total_length = response->header.length + sizeof(response->header);
    
    current_tx_ptr = (uint8_t *)SERVER_RESPONSE_ADDRESS + g_current_tx_offset;
    if (current_tx_ptr + total_length > end_tx_buffer) {
        g_current_tx_offset = 0;
    }

    utils__memcpy((uint8_t *)SERVER_RESPONSE_ADDRESS + g_current_tx_offset, response, total_length);
    g_current_tx_offset += total_length;
}

static void receive_bytes(OUT void *output, IN uint32_t num_bytes)
{
    uint8_t *current_rx_ptr = NULL;
    uint8_t *end_rx_buffer = (uint8_t *)SERVER_REQUEST_ADDRESS + SERVER_REQUEST_REGION_SIZE;

    current_rx_ptr = (uint8_t *)SERVER_REQUEST_ADDRESS + g_current_rx_offset;
    if (current_rx_ptr + num_bytes > end_rx_buffer) {
        g_current_rx_offset = 0;
    }

    utils__memcpy(output, current_rx_ptr, num_bytes);
    g_current_rx_offset += num_bytes;
}

static void receive_request(OUT struct server_request *request)
{
    receive_bytes(&request->header, sizeof(request->header));
    receive_bytes((uint8_t *)request + sizeof(request->header), request->header.length);
}

void __attribute__((section(".server_entry"))) server__entry()
{
    struct server_request request;
    struct server_response response;

    receive_request(&request);
    server__handle_request(&request, &response);
    send_response(&response);
}

void arch__clear_cache_range(IN void *address, IN uint32_t size)
{
}
