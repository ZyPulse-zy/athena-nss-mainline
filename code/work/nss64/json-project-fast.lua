-- Identical JSON tree contract; hot valid cases avoid repeated global calls.
local kind,pairs,raise,floor,huge=type,pairs,error,math.floor,math.huge
local function scalar(v,t)
 if not(t=='nil'or t=='boolean'or t=='string'or(t=='number'and v==v and v>-huge and v<huge))then raise('Non-JSON scalar')end
 return v
end
local function project(value,stack,shape)
 local t=kind(value);if t~='table'then return scalar(value,t)end
 stack=stack or{};if stack[value]then raise('Cyclic JSON tree')end;stack[value]=true
 local dense=shape~='slots';local count,maximum=0,0
 for k in pairs(value)do
  local kt=kind(k);if not(kt=='string'or(kt=='number'and k>=1 and k==floor(k)))then raise('Non-JSON key')end
  count=count+1;if kt~='number'then dense=false elseif k>maximum then maximum=k end
 end
 if count==0 or maximum~=count then dense=false end
 local out={}
 for k,v in pairs(value)do
  local key=(kind(k)=='number'and not dense)and tostring(k)or k
  if out[key]~=nil then raise('Colliding JSON key')end
  local vt=kind(v)
  if vt=='table'then
   local child=(shape=='devices')and'slots'or((k=='baseline'or k=='current')and'devices'or nil)
   out[key]=project(v,stack,child)
  else
   if not(vt=='nil'or vt=='boolean'or vt=='string'or(vt=='number'and v==v and v>-huge and v<huge))then raise('Non-JSON scalar')end
   out[key]=v
  end
 end
 stack[value]=nil;return out
end
return project
