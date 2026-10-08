# Normal-flow resident controller development batch

Continue from committed RC1 `ee0c0ed`. The next milestone is normal-flow admission and a longer bounded coordinator soak. Existing five-WAN/advanced QoS/CPU/rollback hardware proofs remain valid.

The product controller observes existing local IPv4 sockets and the authenticated permanent classifier. It creates no game, download, fixture, socket or router policy. Known, readable OS process identity and exact socket ownership are required; only existing TCP BULK and budget-admitted UDP RT classes may reach the unchanged three-slot data plane. Unknown and ambiguous ownership stays software. Two selected TCPs must have different existing WANs. No connection is moved to another WAN.

All per-generation limits stay unchanged: source6, native hard120, owner180, client180 where a test client exists, exec9000/raw65536/bundle73728/record1MiB. Each generation uses a fresh downloaded/SHA/gzip checkpoint and independently verified restoration. There is no forced controller kill, native deadline extension or terminal gate reopening.

Local batch: normal socket/identity policy; passive reader; adapter to the proven RC1 entry; bounded wait/stop/restore coordinator. Regression precedes production integration. No formal NSS/v number or individual hardware run is created for P2 fixes.

Predefined integration soak: four separate 90-second generations, coordinator minimum900 / maximum1200 seconds; each generation must fully restore before another. A separate test harness may provide the already authorized bounded owned TCP/UDP simulator. The product controller itself never starts that load. No automatic fixture retry. At most four simulator launches; each retains original180-second client/210-second guard/250-second server and32Mbps/64KiB constraints. This is simulated normal connection turnover, not human game acceptance or uninterrupted15-minute NSS.

P0 immediately stops new writes and restores. A failed generation is retained and stops this run. No new fault injection, tap, QoS, class, CPU, Wi-Fi/autorate/ECN feature or old hardware revalidation.

After passing the bounded integration and final restoration, end this batch. Permanent/default NSS remains a separate deployment decision; do not silently convert this finite controller into an indefinite service.
