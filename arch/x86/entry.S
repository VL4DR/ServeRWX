.global server__entry

.section .server_entry, "ax"
push eax
push ebx
push ecx
push edx
push edi
push esi
mov eax, esp
sub eax, 0x18
push eax
mov eax, esp
push esp
call server__entry
add esp, 0x4
pop eax
pop esi
pop edi
pop edx
pop ecx
pop ebx
pop eax
ret
