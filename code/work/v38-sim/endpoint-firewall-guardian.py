"""RAM-only, sole writer of two owned temporary endpoint allow rules."""
import copy, hashlib, ipaddress, json, os, select, signal, subprocess, time

def canonical(value):
    v=copy.deepcopy(value)
    def walk(x):
        if isinstance(x,dict):
            for k,y in x.items():
                if k=='counter' and isinstance(y,dict):
                    y.pop('packets',None);y.pop('bytes',None)
                walk(y)
        elif isinstance(x,list):
            for y in x:walk(y)
    walk(v)
    return json.dumps(v,sort_keys=True,separators=(',',':'))

def nft(args, payload=None):
    r=subprocess.run(['nft',*args],input=None if payload is None else json.dumps(payload),
                     capture_output=True,text=True,timeout=4)
    if r.returncode:raise RuntimeError('nft invocation failed: '+str(r.returncode))
    return json.loads(r.stdout) if r.stdout.strip() else None

def identity(pid):
    p='/proc/'+str(pid)+'/stat'
    with open(p) as f:a=f.read().strip().rsplit(') ',1)[1].split()
    return {'pid':pid,'start':a[19],'ppid':int(a[1]),'pgrp':int(a[2]),'session':int(a[3])}

def pipe_json(fd,value):
    data=(json.dumps(value,separators=(',',':'))+'\n').encode()
    while data:
        n=os.write(fd,data);data=data[n:]

def receive_json(fd,seconds):
    due=time.monotonic()+seconds; data=b''
    while time.monotonic()<due:
        if not select.select([fd],[],[],max(0,due-time.monotonic()))[0]:break
        b=os.read(fd,8192)
        if not b:break
        data+=b
        if b'\n' in data:return json.loads(data.split(b'\n',1)[0])
        if len(data)>65536:raise RuntimeError('Oversized guardian receipt')
    raise RuntimeError('Guardian receipt deadline')

def allow_commands(c):
    commands=[]
    for proto,port in [('tcp',45817),('udp',45818)]:
        comment='nss14-'+c['owner']+'-'+proto
        rule={'family':'inet','table':'sub2api','chain':'input','comment':comment,'expr':[
            {'match':{'op':'==','left':{'meta':{'key':'nfproto'}},'right':'ipv4'}},
            {'match':{'op':'==','left':{'meta':{'key':'l4proto'}},'right':proto}},
            {'match':{'op':'==','left':{'payload':{'protocol':'ip','field':'saddr'}},'right':c['peers'][proto]}},
            {'match':{'op':'==','left':{'payload':{'protocol':proto,'field':'dport'}},'right':port}},
            {'counter':{'packets':0,'bytes':0}},{'accept':None}]}
        commands.append({'add':{'rule':rule}})
    return commands

def run(c):
    assert os.getuid()==0 and c['mode'] in ('pilot','apply')
    assert len(c['owner'])==32 and all(x in '0123456789abcdef' for x in c['owner'])
    for ip in c['peers'].values():assert ipaddress.IPv4Address(ip).is_global
    with open('/proc/sys/kernel/random/boot_id') as f:boot=f.read().strip()
    assert boot==c['boot']
    rr,rw=os.pipe();gr,gw=os.pipe();pid=os.fork()
    if pid==0:
        os.close(rr);os.close(gw);os.setsid();signal.signal(signal.SIGHUP,signal.SIG_IGN);signal.signal(signal.SIGPIPE,signal.SIG_IGN)
        null=os.open('/dev/null',os.O_RDWR)
        for fd in (0,1,2):os.dup2(null,fd)
        if null>2:os.close(null)
        due=time.monotonic()+(8 if c['mode']=='pilot' else 180)
        expected={};failure=False
        try:
            pipe_json(rw,{'ready':True,'identity':identity(os.getpid()),'deadline':due,'boot':boot,'goFd':gr,'resultFd':rw})
            assert select.select([gr],[],[],5)[0] and os.read(gr,1)==b'G';os.close(gr)
            before=nft(['-j','list','ruleset']);assert hashlib.sha256(canonical(before).encode()).hexdigest()==c['baselineCanonicalSha256']
            if c['mode']=='apply':
                assert time.monotonic()<due-25
                nft(['-j','-f','-'],{'nftables':allow_commands(c)})
                now=nft(['-j','list','ruleset'])
                for x in now['nftables']:
                    r=x.get('rule',{})
                    if r.get('comment','').startswith('nss14-'+c['owner']+'-'):
                        assert r['family']=='inet' and r['table']=='sub2api' and r['chain']=='input'
                        expected[r['comment']]=r
                assert len(expected)==2
            pipe_json(rw,{'applied':c['mode']=='apply','mode':c['mode'],'rules':list(expected.values()),'identity':identity(os.getpid()),'deadline':due,'boot':boot})
            os.close(rw);rw=-1
            while time.monotonic()<due:time.sleep(min(.2,max(0,due-time.monotonic())))
        except BaseException:
            failure=True
        finally:
            # No parent can add rules after this cleanup: child is the sole writer.
            try:
                current=nft(['-j','list','ruleset']);owned=[]
                for x in current['nftables']:
                    r=x.get('rule',{})
                    if not r.get('comment','').startswith('nss14-'+c['owner']+'-'):continue
                    assert r['family']=='inet' and r['table']=='sub2api' and r['chain']=='input'
                    if expected:assert r['comment'] in expected and canonical(r)==canonical(expected[r['comment']])
                    owned.append(r)
                if owned:
                    nft(['-j','-f','-'],{'nftables':[{'delete':{'rule':{'family':'inet','table':'sub2api','chain':'input','handle':r['handle']}}} for r in owned]})
                after=nft(['-j','list','ruleset'])
                assert not any(x.get('rule',{}).get('comment','').startswith('nss14-'+c['owner']+'-') for x in after['nftables'])
            except BaseException:failure=True
            if rw>=0:
                try:os.close(rw)
                except OSError:pass
            os._exit(1 if failure else 0)
    os.close(rw);os.close(gr)
    ready=receive_json(rr,6);actual=identity(pid)
    assert ready['identity']==actual and actual['ppid']==os.getpid() and actual['pgrp']==pid and actual['session']==pid
    fds={int(x):os.readlink('/proc/'+str(pid)+'/fd/'+x) for x in os.listdir('/proc/'+str(pid)+'/fd')}
    for fd,target in fds.items():
        assert (fd in (0,1,2) and target=='/dev/null') or (fd in (ready['goFd'],ready['resultFd']) and target.startswith('pipe:['))
    assert set(fds)=={0,1,2,ready['goFd'],ready['resultFd']}
    os.write(gw,b'G');os.close(gw);receipt=receive_json(rr,7);os.close(rr)
    receipt['parentVerified']=True;receipt['beforeWriteIndependentGuardianVerified']=True
    print(json.dumps(receipt),flush=True)

