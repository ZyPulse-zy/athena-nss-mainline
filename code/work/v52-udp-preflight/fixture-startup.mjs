const slots=Object.freeze(['tcp','tcp2','tcp3','tcp4']);
export async function launchInitialFour(startTcp,shouldStop){
 if(shouldStop())return;
 await Promise.all(slots.map(slot=>shouldStop()?undefined:startTcp(slot,1)));
}
export function fourOwnedPidsReady(s,nowSeconds){
 if(!s||!Number.isInteger(s.pid)||s.pid<=0||!Array.isArray(s.errors)||s.errors.length!==0||!Array.isArray(s.tcpChildren)||s.tcpChildren.length!==4)return false;
 if(!Number.isFinite(s.elapsed)||s.elapsed<0||s.elapsed>=50||!Number.isFinite(s.at)||!Number.isFinite(nowSeconds)||nowSeconds-s.at<0||nowSeconds-s.at>=2)return false;
 if(!slots.every((slot,i)=>s.tcpChildren[i].slot===slot&&Number.isInteger(s.tcpChildren[i].ownerPid)&&s.tcpChildren[i].ownerPid>0))return false;
 return new Set(s.tcpChildren.map(x=>x.ownerPid)).size===4;
}
