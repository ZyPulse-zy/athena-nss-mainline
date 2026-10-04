-- Encode complete publications in independent pieces using the original projector.
-- Keeps shared-reference/cycle/key/scalar checks and baseline/current slot shapes.
-- Does not create a second full projected tree or a global jsonc visited list.
local function stringify(value,j,project)
 local function object(t)
  if type(t)~='table'or next(t)==nil then return false end
  for k in pairs(t)do if type(k)~='string'then return false end end;return true
 end
 if not(object(value)and object(value.snapshot)and type(value.snapshot.flows)=='table')then return j.stringify(project(value))end
 local flows=value.snapshot.flows;local count=0
 for k in pairs(flows)do if type(k)~='number'or k%1~=0 or k<1 then return j.stringify(project(value))end;count=count+1 end
 if count~=#flows then return j.stringify(project(value))end
 local function enc(v,shape)return assert(j.stringify(project(v,nil,shape)))end
 local function child(k)return(k=='baseline'or k=='current')and'devices'or nil end
 local parts={}
 for _,flow in ipairs(flows)do parts[#parts+1]=enc(flow)end
 local encodedFlows='['..table.concat(parts,',')..']'
 parts={}
 for k,v in pairs(value.snapshot)do parts[#parts+1]=enc(k)..':'..(k=='flows'and encodedFlows or enc(v,child(k)))end
 local encodedSnapshot='{'..table.concat(parts,',')..'}'
 parts={}
 for k,v in pairs(value)do parts[#parts+1]=enc(k)..':'..(k=='snapshot'and encodedSnapshot or enc(v,child(k)))end
 return '{'..table.concat(parts,',')..'}'
end
return stringify
