#pragma once

#include "server/common/common.h"

#define SERVER_MAX_DATA_SIZE            (0x100)
#define SERVER_MAGIC                    (0xDEADBEEF)

#ifndef ALLOCATE_SHELLCODE_BUFFER
#define SERVER_SHELLCODE_BUFFER_SIZE    (0x1000) 
#endif

#ifdef ADDRESS_64
typedef uint64_t address_t;
#else /* ADDRESS_64 */
typedef uint32_t address_t;
#endif /* !ADDRESS_64 */

#ifdef VALUE_64
typedef uint64_t value_t;
#else /* VALUE_64 */
typedef uint32_t value_t;
#endif /* !VALUE_64 */

#ifdef ALLOCATE_SHELLCODE_BUFFER
extern void *utils__allocate_memory(IN uint32_t size);
extern void utils__free_memory(IN void *ptr);
#endif
