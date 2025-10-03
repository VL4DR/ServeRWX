cmake_minimum_required(VERSION 3.15)

project(server
    C
)

option(ALLOCATE_SHELLCODE_BUFFER "Determines whether to allocate shellcode space using firmware's memory allocation routine" OFF)
option(HAVE_EXECUTE_SUPPORT "Determines whether to include logic of executing arbitrary shellcodes" ON)

set(SERVER_MAX_DATA_SIZE 0x100 CACHE STRING "The maximum data size for server requests and responses")
set(SERVER_MAGIC 0xDEADBEEF CACHE STRING "The magic to be used for the server")
set(SERVER_SHELLCODE_BUFFER_SIZE 0x1000 CACHE STRING "The number of bytes that may be used for the shellcode buffer")

configure_file(src/server/server_conf.h.in
    ${CMAKE_CURRENT_SOURCE_DIR}/include/server/server_conf.h
)

set(SERVER_SOURCES  
    src/server/server.c
    src/utils/utils.c
)

add_library(server_core
    ${SERVER_SOURCES}
)

if (ALLOCATE_SHELLCODE_BUFFER)
    target_compile_definitions(server_core PRIVATE ALLOCATE_SHELLCODE_BUFFER)
    message(STATUS "Server is configured to allocate shellcode buffer")
else ()
    message(STATUS "Server is configured to use bss space of size ${SERVER_SHELLCODE_BUFFER_SIZE} bytes")
endif ()

if (HAVE_EXECUTE_SUPPORT)
    target_compile_definitions(server_core PRIVATE HAVE_EXECUTE_SUPPORT)
    message(STATUS "Server is configured to include shellcode execution logic")
else ()
    message(STATUS "Server is configured without shellcode execution logic")
endif ()

target_include_directories(server_core 
    PUBLIC include
    PRIVATE src
)

add_subdirectory(tests)
