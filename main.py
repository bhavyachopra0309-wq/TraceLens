import json, os, sys, tkinter as tk
from tkinter import ttk, filedialog, messagebox
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"src"))
from analyzer import analyze, auto_fix
from ai_engine import offline_coach, ollama_coach

SAMPLES={
"Complete Demo":"""int add(int a, int b) {\n    int result = a + b;\n    return result;\n}\n\nint main() {\n    int x = 4;\n    int y = 5;\n    int total;\n    total = add(x, y) + 2 * 3;\n    if (total > 10) {\n        total = total + 0;\n    } else {\n        total = total + 1;\n    }\n    for (int i = 0; i < 3; i++) {\n        total = total + i;\n    }\n    return 0;\n}""",
"Lexical Error":"""int main() {\n    int total = 10 @ 2;\n    return 0;\n}""",
"Syntax Error":"""int main() {\n    int a = 10\n    int b = 20;\n    return 0;\n}""",
"Semantic Errors":"""int main() {\n    int marks = 90;\n    int marks = 80;\n    total = marks + bonus;\n    return 0;\n}""",
"TAC + Optimization":"""int main() {\n    int a = 4 * 5;\n    int b;\n    b = a + 0;\n    return 0;\n}"""}

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("TraceLens AI — 100% Complete Educational Compiler for Restricted C"); self.geometry("1380x820"); self.minsize(1100,680); self.configure(bg="#edf3f8"); self.result=None; self.history=[]; self.build(); self.load_sample("Complete Demo")
    def build(self):
        top=tk.Frame(self,bg="#123b63",height=72); top.pack(fill="x")
        tk.Label(top,text="TraceLens AI",font=("Segoe UI",22,"bold"),fg="white",bg="#123b63").pack(side="left",padx=18,pady=12)
        tk.Label(top,text="100% Final • Restricted-C Compiler Pipeline + Explainable AI",font=("Segoe UI",11),fg="#d9ecff",bg="#123b63").pack(side="left",pady=18)
        body=tk.PanedWindow(self,orient="horizontal",sashwidth=5,bg="#d7e3ef"); body.pack(fill="both",expand=True,padx=10,pady=10)
        left=tk.Frame(body,bg="white"); right=tk.Frame(body,bg="white"); body.add(left,minsize=470); body.add(right,minsize=650)
        bar=tk.Frame(left,bg="white"); bar.pack(fill="x",padx=10,pady=8)
        self.combo=ttk.Combobox(bar,values=list(SAMPLES),state="readonly",width=20); self.combo.pack(side="left"); self.combo.bind("<<ComboboxSelected>>",lambda e:self.load_sample(self.combo.get()))
        ttk.Button(bar,text="Analyze ▶",command=self.run).pack(side="left",padx=4); ttk.Button(bar,text="Safe Auto-Fix",command=self.fix).pack(side="left",padx=4); ttk.Button(bar,text="Clear",command=lambda:self.editor.delete("1.0","end")).pack(side="left")
        tk.Label(left,text="SOURCE CODE — editable restricted C",font=("Segoe UI",10,"bold"),bg="white",fg="#345").pack(anchor="w",padx=10)
        self.editor=tk.Text(left,font=("Consolas",11),undo=True,wrap="none",bg="#fbfdff"); self.editor.pack(fill="both",expand=True,padx=10,pady=(4,10))
        self.tabs=ttk.Notebook(right); self.tabs.pack(fill="both",expand=True,padx=8,pady=8); self.views={}
        for name in ["Dashboard","Pipeline","Tokens","AST","Symbol Table","Diagnostics","TAC","Optimization","AI Coach","History"]:
            f=tk.Frame(self.tabs,bg="white"); self.tabs.add(f,text=name); t=tk.Text(f,font=("Consolas",10),wrap="word",bg="white",relief="flat",padx=10,pady=10); t.pack(fill="both",expand=True); self.views[name]=t
        foot=tk.Frame(right,bg="white"); foot.pack(fill="x",padx=8,pady=(0,8)); ttk.Button(foot,text="Ask Local LLM (Ollama)",command=self.llm).pack(side="left"); ttk.Button(foot,text="Export JSON",command=self.export).pack(side="left",padx=8); self.status=tk.StringVar(value="Ready"); tk.Label(foot,textvariable=self.status,bg="white",fg="#456").pack(side="right")
    def load_sample(self,name): self.combo.set(name); self.editor.delete("1.0","end"); self.editor.insert("1.0",SAMPLES[name])
    def put(self,name,text): self.views[name].config(state="normal"); self.views[name].delete("1.0","end"); self.views[name].insert("1.0",text); self.views[name].config(state="disabled")
    def run(self):
        code=self.editor.get("1.0","end-1c"); self.result=analyze(code); r=self.result; s=r['summary']; self.history.append({"run":len(self.history)+1,"errors":s['error_count'],"warnings":s['warning_count'],"tokens":s['token_count'],"tac":s['tac_count']})
        self.put("Dashboard",f"TRACELENS AI — 100% FINAL DASHBOARD\n\nTokens: {s['token_count']}\nAST nodes: {s['ast_nodes']}\nSymbols: {s['symbol_count']}\nTAC instructions: {s['tac_count']}\nOptimizations applied: {s['optimization_count']}\nErrors: {s['error_count']}\nWarnings: {s['warning_count']}\n\nCOMPLETE WITHIN THE DECLARED RESTRICTED-C SCOPE:\n✓ Lexical analyzer + exact source positions\n✓ Recursive-descent CFG parser + panic-mode recovery\n✓ AST construction\n✓ Scoped symbol table + semantic checks\n✓ Function parameters and calls\n✓ if/else, while, for, return\n✓ Phase-aware diagnostics + deterministic safe fixes\n✓ Three-address intermediate code (TAC)\n✓ Basic machine-independent optimization\n✓ Lightweight RAG knowledge retrieval\n✓ Grounded AI Compiler Coach\n✓ Optional local Llama 3.2 via Ollama\n✓ JSON export + analysis history\n\nScope note: this is intentionally an educational compiler for a restricted subset of C, not a full ANSI-C compiler or machine-code backend.")
        p=r['phases']; self.put("Pipeline",f"SOURCE CODE\n   ↓\nLEXICAL ANALYZER        [{p['Lexical Analysis']}]\n   ↓ tokens\nCFG PARSER              [{p['CFG Parsing']}]\n   ↓\nAST                     [{p['AST Construction']}]\n   ↓\nSEMANTIC ANALYZER       [{p['Semantic Analysis']}]\n   ↕ scoped symbol table\nDIAGNOSTIC / SAFE FIX ENGINE\n   ↓\nINTERMEDIATE CODE (TAC) [{p['Intermediate Code']}]\n   ↓\nOPTIMIZER               [{p['Optimization']}]\n   ↓\nRAG KNOWLEDGE RETRIEVER\n   ↓\nAI COMPILER COACH       [{p['AI/RAG Explanation']}]\n   ↓\nOPTIONAL LOCAL LLM (OLLAMA)\n\nGrounding rule: deterministic compiler evidence is the source of truth; AI only explains it.")
        self.put("Tokens","TYPE\tLEXEME\tLINE:COL\n"+"-"*58+"\n"+"\n".join(f"{t['kind']:<12}{t['lexeme']:<18}{t['line']}:{t['column']}" for t in r['tokens']))
        self.put("AST",r['ast_text']); self.put("Symbol Table","NAME\tTYPE\t\tSCOPE\t\tDECLARED\n"+"-"*70+"\n"+"\n".join(f"{x['name']:<12}{x['type']:<16}{x['scope']:<18}{x['declared_line']}" for x in r['symbols']))
        self.put("Diagnostics","\n\n".join(f"[{d['severity']}] {d['phase']} / {d['code']} @ {d['line']}:{d['column']}\n{d['message']}\nRule: {d['rule']}\nSuggested fix: {d['suggestion']}" for d in r['diagnostics']) or "No diagnostics. Program accepted by the supported restricted-C grammar and semantic rules.")
        self.put("TAC","THREE-ADDRESS / INTERMEDIATE CODE\n"+"="*42+"\n"+"\n".join(r['tac']) if r['tac'] else "TAC not generated because parsing did not complete successfully.")
        self.put("Optimization","OPTIMIZED TAC\n"+"="*42+"\n"+"\n".join(r['optimized_tac'])+"\n\nOPTIMIZATION LOG\n"+"="*42+"\n"+("\n".join(r['optimizations']) or "No safe optimization pattern was applicable."))
        self.put("AI Coach",offline_coach(r)); self.put("History","ANALYSIS HISTORY\n"+"="*42+"\n"+"\n".join(f"Run {h['run']}: {h['errors']} error(s), {h['warnings']} warning(s), {h['tokens']} tokens, {h['tac']} TAC instructions" for h in self.history)); self.status.set(f"Complete: {s['error_count']} errors, {s['warning_count']} warnings")
    def fix(self):
        if not self.result:self.run()
        fixed,changes=auto_fix(self.editor.get("1.0","end-1c"),[type('D',(),d) for d in self.result['diagnostics']])
        if not changes: messagebox.showinfo("TraceLens AI","No safe deterministic auto-fix is available. Ambiguous semantic fixes are intentionally suggestions only."); return
        self.editor.delete("1.0","end"); self.editor.insert("1.0",fixed); self.status.set("; ".join(changes)); self.run()
    def llm(self):
        if not self.result:self.run()
        self.status.set("Querying local Llama 3.2 through Ollama..."); self.update_idletasks(); text,ok=ollama_coach(self.result); self.put("AI Coach",text); self.tabs.select(list(self.views).index("AI Coach")); self.status.set("Local LLM connected" if ok else "Ollama unavailable — grounded fallback shown")
    def export(self):
        if not self.result:self.run()
        p=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")],initialfile="tracelens_analysis.json")
        if p:
            with open(p,"w",encoding="utf-8") as f: json.dump(self.result,f,indent=2)
            self.status.set("Analysis exported")
if __name__=="__main__": App().mainloop()
