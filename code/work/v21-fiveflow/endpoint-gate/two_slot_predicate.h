/* SPDX-License-Identifier: GPL-2.0 */
/* Endpoint-configurable predicate shared by the offline tests and lab gate.
 * This header itself does not register with ECM. */
#ifndef RP_NSS11_TWO_SLOT_PREDICATE_H
#define RP_NSS11_TWO_SLOT_PREDICATE_H
#ifdef __KERNEL__
#include <linux/types.h>
typedef __u32 rp11_u32;
typedef __u16 rp11_u16;
typedef __u8 rp11_u8;
#define RP11_U32C(x) x##U
#else
#include <stdint.h>
typedef uint32_t rp11_u32;
typedef uint16_t rp11_u16;
typedef uint8_t rp11_u8;
#define RP11_U32C(x) UINT32_C(x)
#endif

/* Numerical host-order IPv4 values; AE adapter must use ntohl(v4_addr).
 * AE ports are host order. Exact revoke API ports instead require htons(). */
#define RP11_CLIENT RP11_U32C(0xc0a8edcf) /* 192.168.237.207 */
/* Legacy test fixtures only; the lab module requires explicit TCP parameters. */
#define RP11_TCP_SERVER RP11_U32C(0xca7441ec) /* 202.116.65.236 */
#define RP11_TCP_SPORT 47471
#define RP11_TCP_DPORT 443
#define RP11_ROUTED 1
enum rp11_slot { RP11_OTHER = -1, RP11_TCP = 0, RP11_GAME = 1, RP11_TCP2 = 2, RP11_TCP3 = 3, RP11_TCP4 = 4 };
#define RP11_SLOTS 5
struct rp11_config {
    rp11_u32 game_server;
    rp11_u16 game_source_port;
    rp11_u16 game_server_port;
    rp11_u32 tcp_server;
    rp11_u16 tcp_source_port, tcp_server_port;
    rp11_u32 tcp2_server;
    rp11_u16 tcp2_source_port, tcp2_server_port;
    rp11_u32 tcp3_server, tcp4_server;
    rp11_u16 tcp3_source_port, tcp3_server_port, tcp4_source_port, tcp4_server_port;
};
struct rp11_tuple {
    rp11_u32 src, dst;
    rp11_u16 sport, dport;
    rp11_u8 protocol;
};
static inline int rp11_game_server_valid(rp11_u32 a)
{
    /* Reject obvious non-unicast, private, link-local, loopback, benchmark,
     * documentation and shared-address-space endpoints. This bounded check
     * is not a substitute for controller route/identity qualification. */
    if (!a || (a >> 24) == 0 || (a >> 24) == 10 || (a >> 24) == 127 ||
        (a >> 28) >= 14 || (a >> 16) == 0xa9fe ||
        (a >> 20) == 0xac1 || (a >> 16) == 0xc0a8 ||
        (a >> 17) == (RP11_U32C(0xc6120000) >> 17) ||
        (a >> 22) == (RP11_U32C(0x64400000) >> 22) ||
        (a >> 8) == 0xc00002 || (a >> 8) == 0xc63364 ||
        (a >> 8) == 0xcb0071) return 0;
    return 1;
}
static inline int rp11_config_valid(const struct rp11_config *c)
{
    if (!c || !rp11_game_server_valid(c->game_server) || !c->game_source_port || !c->game_server_port) return 0;
    rp11_u32 hosts[4]={c->tcp_server,c->tcp2_server,c->tcp3_server,c->tcp4_server};
    rp11_u16 source[4]={c->tcp_source_port,c->tcp2_source_port,c->tcp3_source_port,c->tcp4_source_port};
    rp11_u16 dest[4]={c->tcp_server_port,c->tcp2_server_port,c->tcp3_server_port,c->tcp4_server_port};
    for (unsigned n=0;n<4;n++) { if (!rp11_game_server_valid(hosts[n]) || !source[n] || !dest[n]) return 0;
        for(unsigned m=0;m<n;m++) if(hosts[n]==hosts[m] && source[n]==source[m] && dest[n]==dest[m]) return 0; }
    return 1;
}
static inline enum rp11_slot rp11_match(const struct rp11_config *c,
        unsigned ip_version, unsigned protocol, unsigned flags,
        rp11_u32 src, rp11_u32 dst, unsigned sport, unsigned dport)
{
    if (!rp11_config_valid(c) || ip_version != 4 || flags != RP11_ROUTED ||
        sport == 0 || sport > 65535 || dport == 0 || dport > 65535)
        return RP11_OTHER;
    if (protocol == 6 &&
        ((src == RP11_CLIENT && dst == c->tcp_server &&
          sport == c->tcp_source_port && dport == c->tcp_server_port) ||
         (src == c->tcp_server && dst == RP11_CLIENT &&
          sport == c->tcp_server_port && dport == c->tcp_source_port))) return RP11_TCP;
    if (protocol == 6 &&
        ((src == RP11_CLIENT && dst == c->tcp2_server &&
          sport == c->tcp2_source_port && dport == c->tcp2_server_port) ||
         (src == c->tcp2_server && dst == RP11_CLIENT &&
          sport == c->tcp2_server_port && dport == c->tcp2_source_port))) return RP11_TCP2;
    if (protocol == 6 &&
        ((src == RP11_CLIENT && dst == c->tcp3_server &&
          sport == c->tcp3_source_port && dport == c->tcp3_server_port) ||
         (src == c->tcp3_server && dst == RP11_CLIENT &&
          sport == c->tcp3_server_port && dport == c->tcp3_source_port))) return RP11_TCP3;
    if (protocol == 6 &&
        ((src == RP11_CLIENT && dst == c->tcp4_server &&
          sport == c->tcp4_source_port && dport == c->tcp4_server_port) ||
         (src == c->tcp4_server && dst == RP11_CLIENT &&
          sport == c->tcp4_server_port && dport == c->tcp4_source_port))) return RP11_TCP4;
    if (protocol == 17 &&
        ((src == RP11_CLIENT && dst == c->game_server &&
          sport == c->game_source_port && dport == c->game_server_port) ||
         (src == c->game_server && dst == RP11_CLIENT &&
          sport == c->game_server_port && dport == c->game_source_port))) return RP11_GAME;
    return RP11_OTHER;
}
static inline void rp11_revoke_tuples(const struct rp11_config *c,
        struct rp11_tuple out[10])
{
    out[0] = (struct rp11_tuple){RP11_CLIENT, c->tcp_server,
        c->tcp_source_port, c->tcp_server_port, 6};
    out[1] = (struct rp11_tuple){c->tcp_server, RP11_CLIENT,
        c->tcp_server_port, c->tcp_source_port, 6};
    out[2] = (struct rp11_tuple){RP11_CLIENT, c->game_server,
        c->game_source_port, c->game_server_port, 17};
    out[3] = (struct rp11_tuple){c->game_server, RP11_CLIENT,
        c->game_server_port, c->game_source_port, 17};
    out[4] = (struct rp11_tuple){RP11_CLIENT, c->tcp2_server,
        c->tcp2_source_port, c->tcp2_server_port, 6};
    out[5] = (struct rp11_tuple){c->tcp2_server, RP11_CLIENT,
        c->tcp2_server_port, c->tcp2_source_port, 6};
    out[6] = (struct rp11_tuple){RP11_CLIENT, c->tcp3_server, c->tcp3_source_port, c->tcp3_server_port, 6};
    out[7] = (struct rp11_tuple){c->tcp3_server, RP11_CLIENT, c->tcp3_server_port, c->tcp3_source_port, 6};
    out[8] = (struct rp11_tuple){RP11_CLIENT, c->tcp4_server, c->tcp4_source_port, c->tcp4_server_port, 6};
    out[9] = (struct rp11_tuple){c->tcp4_server, RP11_CLIENT, c->tcp4_server_port, c->tcp4_source_port, 6};
}
/* AE metadata has no ctid, zone, mark, packet length, fragment bit, skb or
 * interface. The lab adapter must enforce its pinned CT identity separately;
 * offline predicate success is not runtime admission qualification. */
#endif
