-- Same unshared JSON projection contract. Recurse only for table values.
-- No memoization: jsonc must see a fresh table for every repeated reference.
local function project(value,stack,shape)
 local t=type(value)
 if t~='table'then
  assert(t=='nil'or t=='boolean'or t=='string'or(t=='number'and value==value and value>-math.huge and value<math.huge),'Non-JSON scalar')
  return value
 end
 stack=stack or{};assert(not stack[value],'Cyclic JSON tree');stack[value]=true
 local dense=shape~='slots';local count,maximum=0,0
 for k in pairs(value)do
  local kt=type(k);assert(kt=='string'or(kt=='number'and k>=1 and k==math.floor(k)),'Non-JSON key')
  count=count+1;if kt~='number'then dense=false elseif k>maximum then maximum=k end
 end
 if count==0 or maximum~=count then dense=false end
 local out={}
 for k,v in pairs(value)do
  local key=(type(k)=='number'and not dense)and tostring(k)or k
  assert(out[key]==nil,'Colliding JSON key')
  local vt=type(v)
  if vt=='table'then
   local child=(shape=='devices')and'slots'or((k=='baseline'or k=='current')and'devices'or nil)
   out[key]=project(v,stack,child)
  else
   assert(vt=='nil'or vt=='boolean'or vt=='string'or(vt=='number'and v==v and v>-math.huge and v<math.huge),'Non-JSON scalar')
   out[key]=v
  end
 end
 stack[value]=nil;return out
end
return project
