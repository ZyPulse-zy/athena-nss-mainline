-- Reviewable additive preparation, never executes commands. The independent
-- deployment guardian must own rollback before any of these operations run.
local M={}
function M.routing_nft()
 local nft={
   'add chain inet rp_pbr mark_w6',
   'add rule inet rp_pbr mark_w6 ct mark set (ct mark & 0xff00ffff) | 0x00060000 return',
   'add rule inet rp_pbr local_output ct state new ct mark & 0x00ff0000 == 0 oifname "rpwan6" ct mark set (ct mark & 0xff00ffff) | 0x00060000 comment "athena-wan6-local-output"',
   'add rule inet rp_pbr forwarding_counters iifname "br-lan" oifname "rpwan6" ct mark & 0x00ff0000 == 0x00060000 counter comment "athena-wan6-lan-egress"',
   'add rule inet fw4 srcnat oifname "rpwan6" jump srcnat_wan comment "athena-wan6-srcnat"',
   'add rule inet fw4 accept_to_wan meta nfproto ipv4 oifname "rpwan6" ct state invalid drop comment "athena-wan6-nat-leak"',
   'add rule inet fw4 accept_to_wan oifname "rpwan6" accept comment "athena-wan6-forward"'}
 return table.concat(nft,'\n')..'\n'
end
function M.plan(f)
 assert(f.rollbackVerified and f.independentGuardianReady,'Independent rollback required')
 assert(f.installedBaselineVerified and f.fiveWansStable and f.protectedFilesPinned,'Current baseline required')
 assert(f.physicalMbps==1000 and f.table106Free and f.rules906And1006Free,'Physical/routing prerequisites failed')
 assert(f.campus6Absent and f.rpwan6Absent and f.rpifb6Absent and f.auth6Absent,'WAN6 objects already owned')
 assert(f.wan6OriginalProto=='dhcpv6','Preserve the physical IPv6 interface')
 assert(type(f.mac)=='string'and f.mac:match('^02:%x%x:%x%x:%x%x:%x%x:%x%x$')and f.macUnused,'Unused local MAC required')
 assert(f.firewallZoneName=='wan' and f.firewallMasquerade and f.macMapPinned,'Firewall/MAC-map prerequisites failed')
 assert(f.gameEnabled==false,'Game rules need a separate risk-reviewed stage')
 local commands={
  'ip link add link wan name rpwan6 address '..f.mac..' type macvlan mode bridge',
  'ip link set dev rpwan6 up',
  'ip -4 rule add pref 906 oif rpwan6 lookup 106',
  'ip -4 route add unreachable default table 106 metric 42760',
  'ip -4 rule add pref 1006 fwmark 0x00060000/0x00ff0000 lookup 106',
  'uci set network.campus6=interface',
  'uci set network.campus6.proto=dhcp',
  'uci set network.campus6.device=rpwan6',
  'uci set network.campus6.auto=0',
  'uci set network.campus6.peerdns=0',
  'uci set network.campus6.ip4table=106',
  'uci set network.campus6.metric=106',
  'uci set network.campus6.delegate=0',
  'uci set network.campus6.sendclientid=hardware',
  'uci add_list firewall.@zone[1].network=campus6',
  'uci commit network',
  'uci commit firewall',
  'ip link add rpifb6 type ifb',
  'ip link set dev rpifb6 up',
  'tc qdisc add dev rpwan6 root handle 8061: cake bandwidth 40mbit diffserv4 dual-srchost nat overhead 38 mpu 84',
  'tc qdisc add dev rpifb6 root handle 8062: cake bandwidth 70mbit diffserv4 dual-dsthost nat ingress overhead 38 mpu 84',
  'tc qdisc add dev rpwan6 handle ffff: ingress',
  'tc filter add dev rpwan6 parent ffff: protocol ip pref 10 matchall action mirred egress redirect dev rpifb6'}
 -- Native source classifier performs precise basic filter installation from
 -- the captured WAN6 queue contract. Existing ten queue roots are untouched.

 return{commands=commands,nft=M.routing_nft(),requiresApproval=true,
  originalFiveMarksPreserved=true,existingNatMigration=false,restartRouter=false,
  credentials='Existing private MiniEAP config provider; no argv, stdout or evidence',
  accountInterface='campus6',accountDevice='rpwan6',routeTable=106,
  persistence={'Append exactly one unused WAN6 MAC to the pinned existing map',
   'Install additive wan6-routing.nft and gated PBR/shaper/auth/health candidates',
   'Keep normal buckets, sticky sets and main-route choices at WAN1-5',
   'Replace only existing watcher instances without invoking global queue teardown',
   'Private fresh checkpoint and independent guardian are deployment prerequisites'},
  nextStages={'Capture WAN6 roots and extend source config/journals',
   'Add only authentication/autorate instance wan6 after private credential install',
   'One approved complete native/source stop-restore-replace-start transaction',
   'Read actual CREATE/REMOVE acknowledgements, both tags and per-flow bytes',
   'Enable game policy only after exclusions and risk review'}}
end
function M.rollback(f)
 assert(f.checkpointOwned and f.bootMatches and f.fileHashesMatch,'Refuse a foreign or drifted checkpoint')
 -- These are ordered guardian stages, not shell fragments to execute blindly.
 -- Hardware cleanup may not advance past an unconfirmed firmware removal.
 return {
  {stage='withdraw-new-routing',actions={'Withdraw WAN6 game readiness first',
   'Remove only the journaled jump/rules by verified handles; retain five-account maps'}},
  {stage='native-recovery',actions={'Stop the single native owner using its existing guardian',
   'Require exact REMOVE/firmware-absent receipts and full physical queue/guard restoration'},
   advanceOnlyWhen='nativeStoppedAndFirmwareAbsentAndOriginalPhysicalQueuesRestored'},
  {stage='source-recovery',actions={'Stop candidate source with its pinned generation/hash',
   'Require exact owned selector/journal cleanup on all twelve roots before restoring original source pointer'},
   advanceOnlyWhen='candidateSourceOwnedRulesAbsent'},
  {stage='account6-isolation',actions={'Stop only wan6 authentication and autorate instances',
   'Down only campus6 and remove its exact journaled DHCP routes',
   'Retain fwmark rule 1006 and unreachable table 106 while any WAN6-marked CT remains'},
   existingNatMigration=false,advanceOnlyWhen='table106HasOnlyOwnedUnreachableDefault'},
  {stage='persistent-restore',actions={'Restore checkpointed changed files only if current bytes equal journaled candidate hashes',
   'Restore absence of new account/profile files; restore original MAC map, init scripts and source pointer',
   'Remove only new owned rpwan6/rpifb6 and nft additions; preserve original DHCPv6 wan6'}},
  {stage='resume-five',actions={'Start original source and native payload with verified original build pins',
   'Resume original watcher instances without global queue teardown',
   'Verify five accounts, protected services/configuration, all ten fixed queue contracts and fresh NSS receipts'}},
  {stage='retire-route-fence',actions={'Delete only rule 1006/unreachable route after two complete fresh CT reads find zero WAN6 marks'},
   advanceOnlyWhen='noWan6CtAndNoSnapshotTruncation',existingNatMigration=false}}
end
return M
