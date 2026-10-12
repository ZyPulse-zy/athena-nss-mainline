"""Exercise exact built-source classification and AQL gates; no live traffic or writes."""
import argparse,pathlib,re,subprocess,tempfile,hashlib,json
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--backports',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path);a=p.parse_args()
files={k:(a.backports/v).read_text()for k,v in {'util':'net/wireless/util.c','wme':'net/mac80211/wme.c','tx':'net/mac80211/tx.c','hal':'drivers/net/wireless/ath/ath11k/hal_tx.c'}.items()}
parts=[files['util'][files['util'].index('unsigned int cfg80211_classify8021d('):files['util'].index('EXPORT_SYMBOL(cfg80211_classify8021d)')],files['tx'][files['tx'].index('bool ieee80211_txq_airtime_check('):files['tx'].index('EXPORT_SYMBOL(ieee80211_txq_airtime_check)')]]
for key,name in [('wme','ieee802_1d_to_ac'),('hal','dscp_tid_map')]:parts.append(re.search(r'(?:static )?const (?:int|u8) '+name+r'\[[^]]*\]\s*=\s*\{.*?\};',files[key],re.S)[0])
fixture=(pathlib.Path(__file__).resolve().parents[1]/'code/controller/native/test-wifi-tid-aql.c').read_text().replace('/* SOURCE_FUNCTIONS */','\n'.join(parts))
with tempfile.TemporaryDirectory()as folder:
 f=pathlib.Path(folder);(f/'model.c').write_text(fixture);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(f/'model.c'),'-o',str(f/'model')],check=True);result=subprocess.check_output([str(f/'model')],text=True);print(result.strip())
report={'passed':True,'checks':int(result.split()[0]),'actualSourceFunctionsUsed':True,'firmwareIoMocked':True,'routerModified':False,'finalAirTidAcVerified':False,'sourceSha256':{k:hashlib.sha256(v.encode()).hexdigest()for k,v in files.items()}}
if a.output:a.output.write_text(json.dumps(report,indent=2)+'\n')
