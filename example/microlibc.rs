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

fn itoa(n: int, s: char[]) -> char[] {
    $   lea rbx, [s]
    $   mov rax, [n]
    $   mov rdi, 0
    $   push 0
    $ .cycle:
    $   mov rdx, 0
    $   mov rcx, 10
    $   div rcx
    $   add rdx, 48
    $   push rdx
    $   mov cl, [rsp]
    $   mov [rbx+rdi], cl
    $   test rax, rax
    $   je .done
    $   dec rdi
    $   jmp .cycle
    $ .done:
    $   lea rax, [rbx+rdi]
    return;
}

fn _start(argc: int, argv: char[][]) -> void {
    rbx = main(argc, argv);
    rax = 1;
    $ int 0x80
}
