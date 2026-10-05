import assert from 'node:assert/strict';
// Formatting only. Reject Lua multiline strings/comments and continued quoted
// strings rather than change their contents. Original sources remain byte-exact.
export function packLua(source){
 assert.equal(typeof source,'string');assert.ok(!/\[=*\[/.test(source),'Multiline Lua literal requires original bytes');
 assert.ok(!source.includes('\\\n')&&!source.includes('\\\r\n'),'Continued quoted Lua literal requires original bytes');
 return source.split('\n').map(line=>line.trimStart()).filter(line=>line.trim()!==''&&!line.startsWith('--')).join('\n');
}
