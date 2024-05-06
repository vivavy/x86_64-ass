format "elf-executable";  /* "elf-32-86_64-object" also works, but it will be unlinked */

import "microlibc.rs";


fn main(argc: int, argv: char[][]) -> int {
    puts("Hello, world!\n");
    return 0;
};
