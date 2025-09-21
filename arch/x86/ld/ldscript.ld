MEMORY
{
    server_code (rx) : ORIGIN = 0, LENGTH = 0x1000
}

SECTIONS
{
    .text : {
        *(.server_entry)
        *(.text)
    } > server_code

    .data : {
        *(.data)
        *(.rdata)
        *(.reloc)
        *(.got)
    } > server_code

    .bss : {
        *(.bss)
    }
}
