import assert from 'node:assert/strict';

export function patchLearningAlignment(source){
 const before=`    local ready,reason,retryable=A.preLearningReady()
    R.learningAlignment[#R.learningAlignment+1]={coreAt=R.corePhase.observedAt,checkedAt=now(),ready=ready,reason=reason,retryable=retryable==true}
    if not ready and retryable~=true then error('Pre-learning admission refused: '..tostring(reason),0)end
    if ready and now()<probeUntil then
     local fresh=A.resampleClosed();local due=fresh.provenance.startedAtUptime+6;for _,f in ipairs(fresh.flows)do due=math.min(due,f.validUntilUptime)end`;
 const after=`    local ready,fresh=pcall(A.resampleClosed)
    local reason=not ready and tostring(fresh)or nil
    local retryable=reason and(reason:match(': Pre%-learning time margin insufficient$')or reason:match(': Per%-flow pre%-learning time margin insufficient$')or reason:match(': Fresh epoch lacks tag setup reserve$'))
    R.learningAlignment[#R.learningAlignment+1]={coreAt=R.corePhase.observedAt,checkedAt=now(),ready=ready,reason=reason,retryable=retryable~=nil}
    if not ready and not retryable then error('Pre-learning admission refused: '..reason,0)end
    if ready and now()<probeUntil then
     local due=fresh.provenance.startedAtUptime+6;for _,f in ipairs(fresh.flows)do due=math.min(due,f.validUntilUptime)end`;
 const crlf=source.includes('\r\n'),a=crlf?before.replaceAll('\n','\r\n'):before,b=crlf?after.replaceAll('\n','\r\n'):after;
 assert.equal(source.split(a).length,2,'Exact closed learning alignment required');
 return source.replace(a,()=>b);
}
