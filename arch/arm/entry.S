.global server__entry

.section .server_entry, "ax"

#ifdef THUMB
.syntax unified
.thumb
PUSH.W {R0-R12}
#else
PUSH {R0-R12}
#endif

MOV R0, SP
ADD R0, R0, #0x34
PUSH {R0, LR}
MOV R0, SP
BL server__entry

#ifdef THUMB
POP.W {R0, LR}
POP.W {R0-R12}
#else
POP {R0, LR}
POP {R0-R12}
#endif

BX LR
