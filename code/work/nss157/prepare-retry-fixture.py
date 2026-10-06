from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'cohort-client.mjs').read_text(encoding='utf-8');a=s.index('function choose(')
s=s[:a]+"""function retryCohort(){assert.equal(c.allowPreparationRetry,true);assert.equal(stats.preparationCohort,0);assert.equal(selected,null);assert.equal(transports.size,4);for(const t of transports.values())dispose(t);stats.preparationRetry=true;beginCohort(1)}
"""+s[a:];s=s.replace("if(x.prepareSuccessor&&lastRequest!=='successor')", "if(x.prepareRetry&&lastRequest!=='retry'){assert.equal(x.prepareRetry,true);retryCohort();lastRequest='retry'}if(x.prepareSuccessor&&lastRequest!=='successor')")
put('cohort-client-v2.mjs',s)
s=(r/'start-dallas-v2.mjs').read_text(encoding='utf-8');s=s.replace("assert.equal(process.argv[2],'upload');config.mbps=32;", "assert.equal(process.argv[2],'upload');assert.ok(process.argv[3]===undefined||process.argv[3]==='class-retry');config.allowPreparationRetry=process.argv[3]==='class-retry';config.mbps=32;").replace("root+'/cohort-client.mjs'","root+'/cohort-client-v2.mjs'");put('start-dallas-v3.mjs',s)
s=(r/'match-controlled.mjs').read_text(encoding='utf-8');old="if(!x.pairs.length&&x.tcp.length===4&&x.ownedEstablishedTcpPorts.length===4)throw Error('Four software-only candidates classified, none match fixed UDP WAN; no stage');";assert s.count(old)==1
s=s.replace(old,"""if(!x.pairs.length&&x.tcp.length===4&&x.ownedEstablishedTcpPorts.length===4){
  if(c.allowPreparationRetry===true&&status.preparationCohort===0&&!status.preparationRetry){assert.equal(status.selectedTcpPort,null);assert.equal(status.tcpConnected,false);fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:c.session,prepareRetry:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');}
  else if(status.preparationCohort===1)throw Error('Both finite software cohorts exhausted without fixed UDP WAN; no stage');
  else throw Error('Initial finite software cohort does not match fixed UDP WAN; no stage');
 }
""");put('match-controlled-v2.mjs',s)
put('epoch-driver-v8.mjs',(r/'epoch-driver-v7.mjs').read_text(encoding='utf-8').replace("'./session-binding-v7.mjs'","'./session-binding-v8.mjs'").replace('/run13/','/run15/').replace('/run14/','/run16/'))
s=(r/'pilot-supervisor-v7.mjs').read_text(encoding='utf-8').replace("'./session-binding-v7.mjs'","'./session-binding-v8.mjs'").replace("'./epoch-driver-v7.mjs'","'./epoch-driver-v8.mjs'").replace("?'/run13':'/run14'","?'/run15':'/run16'").replace("root+'/start-dallas-v2.mjs',['upload']","root+'/start-dallas-v3.mjs',scenario==='change'?['upload','class-retry']:['upload']").replace("await run(root+'/match-controlled.mjs');","await run(root+(scenario==='change'?'/match-controlled-v2.mjs':'/match-controlled.mjs'));")
put('pilot-supervisor-v8.mjs',s)
put('session-binding-v8.mjs',(r/'session-binding-v7.mjs').read_text(encoding='utf-8').replace("'./session-binding-v6.mjs'","'./session-binding-v7.mjs'").replace('/entry-qualified-v7.json','/entry-qualified-v8.json'))
print('Class-only pre-NSS second cohort uses reserved four ports; fixed UDP, total32Mbps/8 ports/180s unchanged. Close case still reserves successor cohort.')
