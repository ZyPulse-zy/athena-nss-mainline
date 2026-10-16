/* Offline model for the exact deployed shim behavior; kernel I/O is mocked. */
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
struct ath11k_base { int unused; };
struct ieee80211_freq_range { unsigned start_freq_khz, end_freq_khz, max_bandwidth_khz; };
struct ieee80211_power_rule { unsigned max_antenna_gain, max_eirp; };
struct ieee80211_reg_rule { struct ieee80211_freq_range freq_range; struct ieee80211_power_rule power_rule; unsigned flags, dfs_cac_ms; };
struct ieee80211_regdomain { unsigned n_reg_rules; char alpha2[2]; struct ieee80211_reg_rule reg_rules[65]; };
static unsigned logs;
static void ath11k_warn(struct ath11k_base *ab, const char *format, ...) { (void)ab; (void)format; logs++; }
#include "actual-cn-helper.h"
int main(void) {
 struct ath11k_base ab = {0};
 unsigned checks = 0;
 for (unsigned scenario = 0; scenario < 7; scenario++) {
  struct ieee80211_regdomain actual = { .n_reg_rules = 5, .alpha2 = {'C','N'} };
  for (unsigned i = 0; i < 65; i++) actual.reg_rules[i] = (struct ieee80211_reg_rule){{5170000+i,5250000+i,80000},{600,3000},0x51,60000};
  actual.reg_rules[4].freq_range = (struct ieee80211_freq_range){5735000,5835000,160000};
  if (scenario==1) actual.alpha2[0]='U';
  if (scenario==2) actual.n_reg_rules=0;
  if (scenario==3) actual.n_reg_rules=65;
  if (scenario==4) actual.reg_rules[4].freq_range.max_bandwidth_khz=80000;
  if (scenario==5) actual.reg_rules[4].freq_range.end_freq_khz=5835001;
  if (scenario==6) actual.n_reg_rules=64;
  struct ieee80211_regdomain expected=actual;
  if (scenario==0 || scenario==6) expected.reg_rules[4].freq_range.max_bandwidth_khz=80000;
  logs=0; ath11k_preserve_cn_bw(&ab,&actual);
  assert(memcmp(&actual,&expected,sizeof(actual))==0); checks++;
  assert(logs==((scenario==0 || scenario==6)?1u:0u)); checks++;
 }
 printf("{\"passed\":true,\"checks\":%u,\"scenarios\":7,\"actualSourceFunction\":true,\"kernelIOMocked\":true}\n",checks);
 return 0;
}
