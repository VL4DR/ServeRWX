#pragma once

#include "common.h"

#ifdef ENABLE_DEBUG
#define DEBUG_LOG(...)       fw__log("[LOG] " __VA_ARGS__)
#else
#define DEBUG_LOG(...)
#endif
