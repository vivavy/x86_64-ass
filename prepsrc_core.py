import os, sys, lex, base64 as b64, pprint as pp, tokenize as tk, parse, traceback as tb, logging


logging.root.name = "prepsrc_core.py"


class Core:
    def __init__(self):
        self.stack = []
        self.error = None
        self.line = 0
        self.file = None
        self.src = ""
        self.out = ""
    
    def prepsrc(self, infile):
        self.file = infile
        with open(infile, "rt") as f:
            self.src = f.read()
        
        self.push(infile)

        try:
            data = parse.parse(self.src, self.file)
        except Exception as e:
            if not os.path.exists("log.txt"):
                with open("log.txt", "wt") as f:
                    f.write("\n".join(tuple(tb.format_exception(e))))
            self.error = "Syntax~Error"
            self.push_pos(f"{e.location.line}.{e.location.column}")
            raise Exception

        self.out = data

        return self.out

    def push(self, file):
        self.stack.append(b64.b64encode(file.encode("utf-8")).decode("utf-8"))
    
    def pop(self):
        self.stack.pop()
    
    def push_pos(self, pos):
        self.stack[-1] += "#" + pos
    
    def calc_pos(self, src, pos):
        lineno = src[:pos].count("\n") + 1
        colno = len(src.split("\n")[lineno-1]) - len(src[pos:].split("\n", 1)[0]) + 1
        return f"{lineno}.{colno}"
    
    def stacktrace(self):
        return "`".join(self.stack)

    # deprecated code, still here because i want to keep it for now
    def lex(self):
        # tokenize (lex) source code
        any = lambda *x: r"(" + "|".join(x) + r")"
        all = lambda *x: r"(" + "".join(x) + r")"
        maybe = lambda x: r"(" + x + r")?"
        decInt = r"0[Dd][1-9][0-9]*|[1-9][0-9]*[Dd]|[1-9][0-9]*|0|0[Dd]0?"
        hexInt = r"0[Xx][0-9A-Fa-f]+|[0-9A-Fa-f]+[Hh]|0[Xx]0|0[Hh]"
        octInt = r"0[Oo][0-7]+|[0-7]+[Oo]|0[Oo]0?"
        binInt = r"0[Bb][01]+|[01]+[Bb]|0[Bb]0?"
        allInts = any(decInt, hexInt, octInt, binInt)
        decFltBase = all(decInt, r"\.") + r"|" + all(maybe(decInt), r"\.", decInt)
        decFlt = r"0[Dd]" + decFltBase + r"|" + decFltBase + r"[Dd]" + "|" + decFltBase
        hexFltBase = all(hexInt, r"\.") + r"|" + all(maybe(hexInt), r"\.", hexInt)
        hexFlt = r"0[Xx]" + hexFltBase + r"|" + hexFltBase + r"[Hh]" + "|" + hexFltBase
        octFltBase = all(octInt, r"\.") + r"|" + all(maybe(octInt), r"\.", octInt)
        octFlt = r"0[Oo]" + octFltBase + r"|" + octFltBase + r"[Oo]" + "|" + octFltBase
        binFltBase = all(binInt, r"\.") + r"|" + all(maybe(binInt), r"\.", binInt)
        binFlt = r"0[Bb]" + binFltBase + r"|" + binFltBase + r"[Bb]" + "|" + binFltBase
        allFloats = any(decFlt, hexFlt, octFlt, binFlt)
        numbers = any(allInts, allFloats)
        numbers = tk.Number + r"|" + allInts + r"|" + allFloats
        lexer = lex.Lexer({
            "string": r'"[^"]*"|\'[^\']*\'',
            "inline": r"\$[^\n]*",
            "comment": r"//[^\n]*|/\*[^\*]*\*/",
            "number": numbers,
            "name": r"([A-Za-z_]|\$)([A-Za-z0-9_]|\$)*",
            "lp": r"\(",
            "rp": r"\)",
            "comma": r",",
            "colon": r":",
            "semicolon": r";",
            "lb": r"\[",
            "rb": r"\]",
            "lc": r"\{",
            "rc": r"\}",
            "arrow": r"->",
            "doublearrow": r"=>",
            "lt": r"<",
            "gt": r">",
            "le": r"<=",
            "ge": r">=",
            "ne": r"!=",
            "eq": r"==",
            "minus": r"\-",
            "plus": r"\+",
            "mul": r"\*",
            "div": r"\/",
            "mod": r"\%",
            "and": r"\&",
            "or": r"\|",
            "xor": r"\^",
            "not": r"\~",
            "shl": r"\<\<",
            "shr": r"\>\>",
            "equal": r"=",
        })

        lexer.input(self.src)

        self.tokens = []
        while True:
            token = lexer.token()
            if token is None:
                break
            self.tokens.append(token)
        
        # pp.pprint(self.tokens)
