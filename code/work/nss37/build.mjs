import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss37',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest=JSON.parse(fs.readFileSync(root+'/original-manifest.json'));let source=fs.readFileSync(root+'/original-conntrack-source.lua','utf8');
assert.equal(hash(Buffer.from(source)),manifest.files['conntrack-source.lua']);
const old="local function attrs(line,k)local a={};for v in (line..' '):gmatch('%s'..k..'=(%S+)')do a[#a+1]=v end;return a end";
const replacement=[
 "local function attrs(line,k)",
 " -- Literal key search avoids a full Lua-pattern scan for each attribute.",
 " -- Keep the original whitespace boundary, nonempty value and duplicate semantics.",
 " local values,at,needle={},1,k..'='",
 " while true do",
 "  local first,last=line:find(needle,at,true);if not first then break end",
 "  at=last+1",
 "  if first>1 and line:sub(first-1,first-1):match('%s')then",
 "   local a,b=line:find('^%S+',at)",
 "   if a then values[#values+1]=line:sub(a,b);at=b+1 end",
 "  end",
 " end",
 " return values",
 "end"
].join('\n');
assert.equal(source.split(old).length,2);source=source.replace(old,()=>replacement);
fs.writeFileSync(root+'/conntrack-source.lua',source);
fs.writeFileSync(root+'/candidate-manifest.json',JSON.stringify({basedOn:manifest.configSha256,onlyAttributeSearchChanged:true,sourceSha256:hash(Buffer.from(source)),originalSha256:manifest.files['conntrack-source.lua'],routerWrites:false},null,2)+'\n');
console.log(JSON.stringify({built:true,onlyAttributeSearchChanged:true,sha256:hash(Buffer.from(source)),routerWrites:false}));
