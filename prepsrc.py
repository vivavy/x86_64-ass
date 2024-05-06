#!/usr/bin/env python3.11

import os, sys, subprocess as sp, parseargs as pa, prepsrc_core as psc, json, logging, traceback as tb, uuid


logging.root.name = "prepsrc.py"


args = pa.pa("infile:essential:path outfile:optional:path", "prepsrc.py")

if "-debug" in args["flags"]:
    logging.basicConfig(level=logging.DEBUG)

infile, outfile = args["infile"], args["outfile"]

if outfile is None:
    fn = uuid.uuid4().hex[:8]
    logging.debug(f"No outfile specified, using /tmp/ass.prepsrc.{fn}.json")
    outfile = f"/tmp/ass.prepsrc.{fn}.json"

core = psc.Core()

try:
    prepsrc = core.prepsrc(infile)
except Exception as e:
    logging.debug("Error occurred, we need to dump it to /tmp/ass.status, and dump full traceback to /tmp/ass.log")
    with open("/tmp/ass.status", "wt") as f:
        f.write(str(e))
    with open("/tmp/ass.log", "wt") as f:
        f.write(tb.format_exc())
    sys.exit(1)

with open(outfile, "wt") as f:
    json.dump(prepsrc, f, indent=4, sort_keys=True)

logging.debug("Success, dumping \"\" to /tmp/ass.status")
with open("/tmp/ass.status", "wt") as f:
    f.write("''")
