# Toolchain file for Intel x86/AMD64 bare-metal (gcc)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR x86)

option(X64    "Indicates whether to generate x86_64 code"    OFF)

set(X64_ARCH_LIST                   "x86-64")
set(X86_ARCH_LIST                   "i386;i486;i586;i686")
set(SUPPORTED_CCONVENTIONS          "sysv;ms")

# User must set TOOLCHAIN_PATH when configuring CMake
if (NOT DEFINED TOOLCHAIN_PATH)
    message(FATAL_ERROR "Please set -DTOOLCHAIN_PATH=/path/to/gcc")
endif ()

if (NOT DEFINED CCONVENTION)
    set (CCONVENTION sysv)
endif ()

if (NOT ${CCONVENTION} IN_LIST SUPPORTED_CCONVENTIONS)
    message(FATAL_ERROR "Invalid calling convention specified!")
endif ()

if (X64)
    if (DEFINED ARCH)
        if (NOT ${ARCH} IN_LIST X64_ARCH_LIST)
            message(FATAL_ERROR "The specified architecture is invalid for x86_64!")
        endif()
    else ()
        set(ARCH x86-64)
    endif ()

    set(X86_BITNESS     64)
    add_compile_definitions(COMPILE_X64)
else ()
    if (DEFINED ARCH)
        if (NOT ${ARCH} IN_LIST X86_ARCH_LIST)
            message(FATAL_ERROR "The specified architecture is invalid for 32-bit x86!")
        endif ()
    else ()
        set(ARCH i686)
    endif()

    set(X86_BITNESS     32)
endif ()
message(STATUS "Using ${ARCH} x86_${X86_BITNESS}")

# Path to compiler binaries
set(TOOLCHAIN_BIN_DIR "${TOOLCHAIN_PATH}/bin")

# Compilers
set(CMAKE_C_COMPILER   "${TOOLCHAIN_BIN_DIR}/gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_BIN_DIR}/g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_BIN_DIR}/gcc")
set(CMAKE_OBJCOPY      "${TOOLCHAIN_BIN_DIR}/objcopy")

# Compiler flags
set(CMAKE_C_FLAGS_INIT "-march=${ARCH} -m${X86_BITNESS} -mabi=${CCONVENTION} -Os -fPIC -nostdlib -ffreestanding -fno-leading-underscore -fno-stack-protector -fno-jump-tables -Wall ${ADDITIONAL_C_FLAGS}")
set(CMAKE_ASM_FLAGS_INIT "-march=${ARCH} -m${X86_BITNESS}")
set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS_INIT})
set(CMAKE_ASM_FLAGS ${CMAKE_ASM_FLAGS_INIT})

# Bare-metal: no OS, minimal runtime
set(CMAKE_EXE_LINKER_FLAGS_INIT "-Wl,--build-id=none ${ADDITIONAL_LINKER_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS  ${CMAKE_EXE_LINKER_FLAGS_INIT} CACHE STRING "Linker flags")

# Search only inside toolchain for headers/libs
set(CMAKE_FIND_ROOT_PATH "${TOOLCHAIN_PATH}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
