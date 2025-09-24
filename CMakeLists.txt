cmake_minimum_required(VERSION 3.15)

project(server
    C
    ASM
)

set(SERVER_MAX_DATA_SIZE 0x100 CACHE STRING "The maximum data size for server requests and responses")
set(SERVER_MAGIC 0xDEADBEEF CACHE STRING "The magic to be used for the server")

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

target_include_directories(server_core 
    PUBLIC include
    PRIVATE src
)
