import logging


logging.root.name = "compile_code.py"


# needed for beautiful typing
class CompCore:
    prep: dict
    code: str
    stack: list[str]
    error: str
    file: str
    scopes: dict[str,dict[str,dict[str,object]]]
    form: dict[str,object]
    current_scope: str


class Core:
    def __init__(self, cc: CompCore):
        self.cc = cc
    
    def compile_func(self, fname):
        logging.debug(f"Compiling function {fname}")

        self.cc.current_scope = fname

        code = ""

        # function name

        code += fname + ":\n"

        # now we need to indent all lines til' function ends

        # function prolog
        code += f"    push rbp\n"
        code += f"    mov rbp, rsp\n"
        if 8*(len(self.cc.scopes[fname])-len(self.cc.prep['functions'][fname]['args'])) > 0:
            code += f"    sub rsp, {8*(len(self.cc.scopes[fname])-len(self.cc.prep['functions'][fname]['args']))}\n"

        # define all locals from function scope
        for name, local in self.cc.scopes[fname].items():
            if local["type"] == "nomod":
                code += f"    {name} equ {name}\n"
            elif local["type"] == "direct":
                code += f"    {name} equ {local['direct']}\n"
            else:
                raise Exception("Lol how you did it? Text me in TG please: https://t.me/vi_chapmann")

        # for every action we need to use dumper
        for action in self.cc.prep["functions"][fname]["body"]:
            code += self.dump(action)
        
        # function prolog, necessary ONLY if function didn't return anyth just before (now detecting is buggy so it's disabled)

        if action["action"] != "return":
            # if self.cc.prep["functions"][fname]["return"]["base"]["value"] == "void" \
            #     and not self.cc.prep["functions"][fname]["return"]["dimensions"]:
            code += f"    leave\n    ret\n"
        
        logging.debug(f"Compiled function {fname}")

        self.cc.current_scope = "global"

        return code
    
    def dump(self, action: dict) -> str:
        # sometimes this func can get `[action]` instead of `action`
        if action.__class__ == list:
            action = action[0]
        logging.debug(f"Dumping action {action}")
        if action["action"] == "call":
            return self.dump_call(action)
        elif action["action"] == "literal":
            logging.debug("This is a literal")
            if action["type"] == "name":
                logging.debug("This is a name")
                if action["value"] in self.cc.form["globs"]:
                    logging.debug("This is a register")
                    return f"    mov rax, {action['value']}\n"
                else:
                    return f"    mov rax, [{action['value']}]\n"
            elif action["type"] == "register":
                logging.debug("This is a register")
                return f"    mov qword rax, {action['value']}\n"
            elif action["type"] == "number":
                logging.debug("This is a number constant")
                return f"    mov qword rax, {action['value']}\n"
        elif action["action"] == "return":
            return self.dump_return(action)
        elif action["action"] == "inline":
            logging.debug("This is an inline assembly")
            return "    " + action["value"].strip() + "\n"
        elif action["action"] == "eq":
            logging.debug("This is an assignment")
            code = self.dump(action["right"])
            left = self.dump_left(action["left"])
            code += f"    mov {left}, rax\n"
        elif action["action"] == "add":
            logging.debug("This is an addition")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    add rax, rbx\n"
        elif action["action"] == "sub":
            logging.debug("This is a subtraction")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    sub rax, rbx\n"
        elif action["action"] == "mul":
            logging.debug("This is a multiplication")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    push rdx\n"
            code += f"    imul rbx\n"
            code += f"    pop rdx\n"
        elif action["action"] == "mod":
            logging.debug("This is a modulo")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    mov rdx, rbx\n"
            code += f"    idiv rbx\n"
            code += f"    mov rax, rdx\n"
        elif action["action"] == "and":
            logging.debug("This is a logical and")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    and rax, rbx\n"
        elif action["action"] == "or":
            logging.debug("This is a logical or")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    or rax, rbx\n"
        elif action["action"] == "xor":
            logging.debug("This is a logical xor")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    xor rax, rbx\n"
        elif action["action"] == "shl":
            logging.debug("This is a shift left")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    shl rax, rbx\n"
        elif action["action"] == "shr":
            logging.debug("This is a shift right")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    shr rax, rbx\n"
        elif action["action"] == "div":
            logging.debug("This is a division")
            code = self.dump(action["left"])
            code += f"    mov rbx, rax\n"
            code += self.dump(action["right"])
            code += f"    div rbx\n"
        elif action["action"].endswith("eq"):
            logging.debug(f"This is a `{action['action'][:-2]}` assignment, subleveling")
            subact = {
                "action": action["action"][:-2],
                "left": action["left"],
                "right": action["right"]
            }
            return self.dump({
                "action": "eq",
                "left": action["left"],
                "right": subact
            })
        try:
            return code
        except NameError:
            logging.debug(f"This is a `{action['action']}` action, no code generated because of unknown or unsupported action")
            return f"    nop  ; `{repr(action)}` coming soon\n"
    
    def dump_call(self, action: dict) -> str:
        logging.debug(f"This is a function call")
        if action["name"]["value"] not in self.cc.scopes[self.cc.current_scope] and \
            action["name"]["value"] not in self.cc.scopes["global"]:
            raise Exception(f"Undefined function `{action['name']}` "
                            f"called from `{self.cc.current_scope}`")
        logging.debug(f"Dumping arguments")
        for arg in action["args"]:
            code = self.dump(arg)
            code += f"    push qword rax\n"
        logging.debug(f"Calling function")
        code += f"    call {action['name']['value']}\n"
        logging.debug(f"Clearing stack")
        code += f"    add qword {self.cc.form['pointers'][1]}, {self.cc.form['pointers'][2]*len(action['args'])}\n"
        return code
    
    def dump_return(self, action: dict) -> str:
        logging.debug(f"This is a return")
        code = ""
        if action["value"] is not None:
            logging.debug("Dumping return value")
            code = self.dump(action["value"])
        code += "    leave\n    ret\n"
        return code
    
    def dump_left(self, action: dict) -> str:
        logging.debug(f"Dumping left part of expression")
        if action.__class__ == list:
            action =    action[0]
        if action.__class__ == dict:
            if action["type"] == "name":
                if action["value"] in self.cc.form["globs"]:
                    return action['value']
                return action['value']
            return action["value"] if action["value"] else action["name"]["value"]
        else:
            return action
