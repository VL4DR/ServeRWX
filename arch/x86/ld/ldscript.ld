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
         *(.rdata)
        *(.got)
    } > server_code

    .bss : {
        *(.bss)
    }
}
