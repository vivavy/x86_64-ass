import os, sys, time, json, base64 as b64, pprint as pp, compile_format as form, compile_code as cc, uuid, logging


logging.root.name = "compile_core.py"


def uid():
    return "_" + uuid.uuid4().hex[:16]


class Core:
    def __init__(self):
        self.prep = None
        self.code = ""
        self.stack = []
        self.error = ""
        self.file = None
    
    def compile(self, infile):
        self.file = infile

        logging.debug(f"Preprocessing file {self.file}")

        with open(self.file, "rt") as f:
            self.prep = json.load(f)
        
        self.form = form.parse(self.prep["format"]["value"])

        self.cc = cc.Core(self)

        self.get_all_symbols()

        func_code = {}

        for fname in self.prep["functions"].keys():
            func_code[fname] = self.cc.compile_func(fname)

        total_code = ""

        total_code += "format " + self.form["fasm"] + f"\nentry {self.prep['entry']['value'] if self.prep['entry'] is not None else '_start'}\n\n"

        for name, func in func_code.items():
            total_code += f"; function {name}\n"
            total_code += func + "\n\n"
        
        logging.debug(f"Generating predefined symbols")
        for name, value in self.scopes["global"].items():
            logging.debug(f"Generating symbol {name} with config {value}")
            if name in self.prep["functions"] or value["dtype"]["base"]["value"] == "register":
                continue
            total_code += self.gen_symbol_code(name)
        
        total_code += "\n"

        return total_code
    
    def gen_symbol_code(self, name):
        value = self.scopes["global"][name]
        logging.debug(f"Generating code for symbol {name} with config {value}")
        if value["type"]["base"] == "string":
            logging.debug("This is a string")
            val = '"' + value["value"] + '"'
            val = val.replace("\\n", '", 10, "').replace("\\r", '", 13, "').replace("\\b", '", 8, "').\
                replace("\\t", '    ').replace(', ""', "").replace('\\"', "\"\"")
            return f"    {name} string <{val}, 0>\n"
    
    def get_all_symbols(self):
        logging.debug(f"Getting all symbols list for scopes")
        self.scopes = {
            "global": {**self.form["globs"]}
        }
        self.current_scope = "global"

        for name, func in self.prep["functions"].items():
            logging.debug(f"Getting symbols for function {name}")
            self.scopes["global"][name] = {
                "type": "function",
                #"inner-data": {
                #    "args": b64.b64encode(json.dumps(func["args"]).encode()).decode(),
                #    "rtype": b64.b64encode(json.dumps(func["return"]).encode()).decode(),
                #},
                "args": func["args"],
                "rtype": func["return"]
            }
            self.scopes[name] = {}
            self.current_scope = name

            i = self.form["pointer_size"] + self.form["real_bits"] // 8
            for arg in func["args"]:
                self.scopes[name][arg["name"]["value"]] = {"dtype": arg["type"], "direct": f"rbp+{i}", "type": "direct"}
                i += self.form["real_bits"] // 8

            for action in func["body"]:
                self.gen_symbol(action, False)
    
    def throw(self, data):
        self.error = data.replace("\t", " ").replace(" ", "~").replace(":", "@")
    
    def gen_symbol(self, act: dict[str,object], detect_unbound=True):
        logging.debug(f"Generating symbol for action {act}")
        if act.__class__ == list:
            act = act[0]
        if act["action"] == "call":
            if detect_unbound:
                if act["name"]["value"] not in self.scopes["global"] and act["name"]["value"] not in self.scopes[self.current_scope]:
                    self.throw(f"Unbound variable: {act['name']}")
            for subact in act["args"]:
                self.gen_symbol(subact, detect_unbound)
        elif "left" in act.keys() and "right" in act.keys():
            self.gen_symbol(act["left"])
            self.gen_symbol(act["right"])
        elif act["action"] == "return" and act["value"] is not None or "mode" in act.keys():
            self.gen_symbol(act["value"])
        
        # literals
        elif act["action"] == "literal":
            logging.debug("This is a literal")
            if act["type"] == "name":
                logging.debug("This is a name")
                if detect_unbound:
                    if act["value"] not in self.scopes[self.current_scope] and act["value"] not in self.scopes["global"]:
                        self.throw(f"Unbound variable: {act['value']}")
            elif act["type"] == "register":
                logging.debug("This is a register")
            elif act["type"] == "string":
                logging.debug("This is a string")
                name = uid()
                # print("DEBUG:", name)
                self.scopes["global"][name] = {
                    "type": {
                        "base": "string",
                        "dimensions": 0
                    },
                    "value": act["value"],
                    "dtype": {
                        "base": {
                            "value": "string",
                            "type": "name",
                            "action": "literal"
                        },
                        "dimensions": 0
                    }
                }
                act["type"] = "name"
                act["value"] = name
