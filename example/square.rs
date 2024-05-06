format "elf-executable";

import "microlibc.rs";

fn main(argc: int, argv: char[][]) -> int {
    $ jmp @f ; locals are broken so far, i will use static heap here
    $ buffer dq $+8
    $ rb 10
    $ db 0
    $ @@:
    puts(itoa(345, buffer));
    return 0;
}
