import assert from 'node:assert/strict';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
import {activeMask} from '../resident-general-dev-i-20261008/selection.mjs';
import {mapClassifiedPair} from '../resident-general-dev-i-20261008/class-leaf-map.mjs';
import {pinNormalOwnership,processIdentity} from '../resident-normal-dev-i-20261008/normal-policy.mjs';

// The test scope only narrows the unchanged normal entry. It grants no class,
// ownership, pin, lease, or NSS permission and does not create traffic.
export function rtScope(frame){
 assert.equal(frame.routerWrites,false);assert.equal(frame.nssAdmissionAllowed,false);
 assert.ok(frame.sourceAge>=0&&frame.sourceAge<6);
 assert.ok(Array.isArray(frame.udp)&&frame.udp.length===1,'One currently admitted owned RT required');
 const flow=frame.udp[0];assert.equal(flow.identity.protocolNumber,17);
 assert.equal(flow.decision.class,'RT');assert.equal(flow.decision.budgetAdmitted,true);
 const selected={udp:canonicalSelection(flow)};assert.equal(activeMask(selected),2);
 mapClassifiedPair(frame,selected);
 const pinned=pinNormalOwnership(frame,selected),owner=processIdentity(pinned.udp);
 return {version:1,owners:[owner],tcp:[],udp:[structuredClone(flow.identity.original)]};
}
