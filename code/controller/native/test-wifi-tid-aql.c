/* Offline fixtures for the exact source functions; no kernel/firmware I/O. */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
typedef uint8_t u8;
#define IEEE80211_NUM_TIDS 16
#define IEEE80211_AC_VO 0
#define IEEE80211_AC_VI 1
#define IEEE80211_AC_BE 2
#define IEEE80211_AC_BK 3
#define DSCP_TID_MAP_TBL_ENTRY_SIZE 64
#define ETH_P_IP 1
#define ETH_P_IPV6 2
#define ETH_P_MPLS_UC 3
#define ETH_P_MPLS_MC 4
#define ETH_P_80221 5
#define htons(x) (x)
#define ntohl(x) (x)
#define VLAN_PRIO_MASK 0xe000
#define VLAN_PRIO_SHIFT 13
#define MPLS_LS_TC_MASK 0xe00
#define MPLS_LS_TC_SHIFT 9
#define array_index_nospec(x,n) ((x)<(n)?(x):0)
struct sk_buff {unsigned priority,protocol,dsfield,vlan;bool vlan_present;};
struct ethhdr {char x[14];};struct mpls_label {unsigned entry;};
struct cfg80211_qos_map {unsigned num_des;struct{unsigned dscp,up;}dscp_exception[21];struct{unsigned low,high;}up[8];};
#define skb_vlan_tag_present(s) ((s)->vlan_present)
#define skb_vlan_tag_get(s) ((s)->vlan)
#define ip_hdr(s) (s)
#define ipv6_hdr(s) (s)
#define ipv4_get_dsfield(s) ((s)->dsfield)
#define ipv6_get_dsfield(s) ((s)->dsfield)
static void *skb_header_pointer(struct sk_buff*s,unsigned off,unsigned size,void*tmp){(void)s;(void)off;(void)size;(void)tmp;return NULL;}
struct ieee80211_sta{int x;};struct sta_info{struct ieee80211_sta sta;struct{int aql_tx_pending,aql_limit_low,aql_limit_high;}airtime[4];};
struct wiphy {bool aql;};struct ieee80211_local;
struct ieee80211_hw {struct wiphy*wiphy;struct ieee80211_local*local;};
struct ieee80211_local {struct ieee80211_hw hw;int aql_bc_pending_airtime,aql_txq_limit_bc,aql_total_pending_airtime,aql_threshold;};
struct ieee80211_txq{struct ieee80211_sta*sta;unsigned tid,ac;};
#define NL80211_EXT_FEATURE_AQL 1
#define hw_to_local(h) ((h)->local)
#define wiphy_ext_feature_isset(w,x) ((void)(x),(w)->aql)
static bool aql_disable;
#define static_branch_unlikely(p) (*(p))
#define atomic_read(p) (*(p))
#define unlikely(x) (x)
#define container_of(p,type,field) ((type*)((char*)(p)-offsetof(type,field)))
/* SOURCE_FUNCTIONS */
int main(void){unsigned checks=0;
 struct sk_buff s={.protocol=ETH_P_IP};
 unsigned dscps[]={0,8,18,26,32,40,46,48};unsigned ups[]={0,1,3,4,4,5,6,7};
 for(unsigned i=0;i<8;i++){s.dsfield=dscps[i]<<2;assert(cfg80211_classify8021d(&s,NULL)==ups[i]);checks++;}
 s.dsfield=0;s.priority=6;assert(cfg80211_classify8021d(&s,NULL)==0);checks++;
 s.priority=0x7e660006;assert(cfg80211_classify8021d(&s,NULL)==0);checks++;
 s.priority=262;assert(cfg80211_classify8021d(&s,NULL)==6);checks++;
 s.priority=0;s.vlan_present=true;s.vlan=5<<13;assert(cfg80211_classify8021d(&s,NULL)==5);checks++;
 s.vlan_present=false;s.dsfield=46<<2;struct cfg80211_qos_map map={.num_des=1,.dscp_exception={{46,4}}};assert(cfg80211_classify8021d(&s,&map)==4);checks++;
 assert(dscp_tid_map[46]==5&&ieee802_1d_to_ac[5]==IEEE80211_AC_VI);checks++;
 assert(ieee802_1d_to_ac[6]==IEEE80211_AC_VO&&ieee802_1d_to_ac[0]==IEEE80211_AC_BE);checks++;
 struct wiphy w={.aql=false};struct ieee80211_local l={.aql_threshold=24000,.aql_txq_limit_bc=5000};l.hw.wiphy=&w;l.hw.local=&l;
 struct sta_info sta={0};sta.airtime[2].aql_limit_low=5000;sta.airtime[2].aql_limit_high=12000;sta.airtime[2].aql_tx_pending=20000;
 struct ieee80211_txq q={.sta=&sta.sta,.ac=2};
 assert(ieee80211_txq_airtime_check(&l.hw,&q));checks++; /* Feature absent: no throttle. */
 w.aql=true;assert(!ieee80211_txq_airtime_check(&l.hw,&q));checks++;
 aql_disable=true;assert(ieee80211_txq_airtime_check(&l.hw,&q));checks++;aql_disable=false;
 sta.airtime[2].aql_tx_pending=4000;assert(ieee80211_txq_airtime_check(&l.hw,&q));checks++;
 sta.airtime[2].aql_tx_pending=6000;assert(ieee80211_txq_airtime_check(&l.hw,&q));checks++;
 l.aql_total_pending_airtime=24000;assert(!ieee80211_txq_airtime_check(&l.hw,&q));checks++;
 q.tid=16;assert(ieee80211_txq_airtime_check(&l.hw,&q));checks++;
 q.sta=NULL;l.aql_bc_pending_airtime=5000;assert(!ieee80211_txq_airtime_check(&l.hw,&q));checks++;
 printf("%u exact-source TID/AQL fixture checks passed; no firmware I/O\n",checks);return 0;}
