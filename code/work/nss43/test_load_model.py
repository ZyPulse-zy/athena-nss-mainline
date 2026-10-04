"""Consequential counter/identity failures must not become performance evidence."""
import unittest,copy
from load_model import delta,cpu_delta,iface_delta,flow_identity,fixed_demand,analyze,assess_load_comparability
def flow():
    return {'identity':{'connectionId':'1','zone':'0','wan':1,'mark':65536,'protocolNumber':6,
      'original':{'src':'lan','dst':'server','sport':1234,'dport':443},
      'reply':{'src':'server','dst':'nat','sport':443,'dport':1234,'bytes':100,'packets':1}},'decision':{'class':'BULK'}}
def sample(t,seq):
    row={'rx_bytes':t*3e6,'tx_bytes':t*3e6,'rx_packets':t*1000,'tx_packets':t*1000}
    f=flow();f['identity']['reply'].update(bytes=100+int(t*2500000),packets=1+int(t*2000))
    return {'producer':{'pid':1,'start':1},'ecmClosedAndZero':True,'routerWrites':False,'nssAdmissionAllowed':False,
      'sourceSequence':seq,'sourceAge':1,'bulk':[f],'game':[],
      'telemetry':{'uptime':t,'cpu':f'cpu {t*10} 0 {t*10} {t*50} 0 0 {t*30} 0 99 99',
      'softnet':'00000001 00000000 00000001','interfaces':{'lan4':row,**{'rpwan'+str(w):row for w in range(1,6)}}}}
class Tests(unittest.TestCase):
    def test_cpu_softirq_and_guest(self):
        self.assertEqual(cpu_delta('cpu 10 0 10 50 0 0 30 0 1 1','cpu 20 0 20 100 0 0 60 0 99 99'),{'busyPercent':50.,'softirqPercent':30.})
    def test_reset_rejected(self):
        with self.assertRaises(ValueError):delta(10,1)
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):delta(0,float('nan'))
    def test_no_elapsed_time(self):
        with self.assertRaises(ValueError):iface_delta({}, {},0)
    def test_reply_counter_is_not_identity(self):
        a=flow();b=copy.deepcopy(a);b['identity']['reply']['bytes']+=100;self.assertEqual(flow_identity(a),flow_identity(b))
    def test_ct_recreated_is_new_identity(self):
        a=flow();b=copy.deepcopy(a);b['identity']['connectionId']='2';self.assertNotEqual(flow_identity(a),flow_identity(b))
    def test_nat_changed_is_new_identity(self):
        a=flow();b=copy.deepcopy(a);b['identity']['reply']['dst']='another-nat';self.assertNotEqual(flow_identity(a),flow_identity(b))
    def test_proxy_mark_rejected(self):
        f=flow();f['identity']['mark']|=8192
        with self.assertRaises(ValueError):flow_identity(f)
    def test_wrong_wan_rejected(self):
        f=flow();f['identity']['wan']=2
        with self.assertRaises(ValueError):flow_identity(f)
    def test_fixed_demand_cap(self):
        self.assertEqual(fixed_demand(23,30,300,70)['fixedDemandControlledMbps'],23)
        self.assertEqual(fixed_demand(23,20,300,70)['fixedDemandControlledMbps'],20)
    def test_closure_required(self):
        a,b=sample(1,1),sample(2,2);b['ecmClosedAndZero']=False
        with self.assertRaises(ValueError):analyze([a,b])
    def test_source_regression_rejected(self):
        with self.assertRaises(ValueError):analyze([sample(1,2),sample(2,1)])
    def test_reused_sequence_counter_change_rejected(self):
        with self.assertRaises(ValueError):analyze([sample(1,1),sample(2,1)])
    def test_instance_change_rejected(self):
        a,b=sample(1,1),sample(2,2);b['producer']['pid']=2
        with self.assertRaises(ValueError):analyze([a,b])
    def test_sanitized_output_and_rate(self):
        a=analyze([sample(1,1),sample(2,2)]);self.assertEqual(a['flowRates'][0]['ctReplyMbps'],20)
        self.assertNotIn("'src':",str(a));self.assertNotIn('connectionId',str(a));self.assertFalse(a['nssAdmissionAllowed'])
    def test_missing_flow_not_whole_window(self):
        a,b,c=sample(1,1),sample(2,2),sample(3,3);b['bulk']=[]
        self.assertFalse(analyze([a,b,c])['flowRates'][0]['presentEverySample'])
    def test_matching_observations_cannot_authorize_or_prove_demand(self):
        rows=[{'name':name,'lan4DownMbps':300+i,'lan4Pps':25000+i,'wanRxMbps':60+i} for i,name in enumerate(('A','B','A2'))]
        out=assess_load_comparability(rows);self.assertTrue(out['similarObservedLoad']);self.assertFalse(out['permitsCausalCpuClaim']);self.assertFalse(out['nssAdmissionAllowed'])
    def test_same_global_load_does_not_hide_wan_drift(self):
        rows=[{'name':name,'lan4DownMbps':300,'lan4Pps':25000,'wanRxMbps':rate} for name,rate in zip(('A','B','A2'),(30,60,90))]
        self.assertFalse(assess_load_comparability(rows)['similarObservedLoad'])
    def test_missing_active_load_rejected(self):
        rows=[{'name':name,'lan4DownMbps':300,'lan4Pps':25000,'wanRxMbps':0} for name in ('A','B','A2')]
        with self.assertRaises(ValueError):assess_load_comparability(rows)
    def test_phase_order_rejected(self):
        with self.assertRaises(ValueError):assess_load_comparability([{'name':'B'},{'name':'A'},{'name':'A2'}])
if __name__=='__main__':unittest.main()
