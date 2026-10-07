// Lossless bounded LZ encoding of JSON data only. Executable Lua tokens are unchanged.
import assert from'node:assert/strict';
export function packJsonData(text){
 const input=Buffer.from(text),out=[],positions=new Map(),literals=[];assert.ok(input.length>0&&input.length<49152);
 const flush=()=>{for(let at=0;at<literals.length;at+=128){const x=literals.slice(at,at+128);out.push(x.length-1,...x);}literals.length=0;};
 const remember=at=>{if(at+2>=input.length)return;const key=input.subarray(at,at+3).toString('hex'),a=positions.get(key)??[];a.push(at);if(a.length>32)a.shift();positions.set(key,a);};
 for(let at=0;at<input.length;){let best=0,distance=0;const key=input.subarray(at,at+3).toString('hex');for(const p of positions.get(key)??[]){const d=at-p;if(d>65535)continue;let n=0;while(n<Math.min(130,d,input.length-at)&&input[p+n]===input[at+n])n++;if(n>best){best=n;distance=d;}}
  if(best>=4){flush();out.push(128+best-3,distance>>>8,distance&255);for(let k=0;k<best;k++)remember(at+k);at+=best;}else{literals.push(input[at]);remember(at++);if(literals.length===128)flush();}}
 flush();const encoded=Buffer.from(out),decoded=[];for(let at=0;at<encoded.length;){const op=encoded[at++];if(op<128){const n=op+1;assert.ok(at+n<=encoded.length);for(let k=0;k<n;k++)decoded.push(encoded[at++]);}else{const n=op-128+3,d=(encoded[at++]<<8)|encoded[at++];assert.ok(d>=n&&d<=decoded.length);const start=decoded.length-d;for(let k=0;k<n;k++)decoded.push(decoded[start+k]);}}
 assert.deepEqual(Buffer.from(decoded),input,'Packed JSON byte mismatch');return{base64:encoded.toString('base64'),decodedBytes:input.length,encodedBytes:encoded.length};
}
export function luaJsonDecoder(p){
 assert.ok(p.decodedBytes>0&&p.decodedBytes<49152);assert.match(p.base64,/^[A-Za-z0-9+/]+=*$/);
 return "local b=assert(require('nixio').bin.b64decode('"+p.base64+"'));local s='';local i=1;while i<=#b do local o=b:byte(i);i=i+1;if o<128 then local n=o+1;assert(i+n-1<=#b);s=s..b:sub(i,i+n-1);i=i+n else assert(i+1<=#b);local n=o-128+3;local d=b:byte(i)*256+b:byte(i+1);i=i+2;assert(d>=n and d<=#s);s=s..s:sub(#s-d+1,#s-d+n)end;assert(#s<49152)end;assert(#s=="+p.decodedBytes+");local p=assert(j.parse(s));";
}
