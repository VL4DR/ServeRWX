MEMORY
{
    server_code (rx) : ORIGIN = 0, LENGTH = 0x3000
}

SECTIONS
{
    .text : {
        *(.server_entry)
        *(.text)
    } > server_code

    .data : {
        *(.data)
        *(.rodata)
        *(.got)
    } > server_code

    .bss : {
        *(.bss)
    }

    /DISCARD/ : {
        *(.interp)
        *(.dynsym)
        *(.dynstr)
        *(.hash)
        *(.gnu.hash)
        *(.header)
    } : phdr
}
