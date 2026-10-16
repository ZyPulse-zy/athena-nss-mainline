/* Uses unchanged structures extracted from the pinned NSS export header.
 * A provider writes a synthetic multi-peer message; a consumer reads it.
 * No kernel or firmware I/O is present. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* SOURCE_STRUCTURES */
int main(int argc, char **argv) {
 if(argc!=3)return 2;
 if(!strcmp(argv[1],"write")) {
  size_t size=sizeof(uint32_t)+3*sizeof(struct nss_wifili_peer_ctrl_stats);
  struct nss_wifili_peer_stats *s=calloc(1,size);if(!s)return 3;s->npeers=3;
  for(unsigned i=0;i<3;i++) {
   s->wpcs[i].peer_id=1001+i;
   s->wpcs[i].tx.tx_ucast_cnt=10+i;
   s->wpcs[i].tx.tx_ucast_bytes=1000+i;
   s->wpcs[i].rx.rx_recvd_bytes=2000+i;
   s->wpcs[i].retry.tx_failed_retry_count=30+i;
   s->wpcs[i].retry.tx_multiple_retry_count=40+i;
  }
  FILE *f=fopen(argv[2],"wb");if(!f)return 4;
  if(fwrite(s,1,size,f)!=size)return 5;
  fclose(f);free(s);return 0;
 }
 FILE *f=fopen(argv[2],"rb");if(!f)return 6;
 void *data=calloc(1,8192);if(!data)return 7;
 size_t read=fread(data,1,8192,f);fclose(f);
 struct nss_wifili_peer_stats *s=data;
 if(read<sizeof(uint32_t)+3*sizeof(struct nss_wifili_peer_ctrl_stats)||s->npeers!=3)return 8;
 printf("{\"peerBytes\":%zu,\"retryOffset\":%zu,\"peers\":[",sizeof(struct nss_wifili_peer_ctrl_stats),offsetof(struct nss_wifili_peer_ctrl_stats,retry));
 for(unsigned i=0;i<3;i++) {
  struct nss_wifili_peer_ctrl_stats *p=&s->wpcs[i];
  printf("%s{\"id\":%u,\"txPackets\":%u,\"txBytes\":%u,\"rxBytes\":%u,\"txFailedRetries\":%u}",i?",":"",p->peer_id,p->tx.tx_ucast_cnt,p->tx.tx_ucast_bytes,p->rx.rx_recvd_bytes,p->retry.tx_failed_retry_count);
 }
 printf("]}\n");free(data);
}
