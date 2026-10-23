from dataclasses import dataclass, asdict, field
import re

KEYWORDS={"int","float","char","void","return","if","else","while","for","break","continue"}
TYPE_KEYWORDS={"int","float","char","void"}
TOKEN_SPEC=[
("COMMENT",r"//[^\n]*|/\*[\s\S]*?\*/"),("STRING",r'"(?:\\.|[^"\\])*"'),("CHAR",r"'(?:\\.|[^'\\])'"),
("FLOAT",r"\d+\.\d+"),("INTEGER",r"\d+"),("IDENTIFIER",r"[A-Za-z_][A-Za-z0-9_]*"),
("OPERATOR",r"==|!=|<=|>=|\+\+|--|&&|\|\||[+\-*/%=<>!]"),("DELIMITER",r"[;,(){}\[\]]"),
("NEWLINE",r"\n"),("SKIP",r"[ \t\r]+"),("MISMATCH",r".")]
MASTER=re.compile("|".join(f"(?P<{n}>{p})" for n,p in TOKEN_SPEC))

@dataclass
class Token: kind:str; lexeme:str; line:int; column:int
@dataclass
class Diagnostic:
    phase:str; severity:str; line:int; column:int; message:str; rule:str; suggestion:str; code:str=""
@dataclass
class ASTNode:
    kind:str; value:str=""; children:list=field(default_factory=list); line:int=0
    def to_dict(self): return {"kind":self.kind,"value":self.value,"line":self.line,"children":[c.to_dict() for c in self.children]}

class ParseError(Exception):
    def __init__(self,t,msg,rule="Grammar production not satisfied.",suggestion="Check statement structure and delimiters."):
        self.t=t; self.msg=msg; self.rule=rule; self.suggestion=suggestion

def tokenize(code):
    tokens=[]; ds=[]; line=1; line_start=0
    for m in MASTER.finditer(code):
        kind,text=m.lastgroup,m.group(); col=m.start()-line_start+1
        if kind=="NEWLINE": line+=1; line_start=m.end(); continue
        if kind in {"SKIP","COMMENT"}: continue
        if kind=="MISMATCH":
            ds.append(Diagnostic("Lexical","ERROR",line,col,f"Invalid character '{text}'","Characters must match a valid token pattern in the restricted-C lexical specification.",f"Remove or replace '{text}' with a valid token.","LEX001")); continue
        if kind=="IDENTIFIER" and text in KEYWORDS: kind="KEYWORD"
        tokens.append(Token(kind,text,line,col))
    tokens.append(Token("EOF","<EOF>",line,1)); return tokens,ds

class Parser:
    def __init__(self,tokens): self.ts=tokens; self.i=0; self.ds=[]
    def cur(self): return self.ts[self.i]
    def peek(self,n=1): return self.ts[min(self.i+n,len(self.ts)-1)]
    def accept(self,x):
        if self.cur().lexeme==x: t=self.cur(); self.i+=1; return t
        return None
    def expect(self,x,msg=None):
        t=self.cur()
        if t.lexeme!=x: raise ParseError(t,msg or f"Expected '{x}' but found '{t.lexeme}'",f"Grammar requires '{x}' at this position.",f"Insert '{x}' before '{t.lexeme}'.")
        self.i+=1; return t
    def expect_kind(self,k,msg):
        t=self.cur()
        if t.kind!=k: raise ParseError(t,msg)
        self.i+=1; return t
    def synchronize(self):
        while self.cur().kind!="EOF" and self.cur().lexeme not in {";","}"}: self.i+=1
        if self.cur().lexeme==";": self.i+=1
    def parse(self):
        children=[]
        while self.cur().kind!="EOF":
            try:
                if self.cur().lexeme in TYPE_KEYWORDS and self.peek().kind=="IDENTIFIER" and self.peek(2).lexeme=="(": children.append(self.function())
                else: children.append(self.statement())
            except ParseError as e:
                self.ds.append(Diagnostic("Syntax","ERROR",e.t.line,e.t.column,e.msg,e.rule,e.suggestion,"SYN001")); self.synchronize()
        return ASTNode("Program",children=children),self.ds
    def function(self):
        typ=self.cur(); self.i+=1; name=self.expect_kind("IDENTIFIER","Expected function name"); self.expect("(")
        params=[]
        if self.cur().lexeme!=")":
            while True:
                if self.cur().lexeme not in TYPE_KEYWORDS: raise ParseError(self.cur(),"Expected parameter type")
                pt=self.cur(); self.i+=1; pn=self.expect_kind("IDENTIFIER","Expected parameter name")
                params.append(ASTNode("Parameter",f"{pt.lexeme} {pn.lexeme}",line=pn.line))
                if not self.accept(","): break
        self.expect(")"); body=self.block(); return ASTNode("Function",f"{typ.lexeme} {name.lexeme}",params+[body],typ.line)
    def block(self):
        start=self.expect("{"); xs=[]
        while self.cur().kind!="EOF" and self.cur().lexeme!="}":
            try: xs.append(self.statement())
            except ParseError as e:
                self.ds.append(Diagnostic("Syntax","ERROR",e.t.line,e.t.column,e.msg,e.rule,e.suggestion,"SYN001")); self.synchronize()
        self.expect("}","Expected '}' to close block"); return ASTNode("Block",children=xs,line=start.line)
    def statement(self):
        t=self.cur()
        if t.lexeme=="{": return self.block()
        if t.lexeme in TYPE_KEYWORDS: return self.declaration()
        if t.lexeme=="if": return self.if_stmt()
        if t.lexeme=="while": return self.while_stmt()
        if t.lexeme=="for": return self.for_stmt()
        if t.lexeme=="return": return self.return_stmt()
        if t.lexeme in {"break","continue"}:
            self.i+=1; self.expect(";"); return ASTNode(t.lexeme.capitalize(),line=t.line)
        if t.kind=="IDENTIFIER" and self.peek().lexeme=="=": return self.assignment(True)
        if t.kind=="IDENTIFIER" and self.peek().lexeme=="(":
            n=self.call(); self.expect(";"); return ASTNode("ExprStmt",children=[n],line=t.line)
        raise ParseError(t,f"Unexpected token '{t.lexeme}' at start of statement")
    def declaration(self,need_semicolon=True):
        typ=self.cur(); self.i+=1; name=self.expect_kind("IDENTIFIER","Expected identifier after type"); kids=[]
        if self.accept("="): kids=[self.expr()]
        if need_semicolon:
            if self.cur().lexeme!=";": raise ParseError(self.cur(),f"Missing ';' after declaration of '{name.lexeme}'","Declaration -> type identifier [= expression] ;","Insert ';' at the end of the declaration.")
            self.i+=1
        return ASTNode("Declaration",f"{typ.lexeme} {name.lexeme}",kids,typ.line)
    def assignment(self,need_semicolon=True):
        name=self.cur(); self.i+=1; self.expect("="); e=self.expr()
        if need_semicolon:
            if self.cur().lexeme!=";": raise ParseError(self.cur(),f"Missing ';' after assignment to '{name.lexeme}'","Assignment -> identifier = expression ;","Insert ';' at the end of the assignment.")
            self.i+=1
        return ASTNode("Assignment",name.lexeme,[e],name.line)
    def if_stmt(self):
        t=self.cur(); self.i+=1; self.expect("("); cond=self.expr(); self.expect(")"); yes=self.statement(); kids=[cond,yes]
        if self.accept("else"): kids.append(self.statement())
        return ASTNode("If",children=kids,line=t.line)
    def while_stmt(self):
        t=self.cur(); self.i+=1; self.expect("("); cond=self.expr(); self.expect(")"); body=self.statement(); return ASTNode("While",children=[cond,body],line=t.line)
    def for_stmt(self):
        t=self.cur(); self.i+=1; self.expect("("); kids=[]
        if self.cur().lexeme!=";":
            if self.cur().lexeme in TYPE_KEYWORDS: kids.append(self.declaration(False))
            elif self.cur().kind=="IDENTIFIER" and self.peek().lexeme=="=": kids.append(self.assignment(False))
            else: kids.append(self.expr())
        self.expect(";")
        kids.append(self.expr() if self.cur().lexeme!=";" else ASTNode("Empty")); self.expect(";")
        if self.cur().lexeme!=")":
            if self.cur().kind=="IDENTIFIER" and self.peek().lexeme=="=": kids.append(self.assignment(False))
            elif self.cur().kind=="IDENTIFIER" and self.peek().lexeme in {"++","--"}:
                name=self.cur(); op=self.peek(); self.i+=2; kids.append(ASTNode("Postfix",op.lexeme,[ASTNode("Identifier",name.lexeme,line=name.line)],name.line))
            else: kids.append(self.expr())
        else: kids.append(ASTNode("Empty"))
        self.expect(")"); kids.append(self.statement()); return ASTNode("For",children=kids,line=t.line)
    def return_stmt(self):
        t=self.cur(); self.i+=1; kids=[] if self.cur().lexeme==";" else [self.expr()]; self.expect(";"); return ASTNode("Return",children=kids,line=t.line)
    def call(self):
        name=self.expect_kind("IDENTIFIER","Expected function name"); self.expect("("); args=[]
        if self.cur().lexeme!=")":
            while True:
                args.append(self.expr())
                if not self.accept(","): break
        self.expect(")"); return ASTNode("Call",name.lexeme,args,name.line)
    def expr(self): return self.logical_or()
    def binary(self,sub,ops):
        n=sub()
        while self.cur().lexeme in ops:
            t=self.cur(); self.i+=1; n=ASTNode("BinaryOp",t.lexeme,[n,sub()],t.line)
        return n
    def logical_or(self): return self.binary(self.logical_and,{"||"})
    def logical_and(self): return self.binary(self.equality,{"&&"})
    def equality(self): return self.binary(self.relational,{"==","!="})
    def relational(self): return self.binary(self.additive,{"<",">","<=",">="})
    def additive(self): return self.binary(self.term,{"+","-"})
    def term(self): return self.binary(self.unary,{"*","/","%"})
    def unary(self):
        if self.cur().lexeme in {"!","-","+"}:
            t=self.cur(); self.i+=1; return ASTNode("UnaryOp",t.lexeme,[self.unary()],t.line)
        return self.primary()
    def primary(self):
        t=self.cur()
        if t.kind in {"INTEGER","FLOAT","CHAR","STRING"}: self.i+=1; return ASTNode("Literal",t.lexeme,line=t.line)
        if t.kind=="IDENTIFIER":
            if self.peek().lexeme=="(": return self.call()
            self.i+=1; return ASTNode("Identifier",t.lexeme,line=t.line)
        if self.accept("("):
            n=self.expr(); self.expect(")"); return n
        raise ParseError(t,f"Unexpected token '{t.lexeme}' in expression")

def infer_literal(v):
    if re.fullmatch(r"\d+",v): return "int"
    if re.fullmatch(r"\d+\.\d+",v): return "float"
    if v.startswith("'"): return "char"
    if v.startswith('"'): return "string"
    return "unknown"

def semantic(ast):
    symbols=[]; ds=[]; scopes=[{}]; names=["global"]; functions={}
    # predeclare functions
    for n in ast.children:
        if n.kind=="Function":
            typ,name=n.value.split(maxsplit=1); params=[p.value.split()[0] for p in n.children if p.kind=="Parameter"]
            functions[name]={"type":typ,"params":params}; symbols.append({"name":name,"type":f"function->{typ}","scope":"global","declared_line":n.line})
    def lookup(name):
        for s in reversed(scopes):
            if name in s:return s[name]
    def compatible(dst,src): return src in {"unknown",dst} or (dst=="float" and src=="int")
    def expr_type(n):
        if n.kind=="Literal": return infer_literal(n.value)
        if n.kind=="Identifier":
            x=lookup(n.value)
            if not x: ds.append(Diagnostic("Semantic","ERROR",n.line,1,f"Use of undeclared identifier '{n.value}'","Every identifier use must resolve to a visible symbol-table entry.",f"Declare '{n.value}' before it is used.","SEM002")); return "unknown"
            return x["type"]
        if n.kind=="Call":
            f=functions.get(n.value)
            argtypes=[expr_type(c) for c in n.children]
            if not f: ds.append(Diagnostic("Semantic","ERROR",n.line,1,f"Call to undeclared function '{n.value}'","Function calls must resolve to a declared function.",f"Declare function '{n.value}' before calling it.","SEM004")); return "unknown"
            if len(argtypes)!=len(f['params']): ds.append(Diagnostic("Semantic","ERROR",n.line,1,f"Function '{n.value}' expects {len(f['params'])} argument(s) but got {len(argtypes)}","Function call arity must match the parameter list.","Pass the required number of arguments.","SEM005"))
            return f['type']
        if n.kind=="UnaryOp": return expr_type(n.children[0])
        if n.kind=="BinaryOp":
            a,b=expr_type(n.children[0]),expr_type(n.children[1])
            if n.value in {"<",">","<=",">=","==","!=","&&","||"}: return "int"
            return "float" if "float" in {a,b} else (a if a!="unknown" else b)
        return "unknown"
    def visit(n):
        if n.kind=="Function":
            scopes.append({}); names.append(n.value.split()[-1])
            for p in n.children:
                if p.kind=="Parameter":
                    typ,name=p.value.split(); ent={"name":name,"type":typ,"scope":names[-1],"declared_line":p.line}; scopes[-1][name]=ent; symbols.append(ent)
            for c in n.children:
                if c.kind!="Parameter": visit(c)
            scopes.pop(); names.pop(); return
        if n.kind=="Block":
            for c in n.children: visit(c)
            return
        if n.kind=="Declaration":
            typ,name=n.value.split(maxsplit=1)
            if name in scopes[-1]: ds.append(Diagnostic("Semantic","ERROR",n.line,1,f"Redeclaration of '{name}'","An identifier cannot be declared twice in the same scope.",f"Rename '{name}' or remove the duplicate declaration.","SEM001"))
            else:
                ent={"name":name,"type":typ,"scope":names[-1],"declared_line":n.line}; scopes[-1][name]=ent; symbols.append(ent)
            if n.children:
                rt=expr_type(n.children[0])
                if not compatible(typ,rt): ds.append(Diagnostic("Semantic","WARNING",n.line,1,f"Possible type mismatch: assigning {rt} to {typ} '{name}'","Initializer type should be compatible with declared type.","Use a compatible value or explicit conversion.","SEM003"))
            return
        if n.kind=="Assignment":
            ent=lookup(n.value); rt=expr_type(n.children[0]) if n.children else "unknown"
            if not ent: ds.append(Diagnostic("Semantic","ERROR",n.line,1,f"Assignment to undeclared identifier '{n.value}'","Assignment target must exist in the symbol table.",f"Declare '{n.value}' before assignment.","SEM002"))
            elif not compatible(ent['type'],rt): ds.append(Diagnostic("Semantic","WARNING",n.line,1,f"Possible type mismatch assigning {rt} to {ent['type']} '{n.value}'","Assignment types should be compatible.","Use a compatible expression or conversion.","SEM003"))
            return
        if n.kind=="For":
            scopes.append({}); names.append(names[-1]+"::for")
            for c in n.children: visit(c) if c.kind not in {"BinaryOp","Identifier","Literal","Postfix","Empty"} else expr_type(c.children[0]) if c.kind=="Postfix" else expr_type(c)
            scopes.pop(); names.pop(); return
        if n.kind in {"If","While","Return","ExprStmt"}:
            for c in n.children:
                if c.kind in {"Identifier","Literal","BinaryOp","UnaryOp","Call"}: expr_type(c)
                else: visit(c)
            return
        for c in n.children: visit(c)
    visit(ast); return symbols,ds

def ast_count(n): return 1+sum(ast_count(c) for c in n.children)
def ast_lines(n,prefix="",last=True):
    label=n.kind+(f": {n.value}" if n.value else ""); lines=[prefix+("└── " if last else "├── ")+label]; np=prefix+("    " if last else "│   ")
    for i,c in enumerate(n.children): lines.extend(ast_lines(c,np,i==len(n.children)-1))
    return lines

class TAC:
    def __init__(self): self.lines=[]; self.t=0; self.l=0
    def temp(self): self.t+=1; return f"t{self.t}"
    def label(self): self.l+=1; return f"L{self.l}"
    def expr(self,n):
        if n.kind in {"Literal","Identifier"}: return n.value
        if n.kind=="Call":
            for a in n.children: self.lines.append(f"param {self.expr(a)}")
            t=self.temp(); self.lines.append(f"{t} = call {n.value}, {len(n.children)}"); return t
        if n.kind=="UnaryOp":
            a=self.expr(n.children[0]); t=self.temp(); self.lines.append(f"{t} = {n.value}{a}"); return t
        if n.kind=="BinaryOp":
            a=self.expr(n.children[0]); b=self.expr(n.children[1]); t=self.temp(); self.lines.append(f"{t} = {a} {n.value} {b}"); return t
        return "?"
    def stmt(self,n):
        if n.kind=="Program":
            for c in n.children:self.stmt(c)
        elif n.kind=="Function":
            name=n.value.split()[-1]; self.lines.append(f"func {name}:");
            for c in n.children:
                if c.kind!="Parameter": self.stmt(c)
            self.lines.append(f"endfunc {name}")
        elif n.kind=="Block":
            for c in n.children:self.stmt(c)
        elif n.kind=="Declaration" and n.children: self.lines.append(f"{n.value.split()[-1]} = {self.expr(n.children[0])}")
        elif n.kind=="Assignment": self.lines.append(f"{n.value} = {self.expr(n.children[0])}")
        elif n.kind=="Return": self.lines.append("return"+(" "+self.expr(n.children[0]) if n.children else ""))
        elif n.kind=="ExprStmt": self.expr(n.children[0])
        elif n.kind=="If":
            cond=self.expr(n.children[0]); lelse=self.label(); lend=self.label(); self.lines.append(f"ifFalse {cond} goto {lelse}"); self.stmt(n.children[1]); self.lines.append(f"goto {lend}"); self.lines.append(f"{lelse}:")
            if len(n.children)>2:self.stmt(n.children[2])
            self.lines.append(f"{lend}:")
        elif n.kind=="While":
            start=self.label(); end=self.label(); self.lines.append(f"{start}:"); cond=self.expr(n.children[0]); self.lines.append(f"ifFalse {cond} goto {end}"); self.stmt(n.children[1]); self.lines.append(f"goto {start}"); self.lines.append(f"{end}:")
        elif n.kind=="For":
            self.stmt(n.children[0]) if n.children[0].kind not in {"Empty"} else None; start=self.label(); end=self.label(); self.lines.append(f"{start}:"); cond=self.expr(n.children[1]) if n.children[1].kind!="Empty" else "1"; self.lines.append(f"ifFalse {cond} goto {end}"); self.stmt(n.children[3]);
            upd=n.children[2]
            if upd.kind=="Assignment": self.stmt(upd)
            elif upd.kind=="Postfix": self.lines.append(f"{upd.children[0].value} = {upd.children[0].value} {'+' if upd.value=='++' else '-'} 1")
            self.lines.append(f"goto {start}"); self.lines.append(f"{end}:")
    def generate(self,ast): self.stmt(ast); return self.lines

def optimize_tac(lines):
    out=[]; notes=[]; const={}
    num=re.compile(r"^-?\d+(?:\.\d+)?$")
    for line in lines:
        m=re.match(r"(\w+) = ([\w.\-]+) ([+\-*/%]) ([\w.\-]+)$",line)
        if m:
            dst,a,op,b=m.groups(); av=const.get(a,a); bv=const.get(b,b)
            if num.match(str(av)) and num.match(str(bv)):
                try:
                    x=float(av); y=float(bv); val={'+':x+y,'-':x-y,'*':x*y,'/':x/y if y else None,'%':x%y if y else None}[op]
                    if val is not None:
                        val=int(val) if float(val).is_integer() else val; out.append(f"{dst} = {val}"); const[dst]=str(val); notes.append(f"Constant folding: {line}  →  {dst} = {val}"); continue
                except Exception: pass
            if (op=='+' and b=='0') or (op=='-' and b=='0') or (op=='*' and b=='1') or (op=='/' and b=='1'):
                out.append(f"{dst} = {a}"); notes.append(f"Algebraic simplification: {line}  →  {dst} = {a}"); continue
            if op=='*' and b=='0': out.append(f"{dst} = 0"); notes.append(f"Algebraic simplification: {line}  →  {dst} = 0"); continue
        m2=re.match(r"(\w+) = (-?\d+(?:\.\d+)?)$",line)
        if m2: const[m2.group(1)]=m2.group(2)
        out.append(line)
    return out,notes

def auto_fix(code,diagnostics):
    lines=code.splitlines(); changed=[]
    for d in diagnostics:
        codeid=d.code if hasattr(d,'code') else d.get('code',''); line=d.line if hasattr(d,'line') else d.get('line',0); msg=d.message if hasattr(d,'message') else d.get('message','')
        if codeid=="SYN001" and "Missing ';'" in msg and 1<=line<=len(lines):
            s=lines[line-1].rstrip()
            if s and not s.endswith(';'): lines[line-1]=s+';'; changed.append(f"Inserted ';' on line {line}")
        elif codeid=="LEX001" and 1<=line<=len(lines):
            m=re.search(r"Invalid character '(.+)'",msg)
            if m: lines[line-1]=lines[line-1].replace(m.group(1),'',1); changed.append(f"Removed invalid character on line {line}")
    return "\n".join(lines),changed

def analyze(code):
    tokens,lex=tokenize(code); parser=Parser(tokens); ast,syn=parser.parse(); symbols,sem=semantic(ast); ds=lex+syn+sem
    tac=TAC().generate(ast) if not syn else []; opt,notes=optimize_tac(tac)
    phases={"Lexical Analysis":"FAILED" if lex else "PASSED","CFG Parsing":"FAILED" if syn else "PASSED","AST Construction":"PARTIAL" if syn else "PASSED","Semantic Analysis":"FAILED" if any(d.severity=="ERROR" for d in sem) else ("ISSUES" if sem else "PASSED"),"Intermediate Code":"BLOCKED" if syn else "GENERATED","Optimization":"BLOCKED" if syn else "COMPLETED","AI/RAG Explanation":"READY"}
    real=[t for t in tokens if t.kind!="EOF"]
    return {"tokens":[asdict(t) for t in real],"diagnostics":[asdict(d) for d in ds],"symbols":symbols,"ast":ast.to_dict(),"ast_text":"\n".join(ast_lines(ast)),"tac":tac,"optimized_tac":opt,"optimizations":notes,"phases":phases,"summary":{"token_count":len(real),"ast_nodes":ast_count(ast),"symbol_count":len(symbols),"tac_count":len(tac),"optimization_count":len(notes),"error_count":sum(d.severity=="ERROR" for d in ds),"warning_count":sum(d.severity=="WARNING" for d in ds)}}
