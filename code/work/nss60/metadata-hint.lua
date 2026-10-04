-- These pattern extracts are untrusted scheduling hints, never proof or input
-- for NSS admission. The original locked full JSON audit must then succeed and
-- independently equal the classification producer and query sequence.
local M={}
function M.extract(raw,j)
 if type(raw)~='string'or #raw>4194304 then return nil end
 local producer=raw:match('"producer"%s*:%s*"([^"\\]+)"')
 local block=raw:match('"provenance"%s*:%s*(%b{})')
 local published=tonumber(raw:match('"atUptime"%s*:%s*([%d%.]+)'))
 if not(producer and block and published)then return nil end
 local p=j.parse(block)
 if not(p and type(p.sequence)=='number'and type(p.startedAtUptime)=='number'and type(p.finishedAtUptime)=='number')then return nil end
 return{producer=producer,sequence=p.sequence,queryStart=p.startedAtUptime,queryFinished=p.finishedAtUptime,published=published}
end
return M
