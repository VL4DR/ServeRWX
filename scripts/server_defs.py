import construct as cs
from enum import Enum

DEFAULT_MAGIC = 0xDEADBEEF
DEFAULT_MAX_SERVER_DATA_SIZE = 0x100
DEFAULT_SHELLCODE_BUFFER_SIZE = 0x1000

class ServerOpcode(Enum):
    SERVER_OPCODE_NOP = 0,
    SERVER_OPCODE_RESET_STATE = 1
    SERVER_OPCODE_READ = 2
    SERVER_OPCODE_WRITE = 3
    SERVER_OPCODE_CALL = 4
    SERVER_OPCODE_TRANSFER_INITIATE = 5
    SERVER_OPCODE_TRANSFER_DATA = 6
    SERVER_OPCODE_EXECUTE = 7
    SERVER_OPCODE_CUSTOM = 8


class ServerStatus(Enum):
    SERVER_SUCCESS = 0
    SERVER_NULL_PARAMETER = 1
    SERVER_INVALID_PARAMETER = 2
    SERVER_UNIMPLEMENTED = 3
    SERVER_INVALID_MAGIC = 4
    SERVER_INTERNAL_ERROR = 5
    SERVER_INVALID_STATE = 6


ServerRequestHeader = cs.Struct(
    "magic" / cs.Int32ul,
    "opcode" / cs.Int32ul,
    "length" / cs.Int32ul,
    "subcommand" / cs.Int32ul,
    "integrity" / cs.Int32ul,
)


ServerResponseHeader = cs.Struct(
    "magic" / cs.Int32ul,
    "opcode" / cs.Int32ul,
    "length" / cs.Int32ul,
    "status" / cs.Int32ul,
    "integrity" / cs.Int32ul,
)


ServerReadRequest = cs.Struct(
    "address" / cs.Int64ul,
    "size" / cs.Int32ul
)


ServerWriteRequest = cs.Struct(
    "address" / cs.Int64ul
)


ServerCallRequest = cs.Struct(
    "address" / cs.Int64ul,
    "arg1" / cs.Int64ul,
    "arg2" / cs.Int64ul,
    "arg3" / cs.Int64ul,
    "arg4" / cs.Int64ul
)
