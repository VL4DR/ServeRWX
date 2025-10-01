# Toolchain file for ARM bare-metal (gcc-aarch64-none-elf)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(SUPPORTED_ARCH_LIST         "armv8-a;armv8-r;armv9-a")

# User must set TOOLCHAIN_PATH when configuring CMake
if (NOT DEFINED TOOLCHAIN_PATH)
    message(FATAL_ERROR "Please set -DTOOLCHAIN_PATH=/path/to/gcc-aarch64-none-elf")
endif ()

if (NOT DEFINED ARCH)
    set(ARCH armv8-a)
endif ()

message(STATUS "Using architecture ${ARCH}")

# Path to compiler binaries
set(TOOLCHAIN_BIN_DIR "${TOOLCHAIN_PATH}/bin")

# Compilers
set(CMAKE_C_COMPILER   "${TOOLCHAIN_BIN_DIR}/aarch64-none-elf-gcc.exe")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_BIN_DIR}/aarch64-none-elf-gcc.exe")
set(CMAKE_OBJCOPY      "${TOOLCHAIN_BIN_DIR}/aarch64-none-elf-objcopy.exe")

# Compiler flags
set(CMAKE_C_FLAGS_INIT "-march=${ARCH} -Os -fPIC -mlittle-endian -nostdlib -ffreestanding -fno-stack-protector -Wall ${ADDITIONAL_C_FLAGS}")
set(CMAKE_ASM_FLAGS_INIT "-march=${ARCH} -mlittle-endian")
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
