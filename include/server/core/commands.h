#pragma once

#include "server/common/common.h"
#include "server/server_conf.h"

#pragma pack(push, 1)
/* Possible operation codes that the server supports. */
enum server_opcode
{
    SERVER_OPCODE_NOP = 0,
    SERVER_OPCODE_RESET_STATE,
    SERVER_OPCODE_READ,
    SERVER_OPCODE_WRITE,
    SERVER_OPCODE_CALL,
    SERVER_OPCODE_TRANSFER_INITIATE,
    SERVER_OPCODE_TRANSFER_DATA,
    SERVER_OPCODE_EXECUTE,
    SERVER_OPCODE_CUSTOM,
};

/* Request structure for arbitrary memory read.
    `address` - the address from which to start the read operation.
    `size` - the number of bytes to read from the requested address.
*/
struct read_request
{
    uint64_t address;
    uint32_t size;
};

/* Request structure for arbitrary memory write.
    `address` - the address to which the requested data will be written.
    `data` - the data to write to the requested address. This field is variable-length,
    but the total size of this structure cannot exceed `SERVER_MAX_DATA_SIZE` bytes.
*/
struct write_request
{
    uint64_t address;
    uint8_t data[1];
};

/* Request structure for calling arbitrary functions. The calling convention used
    for the called function is the same calling convention used to compile the server.
    `address` - the address of the first byte of the function.
    `arg1` - `arg4` - the parameters to the function.
*/
struct call_request
{
    uint64_t address;
    uint64_t arg1;
    uint64_t arg2;
    uint64_t arg3;
    uint64_t arg4;
};

/* Request structure for initiating a shellcode transfer.
    `shellcode_size` - the size, in bytes, of the shellcode to be transferred. If the shellcode
    has a bss that is assumed to be right after the binary itself, this field must include its size as well. 
*/
struct transfer_initiate_request
{
    uint32_t shellcode_size;
};

/* Request structure for transferring a single shellcode chunk.
    `offset` - the offset within the transfer buffer to place the chunk at. 
    `data` - the chunk data. This field is variable-length, but the total
    size of this structure cannot exceed `SERVER_MAX_DATA_SIZE` bytes. 
*/
struct transfer_data_request
{
    uint32_t offset;
    uint8_t data[1];
};

/* Response structure for reading memory.
    `data` - the data read from memory. This field is variable-length, but
    cannot exceed `SERVER_MAX_DATA_SIZE` bytes.
*/
struct read_response
{
    uint8_t data[1];
};

/* Response structure for calling a function.
    `return_value` - the value returned from the called function.
*/
struct call_response
{
    uint64_t return_value;
};

/* Response structure for executing the accumulated shellcode binary.
    `return_value` - the value returned from executing the shellcode as a function.
*/
struct execute_response
{
    uint64_t return_value;
};

/* A general union holding all the aforementioned requests. */
union request_data
{
    uint8_t as_bytes[SERVER_MAX_DATA_SIZE]; 
    struct read_request as_read_request;
    struct write_request as_write_request;
    struct call_request as_call_request;
    struct transfer_initiate_request as_transfer_initiate_request;
    struct transfer_data_request as_transfer_data_request;
};

/* A general union holding all the aforementioned responses. */
union response_data
{
    uint8_t as_bytes[SERVER_MAX_DATA_SIZE];
    struct read_response as_read_response;
    struct call_response as_call_response;
    struct execute_response as_execute_response;
};
#pragma pack(pop)
