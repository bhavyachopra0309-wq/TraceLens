import sys, os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','src'))
from analyzer import analyze
CASES=[
('valid basic','int main(){ int a=1; a=a+2; return 0; }',0),
('lexical','int main(){ int a=1 @ 2; return 0; }',1),
('syntax','int main(){ int a=1 return 0; }',1),
('semantic undeclared','int main(){ x=2; return 0; }',1),
('semantic redeclare','int main(){ int x=1; int x=2; return 0; }',1),
('function','int add(int a,int b){return a+b;} int main(){int x=add(1,2);return 0;}',0),
('for','int main(){int s=0; for(int i=0;i<3;i++){s=s+i;} return 0;}',0),
('if while','int main(){int x=2; while(x>0){x=x-1;} if(x==0){x=x+1;} return 0;}',0),
('type warning','int main(){int x=2.5; return 0;}',0),
('call arity','int f(int a){return a;} int main(){int x=f(1,2);return 0;}',1),
]
passed=0
for name,code,min_errors in CASES:
    r=analyze(code); errors=r['summary']['error_count']; ok=(errors>=min_errors if min_errors else errors==0)
    print(('PASS' if ok else 'FAIL'),name,'errors=',errors,'tac=',r['summary']['tac_count']); passed+=ok
print(f'\n{passed}/{len(CASES)} tests passed')
raise SystemExit(0 if passed==len(CASES) else 1)
