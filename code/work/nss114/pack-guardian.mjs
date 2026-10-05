import assert from'node:assert/strict';import{packLua}from'./pack-lua.mjs';
// These are the only multiline-literal syntax sites in the fixed guardian.
// Preserve them exactly while removing formatting around executable code.
export function packGuardian(source){
 const literals=['__PLAN__','__CORE_PHASE__','__QOS_PHYSICAL__'];let s=source;
 for(const [i,name]of literals.entries()){const raw='[=['+name+']=]';assert.equal(s.split(raw).length,2);s=s.replace(raw,'NSS114_LITERAL_'+i);}
 s=packLua(s);
 for(const [i,name]of literals.entries()){const key='NSS114_LITERAL_'+i;assert.equal(s.split(key).length,2);s=s.replace(key,'[=['+name+']=]');}
 return s;
}
