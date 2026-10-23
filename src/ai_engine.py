import json, math, os, re, urllib.request
KB=[
{"id":"LEX001","title":"Invalid lexical token","text":"Lexical analysis converts characters into valid tokens. An unmatched character fails before parsing."},
{"id":"SYN001","title":"Grammar or punctuation error","text":"Syntax analysis validates token order against CFG productions. Missing semicolons, parentheses, braces or malformed statements are syntax errors."},
{"id":"SEM001","title":"Redeclaration","text":"Semantic analysis uses a scoped symbol table. The same identifier cannot be declared twice in one scope."},
{"id":"SEM002","title":"Undeclared identifier","text":"Every identifier use must resolve to a visible symbol-table entry. This demonstrates declaration-before-use and scope."},
{"id":"SEM003","title":"Type compatibility","text":"Semantic analysis checks type compatibility in declarations, assignments and expressions."},
{"id":"SEM004","title":"Function resolution","text":"A function call must resolve to a declared function."},
{"id":"SEM005","title":"Function arity","text":"The number of call arguments must match the declared parameter list."},
{"id":"AST","title":"Abstract Syntax Tree","text":"An AST represents hierarchical program structure and precedence while removing unnecessary punctuation."},
{"id":"TAC","title":"Three-address code","text":"Intermediate code lowers expressions and control flow into simple temporary assignments, labels and jumps."},
{"id":"OPT","title":"Optimization","text":"Machine-independent optimization can simplify TAC using constant folding and algebraic identities without changing meaning."}]
def words(s): return re.findall(r"[a-z0-9]+",s.lower())
def retrieve(query,k=4):
    q=set(words(query)); scored=[]
    for d in KB:
        ws=words(d['id']+' '+d['title']+' '+d['text']); score=sum(ws.count(w) for w in q)/(math.sqrt(len(ws))+1); scored.append((score,d))
    return [d for _,d in sorted(scored,key=lambda x:x[0],reverse=True)[:k]]
def build_context(result):
    ds=result.get('diagnostics',[]); q=' '.join(d.get('code','')+' '+d.get('message','') for d in ds) or 'valid program AST symbol table TAC optimization'
    return '\n'.join(f"[{d['id']}] {d['title']}: {d['text']}" for d in retrieve(q))
def offline_coach(result):
    ds=result.get('diagnostics',[]); s=result.get('summary',{}); ctx=build_context(result)
    if ds:
        d=ds[0]; body=f"Primary issue: {d['phase']} {d['severity']} ({d['code']}) on line {d['line']}.\nRoot cause: {d['rule']}\nMinimal correction: {d['suggestion']}"
    else: body="No compiler errors were detected in the supported restricted-C subset. The deterministic pipeline accepted the program."
    return f"AI COMPILER COACH — GROUNDED FALLBACK\n\n{body}\n\nCompiler evidence: {s.get('token_count',0)} tokens, {s.get('ast_nodes',0)} AST nodes, {s.get('symbol_count',0)} symbols, {s.get('tac_count',0)} TAC instructions, {s.get('error_count',0)} errors.\n\nRetrieved knowledge (lightweight RAG):\n{ctx}\n\nGuardrail: compiler algorithms decide correctness. AI only explains verified evidence."
def ollama_coach(result,model=None):
    model=model or os.getenv('TRACELENS_LLM_MODEL','llama3.2')
    prompt=f"""You are TraceLens AI Compiler Coach for a Compiler Design lab. The deterministic compiler result below is the only source of truth. Do not invent errors. Explain to a beginner: (1) phase, (2) root cause, (3) failed compiler concept, (4) minimal fix, (5) why it belongs to that phase, (6) one viva learning tip.\n\nDIAGNOSTICS:\n{json.dumps(result.get('diagnostics',[]),indent=2)}\n\nSUMMARY:\n{json.dumps(result.get('summary',{}),indent=2)}\n\nRETRIEVED KNOWLEDGE:\n{build_context(result)}"""
    payload=json.dumps({'model':model,'prompt':prompt,'stream':False}).encode(); req=urllib.request.Request('http://localhost:11434/api/generate',data=payload,headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=45) as r: return json.loads(r.read().decode()).get('response','').strip(),True
    except Exception as e: return offline_coach(result)+f"\n\nLocal LLM status: unavailable ({type(e).__name__}).",False
