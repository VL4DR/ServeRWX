# Toolchain file for ARM bare-metal (gcc-arm-none-eabi)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# User must set TOOLCHAIN_PATH when configuring CMake
if (NOT DEFINED TOOLCHAIN_PATH)
    message(FATAL_ERROR
        "Please set -DTOOLCHAIN_PATH=/path/to/gcc-arm-none-eabi")
endif ()

if (NOT DEFINED ENDIANESS)
    set(ENDIANESS little)
endif ()
message(STATUS "Using ${ENDIANESS}-endian")

if (NOT DEFINED ARCH)
    set(ARCH armv7-m)
endif ()
message(STATUS "Using architecture ${ARCH}")

if (DEFINED THUMB)
    set(THUMB_COMPILE_FLAG    -mthumb)
    message(STATUS "Using Thumb mode")
else ()
    message(STATUS "Using ARM mode")
endif ()

# Path to compiler binaries
set(TOOLCHAIN_BIN_DIR "${TOOLCHAIN_PATH}/bin")

# Compilers
set(CMAKE_C_COMPILER   "${TOOLCHAIN_BIN_DIR}/arm-none-eabi-gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_BIN_DIR}/arm-none-eabi-g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_BIN_DIR}/arm-none-eabi-gcc")

# Compiler flags
set(CMAKE_C_FLAGS_INIT "-march=${ARCH} ${THUMB_COMPILE_FLAG} -Os -fPIC -m${ENDIANESS}-endian -nostdlib -ffreestanding -fno-stack-protector ${ADDITIONAL_C_FLAGS}")

# Bare-metal: no OS, minimal runtime
set(CMAKE_EXE_LINKER_FLAGS_INIT "-nostdlib ${ADDITIONAL_LINKER_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS  ${CMAKE_EXE_LINKER_FLAGS_INIT} CACHE STRING "Linker flags")

# Search only inside toolchain for headers/libs
set(CMAKE_FIND_ROOT_PATH "${TOOLCHAIN_PATH}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
