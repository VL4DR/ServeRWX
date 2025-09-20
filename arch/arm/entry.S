.global server__entry

.section .server_entry, "ax"
PUSH {R0-R12}
MOV R0, SP
SUB R0, R0, #0x34
PUSH {R0, LR}
MOV R0, SP
BL server__entry
POP {R0, LR}
POP {R0-R12}
BX LR
