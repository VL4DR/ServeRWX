# Untitled

## What is this?
Untitled is a library which includes a basic implementation of Read-Write-Execute server which can be used for low-level security research.
There any many cases in which full control over some device's firmware is desirable (for example, altering its functionality), and for that matter, it is very useful for security researchers to have the ability to dynamically interact with the device in a low-level manner. Debuggers (like gdb-stub) can be a useful tool to achieve this goal, but they may be unsuitable in certains situations.
In addition, it can be useful in vulnerability exploitation. Not all exploitations are the same, and some might be limited in what they achieve (for example, an exploitation that gives the user the ability to write a very limited amount of bytes to an arbitrary location). In that case, if an exploitation is write-only, Untitled can be used to upgrade the set feature-set of such exploitation to virtually anything.

## Compiling
CMake is used as the configuration environment.
### Compilation cookbook
As this is a library, the user is the one that is supposed to create the final executable. The following components are *required* from the user:
- A toolchain file. This file defines which toolchain to use, compile flags, linker flags, etc. For reference, you can take a look at sample toolchain files for various CPU architectures under `tests/cmake`.
- A linker script. This file defines the memory layout of the final binary, as well as what information to include and exclude from the final binary. For reference, you can take a look at a sample linker script that may be used with gcc-based toolchains at `tests/ld/ldscript.ld`.
- The logic that glues the server to the target firmware. When the library is compiled, it exports a function symbol of the following prototype:
```
void server__handle_request(IN struct server_request *request, OUT struct server_response *response);
```
Before calling this library function, the user must implement the logic that retrieves the request data, as well the logic that passes the server response forward. Roughly, the following pseudo-code describes a typical implementation:
```
#include "server/core/server.h"
// ... more includes

void server_entry()
{
    struct server_request *request = NULL;
    struct server_response response;

    request = get_request();
    server__handle_request(request, &response);
    send_response(&response);
}
```
For reference, you can take a look at the glue logic implemented for testing the server in `tests/src/impl.c`.

Once everything is set up, what is left is to create the final executable by compiling the glue code and linking it with the server library. It is recommended to do this using CMake, since that would also enable the user to use CMake's `FetchContent` to download the library's code into the user's project. For reference, take a look at the CMakeLists.txt file used for building the test binary in `tests/CMakeLists.txt`.

### Required CMake variables
- `CMAKE_TOOLCHAIN_FILE` - this variable is a core CMake variable that holds the path to the toolchain file to use. This is the path to the toolchain file described in the previous section.
### Configurable CMake variables
- `ENABLE_TEST` - this option determines whether to compile a test server binary. If this option is enabled, a server binary which is only applicable for testing using the testing infrastructure found in this repository will be compiled and saved as `build/tests/test_server.bin`. See Tests section down below for more information on how to test this resulting binary.
- `ENABLE_DEBUG` - this option determines whether to output the server's debug messages. If this option is enabled, the user must provide a log function implementation which has the following prototype:
```
void debug__log(IN const char *fmt, ...);
```
The location to which the output messages are sent (console, UART port, network, etc) is up to the user to decide, as they provide the implementation.
The default value for this option is OFF.
- `ALLOCATE_SHELLCODE_BUFFER` - this option determines whether to allocate shellcode space using user-specified memory allocation routine.
As shellcodes need their own space, the user can choose whether to use the server's bss space (in which case the shellcode maximum size is set in advance by the `SERVER_SHELLCODE_BUFFER_SIZE` CMake variable) or allocate memory for the shellcode to execute using a custom implementation. If this option is enabled, the user must provide their own implementation of memory allocate and memory release routines:
```
void *utils__allocate_memory(IN uint32_t size);
void utils__free_memory(IN void *ptr);
```
The default value for this option is OFF.
- `HAVE_EXECUTE_SUPPORT` - this option determines whether to include logic for executing arbitrary shellcodes.
While in most cases it is useful to have support for this feature, there are cases in which it is crucial to keep the server binary as small as possible, so this option can control whether to drop support for this feature in exchange for smaller binary size. If this option is enabled, the user must provide an implementation of an architecture-specific cache-cleaning routine. Typically, that routine would flush a memory block from the processor's data cache to the PoU (point of unification), and in addition to that, would also invalidate the respective memory range within its instruction cache. Some architectures (like x86) do not require such routine, so an empty implementation may be provided (but in any case, it *must* be provided). The prototype of that routine is the following:
```
void arch__clear_cache_range(IN void *base_address, IN uint32_t size);
```
The default value for this option is ON.
- `HAVE_CUSTOM_COMMAND` - this option determines whether there's a custom server command implementation. This option enables the user to extend the server's functionality without modifying its core by providing an implementation of their own to process custom server commands. The server supports a special command named `SERVER_OPCODE_CUSTOM` to support this feature; combined with the request header's `subcommand` field (see `include/server/core/server.h`), one can add support for many additional commands. If this option is enabled, the user must provide a command processing function of the following prototype:
```
enum server_status server__handle_custom_command(IN struct server_request *request, OUT struct server_response *response);
```
The default value for this option is OFF.
- `SERVER_MAX_DATA_SIZE` - This variable sets the maximum data size for server requests and responses, effectively setting the maximum size of a single request/response message.
The default value for this variable is 0x100.
- `SERVER_MAGIC` - This variable sets the server's magic value which must be included in the headers of requests and responses.
The default value for this variable is 0xDEADBEEF.
- `SERVER_SHELLCODE_BUFFER_SIZE` - This variable sets the number of bytes that may be used for the shellcode buffer. This variable is applicable only when `ALLOCATE_SHELCODE_BUFFER` is configured to OFF.
The default value for this variable is 0x1000.

## Limitations
There are some assumptions made during development, which are mostly to keep this repository simple.
- Only 32-bit and 64-bit architectures where a byte equals 8-bits, and byte is the lowest addressable unit are supported. 
- Some minor usage of non-standard pragma statements (like #pragma pack). Some compilers might not like that, but it appears that the major ones should be fine with that.

## Tests
As mentioned before, the `ENABLE_TEST` cmake option determines whether a test server binary should be compiled. This binary is only suitable to be tested by the testing infrastructure defined in this repository.
To test the server, we use `unicorn` to emulate its core functionality. Currently, there is support for testing the server in its *default* configuration built for various ARM architectures, x86, x86_x64 and MIPS.
`pytest` is used as the testing infrastructure of choice.
The test cases themselves can be found in `tests/test_server.py`.
To run the tests:
```
cd tests
pytest test_server.py --server_binary_path ../build/tests/test_server.bin --arch {arm,arm_thumb,aarch64,x86,x86_64,mips}
```

Where the `arch` parameter is the architecture the library was configured to be compiled for by the provided toolchain file.
