#!/usr/bin/env python3.11

import os, sys, subprocess as sp, parseargs as pa, json, compile_core as cc, logging


logging.root.name = "compile.py"


args = pa.pa("infile:essential:path outfile:essential:path", "compile.py")

infile, outfile = args["infile"], args["outfile"]

core = cc.Core()

basedir = os.path.dirname(os.path.realpath(__file__))

try:
    code = core.compile(infile)
    with open(basedir+"/builtins.asm", "rt") as f:
        code = f.read() + code
except Exception as e:
    print(f"E:"+core.stacktrace()+":"+core.get_error())
    sys.exit(1)

with open(outfile, "wt") as f:
    f.write(code)
