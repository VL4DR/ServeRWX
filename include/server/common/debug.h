#pragma once

#include "common.h"

#ifdef ENABLE_DEBUG
#define DEBUG_LOG(_fmt, ...)       debug__log("[LOG] " _fmt, ##__VA_ARGS__)
#else
#define DEBUG_LOG(_fmt, ...)
#endif
