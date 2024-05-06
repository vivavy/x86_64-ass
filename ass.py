#!/usr/bin/env python3.11

import os, sys, subprocess as sp, parseargs as pa
import logging


logging.root.name = "ass"


print("\n\033[32;1mASsembler Smart (ASS)\033[0;1m ver \033[35;1m0.0.1\033[0;1m by \033[33;1mVi Chapmann\033[0m\n")

os.system("rm -f /tmp/ass.*")

def system(cmd):
    logging.debug("Executing: " + cmd)
    sp.call(cmd, shell=True)


args = pa.pa("infile:essential:path outfile:essential:path", "ass")

if "-debug" in args["flags"]:
    logging.basicConfig(level=logging.DEBUG)

infile, outfile = args["infile"], args["outfile"]

# check if infile or outfile have exploit code

if "$" in infile or "|" in infile or "&" in outfile or "|" in outfile:
    print("\033[31;1mError: exploit detected in paths\033[0m")
    sys.exit(1)


basedir = os.path.dirname(os.path.realpath(__file__))

if "-debug" in args["flags"]:
    logging.info("Debug mode enabled")
    addflags = " --debug"
else:
    addflags = ""

# preprocess infile

logging.debug("Starting preprocessor")
system(f"python3.11 {basedir}/prepsrc.py {infile} /tmp/prepsrc.json" + addflags)

status = open("/tmp/ass.status", 'rt').read()

if status != "''":
    print("\033[31;1mError:\033[0m")
    print("\033[31m    " + "\n    ".join(status.split("\n")) + "\033[0m")
    sys.exit(1)

if "S" in args["flags"]:

    logging.debug("Compile Only option selected")

    # compile infile

    logging.debug("Starting compiler")
    system(f"python3.11 {basedir}/compile.py /tmp/prepsrc.json {outfile}" + addflags)
    
    status = open("/tmp/ass.status", 'rt').read()

    if status != "''":
        print("\033[31;1mError:\033[0m")
        print("\033[31m    " + "\n    ".join(status.split("\n")) + "\033[0m")
        sys.exit(1)
else:

    logging.debug("Default mode selected")

    # compile infile

    logging.debug("Starting compiler")
    system(f"python3.11 {basedir}/compile.py /tmp/prepsrc.json /tmp/comp.asm" + addflags)

    status = open("/tmp/ass.status", 'rt').read()

    if status != "''":
        print("\033[31;1mError:\033[0m")
        print("\033[31m    " + "\n    ".join(status.split("\n")) + "\033[0m")
        sys.exit(1)

    # assemble infile

    logging.debug("Starting assembler")
    try:
        output = sp.check_output(["fasm", "/tmp/comp.asm", outfile])
        logging.debug("Output got from subprocess")
    except sp.CalledProcessError as e:
        logging.debug("Output got from exception")
        output = e.output
    
    out = output.decode("utf-8")

    if "passes" not in out and "bytes" not in out:
        logging.debug("Error dump output got from assembler")
        print("\033[31;1mError: assembler failed, check crush.txt for details\033[0m")

        with open("crush.txt", "wt") as f:
            f.write(out)
        sys.exit(1)

print()
