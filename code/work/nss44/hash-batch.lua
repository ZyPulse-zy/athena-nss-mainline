-- Pure candidate: verify every payload each invocation, using one hash process.
local M={}
function M.command(base,files)
 assert(type(base)=='string'and #base<=128 and base:match('^/root/router%-project/classifier/[%w%-]+$'),'Invalid classifier base')
 assert(type(files)=='table');local names={}
 for name,digest in pairs(files)do
  assert(type(name)=='string'and #name<=64 and name:match('^[a-z0-9%.%-]+$')and not name:find('..',1,true),'Invalid payload name')
  assert(type(digest)=='string'and #digest==64 and digest:match('^[0-9a-f]+$'),'Invalid payload digest')
  names[#names+1]=name
 end
 assert(#names>=1 and #names<=64,'Payload count exceeds hash command bound');table.sort(names)
 local paths={};for _,name in ipairs(names)do paths[#paths+1]=base..'/'..name end
 return '/usr/bin/sha256sum '..table.concat(paths,' '),16384
end
function M.verify(base,files,text)
 M.command(base,files);assert(type(text)=='string'and #text<=16384,'Hash output exceeds bound')
 local seen={};local count=0
 for line in text:gmatch('[^\n]+')do
  local digest,path=line:match('^([0-9a-f]+)  (.+)$');assert(digest and #digest==64,'Malformed hash output')
  assert(path:sub(1,#base+1)==base..'/','Foreign hash path')
  local name=path:sub(#base+2);assert(files[name]and not seen[name],'Unknown or duplicate hash path')
  assert(digest==files[name],'Payload bytes changed '..name);seen[name]=true;count=count+1
 end
 for name in pairs(files)do assert(seen[name],'Missing payload digest '..name)end
 return count
end
return M
