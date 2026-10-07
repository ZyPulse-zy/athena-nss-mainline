export function mayRetryAcquisition({frozen,elapsedSeconds,attempt,hasPayload,knownTimeout}){
 return frozen===false&&hasPayload===false&&knownTimeout===true&&Number.isFinite(elapsedSeconds)&&elapsedSeconds>=0&&elapsedSeconds<30&&Number.isInteger(attempt)&&attempt>=1&&attempt<3;
}
