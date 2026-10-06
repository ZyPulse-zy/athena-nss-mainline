import assert from 'node:assert/strict';
export function requireOwnedDownload(config,status,load,at=Date.now()/1000){
 assert.equal(config.seconds,180);assert.equal(config.mbps,32);assert.equal(config.bulkDirection,'download');
 assert.equal(status.tcpMetric,'application received payload bytes');assert.equal(status.onlyOneRemoteSenderAtATime,true);
 assert.equal(status.pacerDebtCatchupAllowed,false);assert.equal(status.maximumPacerCreditBytes,65536);
 assert.equal(status.session,config.session);assert.equal(status.pid,load.clientPid);assert.equal(status.tcpConnected,true);
 assert.ok(at-status.at>=0&&at-status.at<2,'Owned client status stale');
 assert.ok(status.elapsed>=0&&status.elapsed<110,'Insufficient fixed client lifetime for a new owner');
 return{remainingSeconds:180-status.elapsed,originalIndependentClientDeadlineKept:true};
}
