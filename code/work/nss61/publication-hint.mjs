import assert from 'node:assert/strict';
// This normalizes read-only scheduling metadata. The locked full audit remains
// the authority and independently compares both fields before any checkpoint.
export function normalizePublicationHint(classificationHint, baselineJoin) {
  const a=classificationHint?.alignment;
  assert.equal(typeof a?.producer,'string');
  assert.ok(a.producer.length>0);
  assert.ok(Number.isSafeInteger(a.selectedSequence)&&a.selectedSequence>0);
  assert.equal(baselineJoin?.passed,true);
  assert.equal(baselineJoin.metadataHintOnly,true);
  assert.equal(baselineJoin.originalAuditStillRequired,true);
  assert.equal(baselineJoin.nssAdmissionAllowed,false);
  assert.equal(baselineJoin.join?.passed,true);
  assert.equal(baselineJoin.join.source.producer,a.producer);
  assert.equal(baselineJoin.join.source.sequence,a.selectedSequence);
  return {producer:a.producer,selectedSequence:a.selectedSequence,classificationHint,baselineJoin};
}
