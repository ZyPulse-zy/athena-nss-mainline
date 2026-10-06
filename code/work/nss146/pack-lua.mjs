import assert from'node:assert/strict';
// Lexical packing only. Token values, quoted strings and operators are exact.
export function tokens(source){
 assert.equal(typeof source,'string');assert.ok(!/\[=*\[/.test(source),'Multiline Lua literal requires original bytes');
 assert.ok(!source.includes('\\\n')&&!source.includes('\\\r\n'),'Continued quoted Lua literal requires original bytes');
 const out=[];let i=0;
 while(i<source.length){const c=source[i];if(/\s/.test(c)){i++;continue;}
  if(source.startsWith('--',i)){const end=source.indexOf('\n',i);i=end<0?source.length:end+1;continue;}
  if(c==='"'||c==="'"){let end=i+1,closed=false;while(end<source.length){if(source[end]==='\\'){end+=2;continue;}if(source[end]===c){end++;closed=true;break;}assert.ok(source[end]!=='\r'&&source[end]!=='\n','Unclosed string');end++;}assert.ok(closed,'Unclosed string');out.push(source.slice(i,end));i=end;continue;}
  const rest=source.slice(i);let m;
  if(/[0-9]/.test(c)||(c==='.'&&/[0-9]/.test(source[i+1]??''))){m=rest.match(/^(?:0[xX][0-9a-fA-F]+|(?:[0-9]+\.[0-9]+|[0-9]+\.(?!\.)|[0-9]+|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)/);assert.ok(m,'Invalid numeric token');}
  else m=rest.match(/^(?:[A-Za-z_][A-Za-z_0-9]*|\.\.\.|\.\.|==|~=|<=|>=|[+\-*\/%^#=<>;:,(){}\[\].])/);
  assert.ok(m,'Unsupported Lua token at '+i);out.push(m[0]);i+=m[0].length;
 }return out;
}
export function packLua(source){
 const input=tokens(source);let out='';
 for(const t of input){const a=out.at(-1),b=t[0];if(a&&(/[A-Za-z_0-9]/.test(a)&&/[A-Za-z_0-9]/.test(b)||['--','..','==','~=','<=','>=','::','//','<<','>>'].includes(a+b)||(/[0-9]/.test(a)&&b==='.')||(a==='.'&&/[0-9]/.test(b))))out+=' ';out+=t;}
 assert.deepEqual(tokens(out),input,'Lua token stream changed');return out;
}
