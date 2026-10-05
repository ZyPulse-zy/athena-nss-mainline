// Passive, socket-local capture: one owned IPv4 UDP nonce; no injection/promisc.
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <linux/filter.h>
#include <linux/if_packet.h>
#include <linux/if_ether.h>
#include <net/if.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>
#define MAX_GROUPS 48
#define MAX_SEQ 10000
struct group { int ifindex,type,down;unsigned count,dup;char name[IF_NAMESIZE];unsigned char seen[MAX_SEQ];uint64_t at[MAX_SEQ]; };
static struct group groups[MAX_GROUPS];static unsigned n_groups,invalid,overflow;
static unsigned char nonce[32];static uint32_t server;static uint16_t port;static volatile sig_atomic_t stopped;
static void stop_now(int x){(void)x;stopped=1;}
static uint64_t now_ns(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))exit(3);return(uint64_t)t.tv_sec*1000000000ULL+(uint64_t)t.tv_nsec;}
static unsigned be16(const unsigned char *b){return(unsigned)b[0]*256U+b[1];}
static uint32_t be32(const unsigned char *b){return(uint32_t)b[0]<<24|(uint32_t)b[1]<<16|(uint32_t)b[2]<<8|b[3];}
static int packet(const unsigned char *b,size_t z,const struct sockaddr_ll *a,uint64_t ns){
 if(z<68||b[0]!=0x45||b[9]!=17)return 0;
 unsigned sp=be16(b+20),dp=be16(b+22);int down=be32(b+12)==server&&sp==port;
 int up=be32(b+16)==server&&dp==port;if(!down&&!up)return 0;
 if(be16(b+2)!=156||be16(b+24)!=136||z<156||memcmp(b+28,nonce,32))return 0;
 if(be32(b+60)){invalid++;return 0;}uint32_t seq=be32(b+64);if(seq>=MAX_SEQ){overflow++;return 0;}
 unsigned i;for(i=0;i<n_groups;i++)if(groups[i].ifindex==a->sll_ifindex&&groups[i].type==a->sll_pkttype&&groups[i].down==down)break;
 if(i==n_groups){if(n_groups==MAX_GROUPS){overflow++;return 0;}struct group *g=&groups[n_groups++];g->ifindex=a->sll_ifindex;g->type=a->sll_pkttype;g->down=down;
  if(!if_indextoname((unsigned)a->sll_ifindex,g->name))snprintf(g->name,sizeof(g->name),"if%d",a->sll_ifindex);
  for(char *s=g->name;*s;s++)if(!((*s>='a'&&*s<='z')||(*s>='A'&&*s<='Z')||(*s>='0'&&*s<='9')||*s=='_'||*s=='-'||*s=='.'))*s='_';
 }
 struct group *g=&groups[i];if(g->seen[seq])g->dup++;else{g->seen[seq]=1;g->at[seq]=ns;g->count++;}return 1;
}
static int self_test(void){
 unsigned char b[156]={0};b[0]=0x45;b[9]=17;b[2]=0;b[3]=156;b[24]=0;b[25]=136;server=0x7f000001;port=45818;
 b[12]=127;b[15]=1;b[20]=port>>8;b[21]=port&255;b[67]=7;memcpy(b+28,nonce,32);
 struct sockaddr_ll a={.sll_ifindex=1,.sll_pkttype=PACKET_HOST};
 if(!packet(b,sizeof(b),&a,123)||!packet(b,sizeof(b),&a,124)||n_groups!=1||groups[0].count!=1||groups[0].dup!=1||groups[0].at[7]!=123)return 1;
 b[28]=1;if(packet(b,sizeof(b),&a,125))return 1;b[28]=0;
 if(packet(b,155,&a,126))return 1;
 b[0]=0x46;if(packet(b,sizeof(b),&a,127))return 1;b[0]=0x45;
 b[60]=1;if(packet(b,sizeof(b),&a,128)||invalid!=1)return 1;
 puts("{\"passed\":true,\"parserCases\":6,\"socketOpened\":false}");return 0;
}
int main(int argc,char **argv){
 if(argc==2&&!strcmp(argv[1],"--self-test"))return self_test();
 if(argc!=5){fputs("usage: udp-path-tap seconds server port noncehex\n",stderr);return 2;}
 char *end;long seconds=strtol(argv[1],&end,10);if(*end||seconds<1||seconds>12)return 2;
 struct in_addr ip;if(inet_pton(AF_INET,argv[2],&ip)!=1)return 2;server=ntohl(ip.s_addr);
 long p=strtol(argv[3],&end,10);if(*end||p<1024||p>65535)return 2;port=(uint16_t)p;if(strlen(argv[4])!=64)return 2;
 for(int i=0;i<32;i++){char hex[3]={argv[4][i*2],argv[4][i*2+1],0};unsigned long v=strtoul(hex,&end,16);if(*end||v>255)return 2;nonce[i]=(unsigned char)v;}
 struct sock_filter code[]={
  BPF_STMT(BPF_LD|BPF_B|BPF_ABS,0),BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,0x45,0,11),
  BPF_STMT(BPF_LD|BPF_B|BPF_ABS,9),BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,17,0,9),
  BPF_STMT(BPF_LD|BPF_W|BPF_ABS,12),BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,server,2,0),
  BPF_STMT(BPF_LD|BPF_W|BPF_ABS,16),BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,server,0,5),
  BPF_STMT(BPF_LD|BPF_H|BPF_ABS,20),BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,port,2,0),
  BPF_STMT(BPF_LD|BPF_H|BPF_ABS,22),BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,port,0,1),
  BPF_STMT(BPF_RET|BPF_K,156),BPF_STMT(BPF_RET|BPF_K,0)
 };
 // Protocol zero leaves reception disabled until the socket-local filter is ready.
 struct sock_fprog filter={.len=sizeof(code)/sizeof(code[0]),.filter=code};int fd=socket(AF_PACKET,SOCK_DGRAM|SOCK_NONBLOCK|SOCK_CLOEXEC,0);
 if(fd<0){perror("socket");return 2;}int rcv=262144;
 if(setsockopt(fd,SOL_SOCKET,SO_RCVBUF,&rcv,sizeof(rcv))||setsockopt(fd,SOL_SOCKET,SO_ATTACH_FILTER,&filter,sizeof(filter))){perror("socket options");close(fd);return 2;}
 struct sockaddr_ll binding={.sll_family=AF_PACKET,.sll_protocol=htons(ETH_P_ALL),.sll_ifindex=0};
 if(bind(fd,(struct sockaddr*)&binding,sizeof(binding))){perror("bind");close(fd);return 2;}
 signal(SIGALRM,stop_now);signal(SIGTERM,stop_now);signal(SIGINT,stop_now);alarm((unsigned)seconds+1);
 uint64_t start=now_ns(),due=start+(uint64_t)seconds*1000000000ULL;puts("NSS109_TAP_READY");fflush(stdout);
 while(!stopped&&now_ns()<due){struct pollfd pollfd={.fd=fd,.events=POLLIN};int ret=poll(&pollfd,1,50);if(ret<0&&errno!=EINTR){perror("poll");close(fd);return 2;}if(ret<=0)continue;
  for(unsigned n=0;n<1024;n++){unsigned char b[256];struct sockaddr_ll a;socklen_t alen=sizeof(a);ssize_t size=recvfrom(fd,b,sizeof(b),0,(struct sockaddr*)&a,&alen);
   if(size<0){if(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR)break;perror("receive");close(fd);return 2;}packet(b,(size_t)size,&a,now_ns());}
 }
 uint64_t finish=now_ns();struct tpacket_stats stats={0};socklen_t slen=sizeof(stats);int stat_ok=getsockopt(fd,SOL_PACKET,PACKET_STATISTICS,&stats,&slen)==0;close(fd);
 printf("{\"passed\":%s,\"seconds\":%.6f,\"startNs\":%llu,\"endNs\":%llu,\"socketPackets\":%u,\"socketDrops\":%u,\"invalid\":%u,\"overflow\":%u,\"groups\":[",stat_ok&&!stats.tp_drops&&!invalid&&!overflow?"true":"false",(finish-start)/1e9,(unsigned long long)start,(unsigned long long)finish,stats.tp_packets,stats.tp_drops,invalid,overflow);
 for(unsigned g=0;g<n_groups;g++){struct group *x=&groups[g];printf("%s{\"interface\":\"%s\",\"ifindex\":%d,\"packetType\":%d,\"direction\":\"%s\",\"unique\":%u,\"duplicates\":%u,\"sequenceTimes\":[",g?",":"",x->name,x->ifindex,x->type,x->down?"down":"up",x->count,x->dup);unsigned n=0;
  for(unsigned s=0;s<MAX_SEQ;s++)if(x->seen[s]){printf("%s[%u,%.3f]",n++?",":"",s,(x->at[s]-start)/1e6);}
  fputs("]}",stdout);
 }puts("]}");return stat_ok&&!stats.tp_drops&&!invalid&&!overflow?0:2;
}
