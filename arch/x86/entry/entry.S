.global server__entry

.section .server_entry, "ax"
.intel_syntax noprefix
#ifdef COMPILE_X64
push rax
push rbx
push rcx
push rdx
push rdi
push rsi
push r8
push r9
push r10
push r11
push r12
push r13
push r14
push r15
mov rax, rsp
add rax, 0x70
push rax
mov rdi, rsp
call server__entry
pop rax
pop r15
pop r14
pop r13
pop r12
pop r11
pop r10
pop r9
pop r8
pop rsi
pop rdi
pop rdx
pop rcx
pop rbx
pop rax
ret

#else
push eax
push ebx
push ecx
push edx
push edi
push esi
mov eax, esp
add eax, 0x18
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
#endif