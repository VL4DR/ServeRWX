#pragma once

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define IN
#define OUT
#define OPTIONAL

#define POSSIBLY_UNUSED_VARIABLE(_var)   ((void)(_var))

/* @todo maybe find a better typedef here. */
typedef uint_fast32_t value_t;
