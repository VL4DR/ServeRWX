function(server_create_executable target_name)
    set(options "")
    set(oneValueArgs "")
    set(multiValueArgs SOURCES)
    cmake_parse_arguments(SERVER "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(NOT SERVER_SOURCES)
        message(FATAL_ERROR "No sources provided to server_create_executable")
    endif()

    add_executable(${target_name} ${SERVER_SOURCES})
    target_link_libraries(${target_name} PRIVATE server_core)
    target_link_options(${target_name} PRIVATE "-Wl,--whole-archive")
    target_link_options(${target_name} PRIVATE "-T${SERVER_FRAMEWORK_ROOT_DIR}/arch/${CPU}/ldscript.ld")

    message(STATUS "Configured application ${target_name} with server framework")
endfunction()
