#pragma once

#include "server/common/common.h"

#define SERVER_MAX_DATA_SIZE            (0x100)
#define SERVER_MAGIC                    (0xDEADBEEF)

extern void *server__extract_request_from_context(IN const struct register_context *context);
extern void server__send_response(IN OUT struct register_context *context, IN void *response_data, IN uint32_t response_size);
