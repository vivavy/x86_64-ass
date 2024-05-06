import logging


logging.root.name = "compile_format.py"


def parse(form: str):
    logging.debug(f"Parsing format `{form}`")
    file, *flags = form.lower().split("-")
    bits = 64
    cpu = "86_64"
    pointer_size = None
    for flag in flags:
        if flag.startswith("ps"):
            pointer_size = int(flag[2:])
    return dict(file=file, bits=bits, arch=cpu, flags=flags,
                fasm=comp_fasm(form), globs=get_globals(cpu),
                real_bits=64, pointer_size=pointer_size
                if pointer_size is not None else 8,
                pointers=("rbp", "rsp", pointer_size
                if pointer_size is not None else 8, pointer_size),
                accumulator="rax")


def comp_fasm(form: str):
    logging.debug(f"Compiling format for FASM")
    file, *flags = form.lower().split("-")

    flag = flags[0]

    if file == "elf":
        if flag == "executable":
            return "ELF64 EXECUTABLE 3"
        elif flag == "shared":
            return "ELF64"
        elif flag == "object":
            return "ELF64"
    if file == "pe":
        if flag == "executable":
            flag2 = flags[1]
            if flag2 == "console":
                return "PE64 CONSOLE"
            elif flag2 == "gui":
                return "PE64 GUI 4.0"
            else:
                raise Exception(f"Invalid executable PE class: {flag2}")
        if flag == "shared":
            return "PE64 DLL"
        if flag == "object":
            return "MSCOFF64"
        if flag == "native":
            return "PE64 NATIVE"
        if flag == "efi":
            return "PE64 DLL EFI"
    if file == "mz":
        return "MZ"
    if file == "com":
        return "binary"
    if file == "bin":
        return "binary"


def get_globals(arch: str):
    REG_SIGN = {
                "type": "asis",
                "dtype": {
                    "base": {
                        "action": "literal",
                        "pos": "NaN.NaN",
                        "value": "register"
                    },
                    "dimensions": 0
                }
            }
    if arch == "8088":
        return {
            "al": REG_SIGN,
            "ah": REG_SIGN,
            "bl": REG_SIGN,
            "bh": REG_SIGN,
            "cl": REG_SIGN,
            "ch": REG_SIGN,
            "dl": REG_SIGN,
            "dh": REG_SIGN,
        }
    elif arch == "8086":
        return {
            ** get_globals("8088"),
            "ax": REG_SIGN,
            "bx": REG_SIGN,
            "cx": REG_SIGN,
            "dx": REG_SIGN,
            "si": REG_SIGN,
            "di": REG_SIGN,
            "sp": REG_SIGN,
            "bp": REG_SIGN,
            "ip": REG_SIGN,
            "cs": REG_SIGN,
            "ds": REG_SIGN,
            "ss": REG_SIGN,
            "es": REG_SIGN,
            "fs": REG_SIGN,
            "gs": REG_SIGN,
        }
    
    elif arch == "80286":
        return {
            ** get_globals("8086"),
            "cr0": REG_SIGN,
            "cr1": REG_SIGN,
            "cr2": REG_SIGN,
            "cr3": REG_SIGN,
            "gdtr": REG_SIGN,
            "idtr": REG_SIGN
        }
    elif arch == "80386":
        return {
            ** get_globals("80286"),
            "eax": REG_SIGN,
            "ebx": REG_SIGN,
            "ecx": REG_SIGN,
            "edx": REG_SIGN,
            "esi": REG_SIGN,
            "edi": REG_SIGN,
            "esp": REG_SIGN,
            "ebp": REG_SIGN,
            "eip": REG_SIGN,
            "dr0": REG_SIGN,
            "dr1": REG_SIGN,
            "dr2": REG_SIGN,
            "dr3": REG_SIGN,
        }
    elif arch == "80486":
        return {
            ** get_globals("80386"),
            "tss": REG_SIGN
        }
    elif arch == "80686":
        return {
            ** get_globals("80486"),
            "xmm0": REG_SIGN,
            "xmm1": REG_SIGN,
            "xmm2": REG_SIGN,
            "xmm3": REG_SIGN,
            "xmm4": REG_SIGN,
            "xmm5": REG_SIGN,
            "xmm6": REG_SIGN,
            "xmm7": REG_SIGN,
            "sse0": REG_SIGN,
            "sse1": REG_SIGN,
            "sse2": REG_SIGN,
            "sse3": REG_SIGN,
            "sse4": REG_SIGN,
            "sse5": REG_SIGN,
            "sse6": REG_SIGN,
            "sse7": REG_SIGN,
        }
    elif arch == "86_64":
        return {
            ** get_globals("80686"),
            "msr": REG_SIGN,
            "rax": REG_SIGN,
            "rbx": REG_SIGN,
            "rcx": REG_SIGN,
            "rdx": REG_SIGN,
            "rsi": REG_SIGN,
            "rdi": REG_SIGN,
            "rsp": REG_SIGN,
            "rbp": REG_SIGN,
            "rip": REG_SIGN,
            "r8": REG_SIGN,
            "r9": REG_SIGN,
            "r10": REG_SIGN,
            "r11": REG_SIGN,
            "r12": REG_SIGN,
            "r13": REG_SIGN,
            "r14": REG_SIGN,
            "r15": REG_SIGN,
        }
    else:
        raise Exception(f"Invalid architecture: {arch}")