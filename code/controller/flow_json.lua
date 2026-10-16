-- Encode independently owned flow objects separately, as the original
-- classifier does. jsonc need not walk one growing visited-object list across
-- every unrelated flow. Metadata and each flow still use the real JSON codec.
local M={}
function M.stringify(value,j)
 local encoded={}
 for _,flow in ipairs(assert(value.flows)) do encoded[#encoded+1]=assert(j.stringify(flow)) end
 local flows='['..table.concat(encoded,',')..']';local fields={}
 for key,v in pairs(value) do
  assert(type(key)=='string')
  fields[#fields+1]=assert(j.stringify(key))..':'..(key=='flows' and flows or assert(j.stringify(v)))
 end
 return '{'..table.concat(fields,',')..'}'
end
return M
