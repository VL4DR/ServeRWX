# Toolchain file for ARM bare-metal (gcc-arm-none-eabi)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

option(THUMB    "Indicates whether to generate Thumb-2 code"    OFF)

set(SUPPORTED_ARCH_LIST         "armv4t;armv5t;armv6;armv6t2;armv6-m;armv7-m;armv7-a;armv7-r")
set(THUMB2_SUPPORT_ARCH_LIST    "armv6t2;armv6-m;armv7-m")
set(THUMB2_ONLY_ARCH_LIST       "armv6-m;armv7-m")

# User must set TOOLCHAIN_PATH when configuring CMake
if (NOT DEFINED TOOLCHAIN_PATH)
    message(FATAL_ERROR "Please set -DTOOLCHAIN_PATH=/path/to/gcc-arm-none-eabi")
endif ()

if (NOT DEFINED ENDIANESS)
    set(ENDIANESS little)
endif ()
message(STATUS "Using ${ENDIANESS}-endian")

if (NOT DEFINED ARCH)
    set(ARCH armv7-m)
endif ()

if (NOT ${ARCH} IN_LIST SUPPORTED_ARCH_LIST)
    message(FATAL_ERROR "Unsupported ARM architecture specified!")
endif ()
message(STATUS "Using architecture ${ARCH}")

if (THUMB)
    if (NOT ${ARCH} IN_LIST THUMB2_SUPPORT_ARCH_LIST)
        message(FATAL_ERROR "The selected ARM architecture does not support Thumb-2!")
    endif()
    set(THUMB_COMPILE_FLAG    -mthumb)
    add_compile_definitions(THUMB)
    message(STATUS "Using Thumb mode")
else ()
    if (${ARCH} IN_LIST THUMB2_ONLY_ARCH_LIST)
        message(FATAL_ERROR "The selected ARM architecture does not support ARM mode!")
    endif ()
    message(STATUS "Using ARM mode")
endif ()

# Path to compiler binaries
set(TOOLCHAIN_BIN_DIR "${TOOLCHAIN_PATH}/bin")

# Compilers
set(CMAKE_C_COMPILER   "${TOOLCHAIN_BIN_DIR}/arm-none-eabi-gcc")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_BIN_DIR}/arm-none-eabi-gcc")
set(CMAKE_OBJCOPY      "${TOOLCHAIN_BIN_DIR}/arm-none-eabi-objcopy")

# Compiler flags
set(CMAKE_C_FLAGS_INIT "-march=${ARCH} ${THUMB_COMPILE_FLAG} -Os -fPIC -m${ENDIANESS}-endian -nostdlib -ffreestanding -fno-stack-protector -Wall ${ADDITIONAL_C_FLAGS}")
set(CMAKE_ASM_FLAGS_INIT "-march=${ARCH} -m${ENDIANESS}-endian")
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
list(APPEND CMAKE_TRY_COMPILE_PLATFORM_VARIABLES TOOLCHAIN_PATH)
list(APPEND CMAKE_TRY_COMPILE_PLATFORM_VARIABLES ARCH)
