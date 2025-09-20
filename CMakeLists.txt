cmake_minimum_required(VERSION 3.15)

if (NOT DEFINED CPU)
    message(FATAL_ERROR "Please define the CPU cmake variable!")
endif ()

include(arch/${CPU}/toolchain.cmake)

project(server
    C
    ASM
)

set(SERVER_FRAMEWORK_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR} CACHE STRING "Root directory for the server framework")

set(SERVER_MAX_DATA_SIZE 0x100 CACHE STRING "The maximum data size for server requests and responses")
set(SERVER_MAGIC 0xDEADBEEF CACHE STRING "The magic to be used for the server")

set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS_INIT})

configure_file(src/server/server_exports.h.in
    ${CMAKE_CURRENT_SOURCE_DIR}/include/server/server_exports.h
)

file(COPY arch/${CPU}/arch_defs.h 
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/include/server/
)

set(SERVER_SOURCES  
    src/server/server.c
    src/utils/utils.c
    arch/${CPU}/entry.S
)

add_library(server_core
    ${SERVER_SOURCES}
)

target_include_directories(server_core 
    PUBLIC include
    PRIVATE src
)
