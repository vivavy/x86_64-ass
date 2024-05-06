import parglare as pg, os, sys, base64 as b64, json, uuid
import parglare.parser as pgt, logging


logging.root.name = "parse.py"


basedir = os.path.dirname(os.path.realpath(__file__))


gram = pg.Grammar.from_file(basedir+'/gram.pg')


data = {
    "format": None,
    "entry": None,
    "includes": [],
    "functions": {},
}


def comment(stack, node):
    return None


def format(stack, node):
    data['format'] = {"pos": node[1]["pos"], "value": node[1]["value"]}
    return None


def entry(stack, node):
    data['entry'] = {"pos": node[1]["pos"], "value": node[1]["value"]}
    return None


def import_(stack, node):
    if "&" in node[1]["value"] or "||" in node[1]["value"]:
        raise Exception("Exploit Attempt")
    path = node[1]["value"].removesuffix(".rs") + ".rs"
    path = os.path.join(os.path.dirname(data['file']), path)
    basedir = os.path.dirname(os.path.realpath(__file__))
    targ = "ass.prepsrc." + uuid.uuid4().hex[:8] + ".json"
    CMD = "python3.11 " + basedir+"/prepsrc.py " + repr(path).replace("'", '"') + " " + targ
    os.system(CMD)
    status = open("/tmp/ass.status", "rt").read()
    if status != "''":
        sys.exit(1)
    data["includes"].append(targ)
    return None


def root(stack, node):
    node = node[0]
    for child in node:
        if child == [None, ";"] or child is None:
            del node[node.index(child)]
    return node

def function(stack, node):
    name = node[1]["value"]
    args = node[3]
    rtyp = node[6]
    body = node[7]
    data["functions"][name] = {
        "args": args,
        "return": rtyp,
        "body": body,
        "pos": node[1]["pos"]
    }
    return None


def _list(stack, node):
    # we have: [first, [[",", second], [",", third], ...]]
    # we need: [first, second, third, ...]
    rv = [node[0]]
    if node[1]:
        for i in node[1]:
            rv.append(i[1])
    return rv


def code_block(stack, node):
    rv = [node[1]] + node[2] if node[2] else []
    while None in rv:
        rv.remove(None)
    return rv


def code_line_1(stack, node):
    return node

def code_line_2(stack, node):
    return node[0]

def code_line_3(stack, node):
    return {"action": "return", "value": node[1][0] if node[1] is not None else None, "pos": get_pos(stack)}

def code_line_4(stack: pgt.LRStackNode, node):
    return {"action": "inline", "value": node[0][1:].strip(), "pos": get_pos(stack)}

def code_line_5(stack, node):
    return None

def function_call(stack, node):
    return {"action": "call", "name": node[0], "args": _list(stack, node[2]) if node[2] else []}

def get_pos(stack: pgt.LRStackNode):
    l, c = pg.pos_to_line_col(data['src'], stack.position)
    return f"{l}.{c}"


acts = {
    'root': root,
    'format_definition': format,
    'comment': comment,
    'entry_definition': entry,
    'root_statement': lambda _, n: None if n == [None] else n[0],
    'import_definition': import_,
    'function_definition': function,
    'type': lambda _, n: {"base": n[0], "dimensions": len(n[1])},
    'typer': lambda _, n: {"name": n[0], "type": n[2]},
    'types_list': _list,
    'code_block': code_block,
    'code_line': [
        code_line_1,
        code_line_2,
        code_line_3,
        code_line_4,
        code_line_5,
    ],
    'function_call': function_call,
    'expression': [                      #  this part of code was written manually)))
        lambda _, n: {"action": "land", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "lor", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "lxor", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "isequal", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "isnotequal", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "lt", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "le", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "gt", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "ge", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "not", "value": n[1]},
        lambda _, n: {"action": "neg", "value": n[1]},
        lambda _, n: {"action": "pow", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "mul", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "div", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "mod", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "shl", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "shr", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "and", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "or", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "xor", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "add", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "sub", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "landeq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "loreq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "lxoreq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "noteq", "value": n[1]},
        lambda _, n: {"action": "negeq", "value": n[1]},
        lambda _, n: {"action": "poweq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "muleq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "diveq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "modeq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "shleq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "shreq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "andeq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "oreq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "xoreq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "addeq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "subeq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "eq", "left": n[0], "right": n[2]},
        lambda _, n: {"action": "inc", "value": n[0], "mode": "post"},
        lambda _, n: {"action": "dec", "value": n[0], "mode": "post"},
        lambda _, n: {"action": "inc", "value": n[0], "mode": "pre"},
        lambda _, n: {"action": "dec", "value": n[0], "mode": "pre"},
        lambda _, n: n,
        lambda _, n: n,
        lambda _, n: n,
        lambda _, n: n[0],  # parentheses
        lambda _, n: {"action": "array", "from": n[0], "by": n[2]},
        lambda _, n: {"action": "ternary", "cond": n[0], "true": n[2], "false": n[4]},
        lambda _, n: n[0],  # function call
    ],
    "name": lambda _, n: {"action": "literal", "type": "name", "value": n, "pos": get_pos(_)},
    "string": lambda _, n: {"action": "literal", "type": "string", "value": n[1:-1], "pos": get_pos(_)},
    "number": lambda _, n: {"action": "literal", "type": "number", "value": n, "pos": get_pos(_)},
}

parser = pg.Parser(grammar=gram, actions=acts)

def parse(src, file):
    data['src'] = src
    data['file'] = file
    parser.parse(src)
    del data['src']

    for inc in data["includes"]:
        with open(inc, "rt") as f:
            newdata = json.load(f)
            data["functions"].update(newdata["functions"])
        os.remove(inc)
        data["includes"].remove(inc)

    return data
