import assert from 'node:assert/strict';
export function requireOwnedUpload(config,status,load,at=Date.now()/1000){
 assert.equal(config.seconds,180);assert.equal(config.mbps,32);assert.equal(config.bulkDirection,'download');
 assert.equal(status.tcpMetric,'client-observed stdout download bytes');assert.ok(status.tcpBytes>0);assert.equal(config.tcpPort,22);assert.equal(status.bulkTransport,'owned native OpenSSH download');
 assert.equal(status.pacerDebtCatchupAllowed,false);assert.equal(status.maximumPacerCreditBytes,65536);
 assert.equal(status.session,config.session);assert.equal(status.pid,load.clientPid);assert.ok(status.tcpChildren&&status.tcpChildren.length===2&&status.tcpChildren.every(c=>c.connected));
 assert.ok(at-status.at>=0&&at-status.at<2);assert.ok(status.elapsed>=0&&status.elapsed<110);
 return{remainingSeconds:180-status.elapsed,originalIndependentClientDeadlineKept:true};
}
