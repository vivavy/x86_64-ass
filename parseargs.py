import sys, logging


logging.root.name = "parseargs.py"


first = sys.argv[0]

if first.startswith("py"):
    sys.argv.pop(0)


def format(args, executable):
    rv = "Using: " + executable + " "
    for name, value in args.items():
        # print(name, value)
        if name == "flags":
            continue
        if value["necessary"]:
            rv += f"<{name}>"
        else:
            rv += f"[{name}]"
        rv += " "
    return rv[:-1]


def pa(args, executable):
    # first we need to parse arguments configuration from `args`
    # then we need to parse arguments from `sys.argv`
    # finally we need to return dictionary of arguments or exit with error
    # if there is no essential arguments

    # first we need to parse arguments configuration from `args`
    config = {
        "flags": [],
    }
    order = []
    for arg in args.split():
        name, flag, typee = arg.split(":")
        necessary = flag == "essential"
        config[name] = {"necessary": necessary, "type": typee, "value": None}
        order.append(name)
    
    # then we need to parse arguments from `sys.argv`
    for arg in sys.argv[1:]:
        if arg.startswith("-"):
            config["flags"].append(arg[1:])
        else:
            config[order[0]]["value"] = arg
            order.pop(0)
    
    # check if there is no essential arguments
    for value in config.values():
        if value.__class__ == list:
            continue
        if value["necessary"] and value["value"] is None:
            print(format(config, executable))
            sys.exit(1)
    
    flags = config["flags"]

    del config["flags"]

    return {**{name: value["value"] for name, value in config.items()}, "flags": flags}
