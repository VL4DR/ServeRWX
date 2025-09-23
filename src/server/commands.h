#pragma once

#include "server/common/common.h"
#include "server/server_exports.h"

enum server_opcode
{
    SERVER_OPCODE_NOP = 0,
    SERVER_OPCODE_READ,
    SERVER_OPCODE_WRITE,
    SERVER_OPCODE_CALL,
    SERVER_OPCODE_TRANSFER_INITIATE,
    SERVER_OPCODE_TRANSFER_DATA,
    SERVER_OPCODE_EXECUTE,
    SERVER_OPCODE_CUSTOM,
};

struct read_request
{
    address_t address;
    uint32_t size;
};

struct write_request
{
    address_t address;
    uint8_t data[1];
};

struct call_request
{
    address_t address;
    value_t arg1;
    value_t arg2;
    value_t arg3;
    value_t arg4;
};

struct transfer_initiate_request
{
    uint32_t shellcode_size;
};

struct transfer_data_request
{
    uint32_t offset;
    uint8_t data[1];
};

struct read_response
{
    uint8_t data[1];
};

struct call_response
{
    value_t return_value;
};

union request_data
{
    uint8_t as_bytes[SERVER_MAX_DATA_SIZE]; 
    struct read_request as_read_request;
    struct write_request as_write_request;
    struct call_request as_call_request;
    struct transfer_initiate_request as_transfer_initiate_request;
    struct transfer_data_request as_transfer_data_request;
};

union response_data
{
    uint8_t as_bytes[SERVER_MAX_DATA_SIZE];
    struct read_response as_read_response;
    struct call_response as_call_response;
};
