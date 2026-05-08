cmake_minimum_required(VERSION 3.15)

project(server
    C
)

option(ENABLE_TEST  "Determines whether to compile a test server binary" ON)
option(ENABLE_DEBUG "Determines whether to output the server's debug messages" OFF)
option(ALLOCATE_SHELLCODE_BUFFER "Determines whether to allocate shellcode space using user-specified memory allocation routine" OFF)
option(HAVE_CUSTOM_COMMAND "Determines whether there's a custom server command implementation" OFF)
option(SERVER_BIG_ENDIAN    "Determines whether the server code is big-endian based" OFF)

set(SERVER_MAX_DATA_SIZE 0x100 CACHE STRING "The maximum data size for server requests and responses")
set(SERVER_MAGIC 0xDEADBEEF CACHE STRING "The magic to be used for the server")
set(SERVER_SHELLCODE_BUFFER_SIZE 0x1000 CACHE STRING "The number of bytes that may be used for the shellcode buffer")

configure_file(src/server/server_conf.h.in
    ${CMAKE_CURRENT_SOURCE_DIR}/include/server/server_conf.h
)

configure_file(config/config.yaml.in
    ${CMAKE_CURRENT_BINARY_DIR}/config.yaml
)

set(SERVER_SOURCES  
    src/server/server.c
    src/utils/utils.c
)

add_library(server_core
    ${SERVER_SOURCES}
)

if (ENABLE_DEBUG)
    target_compile_definitions(ENABLE_DEBUG)
    message(STATUS "Server is configured in debug mode")
else ()
    message(STATUS "Server is configured in release mode")
endif ()

if (ALLOCATE_SHELLCODE_BUFFER)
    target_compile_definitions(server_core PRIVATE ALLOCATE_SHELLCODE_BUFFER)
    message(STATUS "Server is configured to allocate shellcode buffer")
else ()
    message(STATUS "Server is configured to use bss space of size ${SERVER_SHELLCODE_BUFFER_SIZE} bytes")
endif ()

if (HAVE_CUSTOM_COMMAND)
    target_compile_definitions(server_core PRIVATE HAVE_CUSTOM_COMMAND)
    message(STATUS "Server is configured to include the user's custom command implementation")
else ()
    message(STATUS "Server is configured to exclude the user's custom command implementation")
endif ()

target_include_directories(server_core 
    PUBLIC include
    PRIVATE src
)

if (ENABLE_TEST)
    add_subdirectory(tests)
endif ()
