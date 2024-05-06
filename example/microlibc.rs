fn strlen(string: char[]) -> int {
    rsi = string;
    rax ^= rax;

    $ .cycle:
    $     cmp byte [rsi], 0
    $     je .done
    $     inc rsi
    $     inc rax
    $     jmp .cycle
    $ .done:
    
    return;
}

fn puts(string: char[]) -> void {
    rdx = strlen(string);
    rbx = 1;
    rcx = string;
    rax = 4;
    $ int 0x80
}

fn _start(argc: int, argv: char[][]) -> void {
    rbx = main(argc, argv);
    rax = 1;
    $ int 0x80
}
