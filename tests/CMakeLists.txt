set(TEST_SOURCES
    ${CMAKE_CURRENT_LIST_DIR}/src/impl.c
)

set(TEST_LINKER_SCRIPT_PATH
    ${CMAKE_CURRENT_LIST_DIR}/ld/ldscript.ld
)

set(TEST_SERVER_ELF_PATH
    ${CMAKE_CURRENT_BINARY_DIR}/test_server
)

set(TEST_SERVER_BINARY_PATH
    ${CMAKE_CURRENT_BINARY_DIR}/test_server.bin
)

add_executable(test_server
    ${TEST_SOURCES}
)

target_link_options(test_server PRIVATE -T${TEST_LINKER_SCRIPT_PATH})
add_dependencies(test_server server_core)
target_link_libraries(test_server server_core)

add_custom_command(TARGET test_server
    POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -j .text -j .data -O binary ${TEST_SERVER_ELF_PATH} ${TEST_SERVER_BINARY_PATH})
