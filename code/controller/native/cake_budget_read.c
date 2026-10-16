/* SPDX-License-Identifier: GPL-2.0-or-later
 * One read-only rtnetlink dump, exact software CAKE roots only. No tc/NSS
 * formatting plugins, shell rate parsing, configuration or hardware writes.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <linux/netlink.h>
#include <linux/pkt_sched.h>
#include <linux/rtnetlink.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define MAX_ROOTS 12
#define BYTE_LIMIT (1024U * 1024U)
#define SAMPLE_MS 750
struct root_rate { int ifindex; unsigned int seen; uint64_t bytes; };
struct sample { struct root_rate roots[MAX_ROOTS]; int count, done; uint32_t sequence; };

static int attributes(const unsigned char *p, size_t len,
                      const struct rtattr **kind, const struct rtattr **options)
{
 while (len) {
  struct rtattr h; size_t step; unsigned int type;
  if (len < sizeof(h)) return -1;
  memcpy(&h, p, sizeof(h));
  if (h.rta_len < sizeof(h) || h.rta_len > len) return -1;
  step = RTA_ALIGN(h.rta_len); if (step > len) return -1;
  type = h.rta_type & NLA_TYPE_MASK;
  if (type == TCA_KIND) { if (*kind) return -1; *kind = (const struct rtattr *)p; }
  if (type == TCA_OPTIONS) { if (*options) return -1; *options = (const struct rtattr *)p; }
  p += step; len -= step;
 }
 return 0;
}
static int base_rate(const struct rtattr *options, uint64_t *rate)
{
 const unsigned char *p = RTA_DATA(options); size_t len = RTA_PAYLOAD(options);
 int found = 0;
 while (len) {
  struct rtattr h; size_t step;
  if (len < sizeof(h)) return -1;
  memcpy(&h, p, sizeof(h));
  if (h.rta_len < sizeof(h) || h.rta_len > len) return -1;
  step = RTA_ALIGN(h.rta_len); if (step > len) return -1;
  if ((h.rta_type & NLA_TYPE_MASK) == TCA_CAKE_BASE_RATE64) {
   if (found || h.rta_len != RTA_LENGTH(sizeof(*rate))) return -1;
   memcpy(rate, p + RTA_LENGTH(0), sizeof(*rate)); found = 1;
  }
  p += step; len -= step;
 }
 /* This controller's original queue contract accepts 1..200 Mbit/s.
  * Reject out-of-range/zero/unlimited values, never round a ceiling upward. */
 return found && *rate >= 125000 && *rate <= 25000000 ? 0 : -1;
}
static int qdisc(struct sample *s, const struct nlmsghdr *nh)
{
 struct tcmsg t; const struct rtattr *kind = NULL, *options = NULL;
 int index = -1;
 if (nh->nlmsg_len < NLMSG_LENGTH(sizeof(t))) return -1;
 memcpy(&t, NLMSG_DATA(nh), sizeof(t));
 if (t.tcm_parent != TC_H_ROOT) return 0;
 for (int i = 0; i < s->count; i++) if (s->roots[i].ifindex == t.tcm_ifindex) index = i;
 if (index < 0) return 0; /* Never interpret unrelated NSS/plugin attributes. */
 if (s->roots[index].seen) return -1;
 if (attributes((const unsigned char *)NLMSG_DATA(nh) + NLMSG_ALIGN(sizeof(t)),
                nh->nlmsg_len - NLMSG_LENGTH(sizeof(t)), &kind, &options)) return -1;
 if (!kind || RTA_PAYLOAD(kind) != 5 || memcmp(RTA_DATA(kind), "cake", 5) || !options) return -1;
 if (base_rate(options, &s->roots[index].bytes)) return -1;
 s->roots[index].seen = 1;
 return 0;
}
static int datagram(struct sample *s, const unsigned char *p, size_t len)
{
 while (len) {
  struct nlmsghdr h; size_t step;
  if (len < sizeof(h)) return -1;
  memcpy(&h, p, sizeof(h));
  if (h.nlmsg_len < sizeof(h) || h.nlmsg_len > len) return -1;
  step = NLMSG_ALIGN(h.nlmsg_len); if (step > len) return -1;
  if (s->done || h.nlmsg_seq != s->sequence || (h.nlmsg_flags & NLM_F_DUMP_INTR)) return -1;
  if (h.nlmsg_type == NLMSG_DONE) {
   int error = 0; size_t body = h.nlmsg_len - NLMSG_HDRLEN;
   if (body && body < sizeof(error)) return -1;
   if (body) memcpy(&error, p + NLMSG_HDRLEN, sizeof(error));
   if (error) return -1;
   s->done = 1;
  } else if (h.nlmsg_type == RTM_NEWQDISC) {
   if (!(h.nlmsg_flags & NLM_F_MULTI) || qdisc(s, (const struct nlmsghdr *)p)) return -1;
  } else return -1; /* Includes NLMSG_ERROR/OVERRUN; no partial success. */
  p += step; len -= step;
 }
 return 0;
}
static int complete(const struct sample *s)
{
 if (!s->done || (s->count != 10 && s->count != 12)) return 0;
 for (int i = 0; i < s->count; i++) if (s->roots[i].seen != 1) return 0;
 return 1;
}
static int64_t monotonic_ms(void)
{
 struct timespec t;
 if (clock_gettime(CLOCK_MONOTONIC, &t)) return -1;
 return (int64_t)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}
static int indices(struct sample *s, int count)
{
 for (int direction = 0; direction < 2; direction++) for (int w = 0; w < count; w++) {
  char path[128], tail; int value; FILE *f;
  snprintf(path, sizeof(path), "/sys/class/net/%s%d/ifindex", direction ? "rpifb" : "rpwan", w + 1);
  f = fopen(path, "r"); if (!f) return -1;
  int ok = fscanf(f, "%d %c", &value, &tail); fclose(f);
  if (ok != 1 || value <= 0) return -1;
  for (int i = 0; i < s->count; i++) if (s->roots[i].ifindex == value) return -1;
  s->roots[s->count++].ifindex = value;
 }
 return 0;
}
static int receive_sample(struct sample *s, int fd, int64_t deadline)
{
 size_t bytes = 0; unsigned char buffer[65536];
 while (!s->done) {
  int64_t at = monotonic_ms();
  if (at < 0 || at >= deadline) return -1;
  struct pollfd pfd = {.fd = fd, .events = POLLIN};
  int rc = poll(&pfd, 1, (int)(deadline - at));
  if (rc < 0 && errno == EINTR) continue;
  if (rc <= 0 || pfd.revents != POLLIN) return -1;
  struct sockaddr_nl peer = {0}; struct iovec iov = {.iov_base = buffer, .iov_len = sizeof(buffer)};
  struct msghdr msg = {.msg_name = &peer, .msg_namelen = sizeof(peer), .msg_iov = &iov, .msg_iovlen = 1};
  ssize_t got = recvmsg(fd, &msg, MSG_DONTWAIT);
  if (got < 0 && (errno == EINTR || errno == EAGAIN)) continue;
  if (got <= 0 || (msg.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) ||
      msg.msg_namelen < sizeof(peer) || peer.nl_family != AF_NETLINK || peer.nl_pid != 0) return -1;
  bytes += (size_t)got;
  if (bytes > BYTE_LIMIT || datagram(s, buffer, (size_t)got)) return -1;
 }
 int64_t finished = monotonic_ms();
 return complete(s) && finished >= 0 && finished < deadline ? 0 : -1;
}
int main(int argc, char **argv)
{
 struct sample s = {0}; int count, fd = -1, rc = EXIT_FAILURE; int64_t began = monotonic_ms();
 if (argc != 2 || (strcmp(argv[1], "5") && strcmp(argv[1], "6")) || began < 0) goto out;
 count = argv[1][0] - '0'; if (indices(&s, count)) goto out;
 s.sequence = (uint32_t)getpid(); if (!s.sequence) goto out;
 fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE); if (fd < 0) goto out;
 struct sockaddr_nl local = {.nl_family = AF_NETLINK}, kernel = {.nl_family = AF_NETLINK};
 int rcvbuf = 262144;
 if (setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf)) || bind(fd, (struct sockaddr *)&local, sizeof(local))) goto out;
 struct {struct nlmsghdr n; struct tcmsg t;} request = {
  .n = {.nlmsg_len = NLMSG_LENGTH(sizeof(struct tcmsg)), .nlmsg_type = RTM_GETQDISC,
        .nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP}, .t = {.tcm_family = AF_UNSPEC}};
 request.n.nlmsg_seq = s.sequence;
 if (sendto(fd, &request, request.n.nlmsg_len, 0, (struct sockaddr *)&kernel, sizeof(kernel)) != (ssize_t)request.n.nlmsg_len) goto out;
 if (receive_sample(&s, fd, began + SAMPLE_MS)) goto out;
 /* Recheck netdev identity after the dump, before publishing any rate. */
 struct sample current = {0}; if (indices(&current, count)) goto out;
 for (int i = 0; i < s.count; i++) if (current.roots[i].ifindex != s.roots[i].ifindex) goto out;
 int64_t finished = monotonic_ms();
 if (finished < 0 || finished >= began + SAMPLE_MS) goto out;
 printf("[");
 for (int i = 0; i < s.count; i++)
  printf("%s{\"dev\":\"%s%d\",\"kind\":\"cake\",\"root\":true,\"options\":{\"bandwidth\":%" PRIu64 "}}",
         i ? "," : "", i < count ? "rpwan" : "rpifb", i % count + 1, s.roots[i].bytes);
 puts("]"); rc = EXIT_SUCCESS;
out:
 if (fd >= 0) close(fd);
 if (rc != EXIT_SUCCESS) fputs("CAKE read-only snapshot incomplete or expired\n", stderr);
 return rc;
}
