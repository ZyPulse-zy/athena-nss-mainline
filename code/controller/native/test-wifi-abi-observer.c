#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
struct nss_wifili_msg;typedef uint32_t u32;typedef void (*nss_wifili_msg_callback_t)(void*,struct nss_wifili_msg*);
#define NSS_WIFILI_PEER_STATS_MSG 12
#define NSS_CMN_RESPONSE_NOTIFY 5
#define time_before_eq(a,b) ((a)<=(b))
#define spin_lock_irqsave(a,b) ((void)(a),(b)=0)
#define spin_unlock_irqrestore(a,b) ((void)(a),(void)(b))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define atomic64_inc(a) (++*(a))
#define mutex_lock(a) ((void)(a))
#define mutex_unlock(a) ((void)(a))
#define cmpxchg(p,o,n) ({__typeof__(*(p)) v=*(p);if(v==(o))*(p)=(n);v;})
struct nss_wifili_msg {struct {unsigned type,response,len,version,interface;}cm;struct {struct {struct{unsigned npeers;}stats;}peer_stats;}msg;unsigned payload[500];};
static unsigned forwards,graces;static void original_fn(void*a,struct nss_wifili_msg*m){(void)a;(void)m;forwards++;}
static void other_fn(void*a,struct nss_wifili_msg*m){(void)a;(void)m;}
static void synchronize_net(void){graces++;}
static nss_wifili_msg_callback_t cell,*slot=&cell,original=original_fn;
static int ownership,records_lock;static _Bool attached,ownership_lost;
static unsigned long jiffies,deadline;static long long all_calls,peer_calls;
struct observation{u32 body_bytes,peers,version,interface,shape196,shape212;};static struct observation records[64];static unsigned record_count;
struct ath11k_base{int base_lock;};struct ath11k_peer{int unused;};
static struct ath11k_peer found;
static struct ath11k_peer *lookup(struct ath11k_base*a,int id){(void)a;return(id>=1001&&id<=1003)?&found:NULL;}
static struct ath11k_peer *(*peer_lookup)(struct ath11k_base*,int)=lookup;
#define rcu_read_lock() ((void)0)
#define rcu_read_unlock() ((void)0)
#define spin_lock_bh(a) ((void)(a))
#define spin_unlock_bh(a) ((void)(a))
#define READ_ONCE(a) (a)
static int copy_from_kernel_nofault(void*d,const void*s,size_t n){memcpy(d,s,n);return 0;}
/* SOURCE_FUNCTIONS */
int main(void){unsigned checks=0;
for(unsigned i=0;i<6;i++){struct nss_wifili_msg m={.cm={12,5,640,1,43},.msg.peer_stats.stats.npeers=3},saved=m;
 if(i==1){m.cm.type=10;}
 if(i==2){m.cm.response=0;}
 if(i==3){m.cm.len=2;}
 saved=m;jiffies=i==4?30:0;deadline=20;record_count=i==5?64:0;unsigned before=record_count,f=forwards;observe(NULL,&m);assert(memcmp(&m,&saved,sizeof(m))==0);checks++;assert(forwards==f+1);checks++;assert(record_count==before+((i==0)?1:0));checks++;}
cell=observe;attached=1;detach();assert(cell==original_fn&&!attached&&graces==1);checks++;
cell=other_fn;attached=1;detach();assert(cell==other_fn&&ownership_lost&&!attached&&graces==2);checks++;
detach();assert(!attached);checks++;struct ath11k_base ab={0};struct nss_wifili_msg packet={.cm={12,5,216,1,43},.msg.peer_stats.stats.npeers=3};
for(unsigned i=0;i<3;i++){u32 id=1001+i;memcpy((char*)&packet.msg.peer_stats.stats+4+i*212,&id,4);}
assert(shape_matches(&ab,&packet,212));checks++;assert(!shape_matches(&ab,&packet,196));checks++;
packet.msg.peer_stats.stats.npeers=9;assert(!shape_matches(&ab,&packet,212));checks++;
packet.msg.peer_stats.stats.npeers=1;assert(!shape_matches(&ab,&packet,212));checks++;
printf("%u source-function model checks passed\n",checks);return 0;}
