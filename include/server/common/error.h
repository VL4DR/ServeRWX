#pragma once

/* Possible server status codes that may be returned to the user. */
enum server_status
{
    SERVER_SUCCESS = 0,
    SERVER_NULL_PARAMETER,
    SERVER_INVALID_PARAMETER,
    SERVER_UNIMPLEMENTED,
    SERVER_INVALID_MAGIC,
    SERVER_INTERNAL_ERROR,
    SERVER_INVALID_STATE,

    SERVER_UNKNOWN = 0x100,
};
