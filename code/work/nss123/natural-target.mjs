import assert from'node:assert/strict';
// Pick another owned local socket only; Linux PBR remains the authority.
export function nextPort({tcpWan,udpWan,status,config}){
 assert.equal(config.experimentWan,5);assert.ok(Number.isInteger(status.tcpSourcePort)&&Number.isInteger(status.udpSourcePort));
 if(udpWan!==undefined&&udpWan!==5){const p=status.udpSourcePort+1;assert.ok(p<config.udpSourcePort+12,'Twelve owned UDP candidates exhausted');return{udpSourcePort:p};}
 if(udpWan===5&&tcpWan!==undefined&&tcpWan!==5){const p=status.tcpSourcePort+1;assert.ok(p<config.tcpSourcePort+8,'Eight owned TCP candidates exhausted');return{tcpSourcePort:p};}
 return null;
}
