from pathlib import Path
import ast
p=Path(__file__).resolve().parent/'endpoint-gate/control_harness.py';s=p.read_text();tree=ast.parse(s)
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='prefix' for x in n.targets):
  text=ast.literal_eval(n.value);old='static void check(bool b) { ++checks; assert(b); }';assert text.count(old)==1
  text=text.replace(old,'static void check(bool b) { ++checks; if(!b) fprintf(stderr,"model check failed: %u\\n",checks); assert(b); }')
  lines=s.splitlines(keepends=True);s=''.join(lines[:n.lineno-1])+'prefix='+repr(text)+'\n'+''.join(lines[n.end_lineno:]);break
else:raise AssertionError('prefix absent')
p.write_text(s)
