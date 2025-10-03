# Toolchain file for ARM bare-metal (mips-linux-gnu-gcc)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR mips)

set(SUPPORTED_ARCH_LIST         "mips32")

# User must set TOOLCHAIN_PATH when configuring CMake
if (NOT DEFINED TOOLCHAIN_PATH)
    message(FATAL_ERROR "Please set -DTOOLCHAIN_PATH=/path/to/mips-linux-gnu-gcc")
endif ()

if (NOT DEFINED ARCH)
    set(ARCH mips32)
endif ()

message(STATUS "Using architecture ${ARCH}")

# Path to compiler binaries
set(TOOLCHAIN_BIN_DIR "${TOOLCHAIN_PATH}/bin")

# Compilers
set(CMAKE_C_COMPILER   "${TOOLCHAIN_BIN_DIR}/mips-linux-gnu-gcc")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_BIN_DIR}/mips-linux-gnu-gcc")
set(CMAKE_OBJCOPY      "${TOOLCHAIN_BIN_DIR}/mips-linux-gnu-objcopy")

# Compiler flags
set(CMAKE_C_FLAGS_INIT "-march=${ARCH} -EL -nostdlib -fno-pic -mno-abicalls -mno-plt -ffreestanding -fno-stack-protector -Wall ${ADDITIONAL_C_FLAGS}")
set(CMAKE_ASM_FLAGS_INIT "-march=${ARCH} -EL")
set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS_INIT})
set(CMAKE_ASM_FLAGS ${CMAKE_ASM_FLAGS_INIT})

# Bare-metal: no OS, minimal runtime
set(CMAKE_EXE_LINKER_FLAGS_INIT "-Wl,--build-id=none ${ADDITIONAL_LINKER_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS  "${CMAKE_EXE_LINKER_FLAGS_INIT}")

# Search only inside toolchain for headers/libs
set(CMAKE_FIND_ROOT_PATH "${TOOLCHAIN_PATH}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
list(APPEND CMAKE_TRY_COMPILE_PLATFORM_VARIABLES TOOLCHAIN_PATH)
list(APPEND CMAKE_TRY_COMPILE_PLATFORM_VARIABLES ARCH)
