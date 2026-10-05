from pathlib import Path
p=Path('work/nss119/save-evidence.py');s=Path('work/nss118/save-evidence.py').read_text(encoding='utf-8').replace('NSS118','NSS119').replace('nss118','nss119').replace('NSS117','NSS118').replace('nss117','nss118')
s=s.replace("len(manifest['sources'])==1331","len(manifest['sources'])==1364").replace("'historicPrefixSources':1331","'historicPrefixSources':1364").replace("'upload-ack.mjs','upload-server.py'","'bounded-pacer.mjs','upload-ack.mjs','upload-server.py'").replace("'save-evidence.py']","'build-report.py','save-evidence.py']")
s=s.replace("qual['onlyOfferedUploadChanged']and len(qual['checks'])==9", "qual['onlyUploadPacingChanged']and len(qual['checks'])==4")
s=s.replace("'onlyOfferedUploadChanged':True,'offeredAveragePerConnectionMbps':32,'instantaneousLoadCatchupStillPossible':True", "'onlyUploadPacingChanged':True,'offeredUploadMbps':32,'maximumPacerCreditBytes':65536,'instantaneousLoadCatchupStillPossible':False,'sameWanAs118':False")
s=s.replace("'boundInputs':857","'boundInputs':890").replace("'smallerRateTransitionRestoredThroughput':False","'boundedPacerRestoredNssThroughput':False").replace("qualifiedExperimentalEntryBoundInputs':857","qualifiedExperimentalEntryBoundInputs':890")
start=s.index("text=f'''");end=s.index("for name,title",start)
s=s[:start]+"""text=f'''更新：{when}，北京时间。最新NSS119；常驻68/config581b5d46…c791d7、4859/17139保持，实验全撤销。

**32Mbps上传改为最多64KiB信用，避免阻塞期间累积补发债务；原双向30/29/1队列和6/27/100期限不变。WAN{m['oneWan']}完整20秒A/B/A2、ECM0→2→0、四leaf/mark/NAT/affinity及恢复通过。服务器确认{speeds}Mbps，A/A2回到约31Mbps，B仍只有16.33Mbps。**

见 [实际指标](../evidence/nss119-metrics.json)、[完整轮次](../evidence/nss119-trial.json)、[汇总](../evidence/nss119-mainline.json)、[上行](../evidence/nss119-uplink-proof.json)、[关闭](../evidence/nss119-endpoint-closure.json)、[终态](../evidence/nss119-final-audit.json)。

- UDP收/发{udp}，上下RT drop0，上bulk drop{summary['bulkLeafDrop']}、parent overlimits+{trans['uplinkParentAndLeafClassDelta']['8e00:50']['overlimits']}；新CPU/游戏/精确限速均不验收。B吞吐仍降，当前发送器债务不能作为唯一解释。与118的WAN1不同，本轮为WAN5，不把两轮差异直接归因pacer；本轮A/B/A2是同一对flow。
- 4项本地合同验证含真实callback时长模型及10秒阻塞后的64KiB上限，硬件helper与118/116逐字节相同。新的890项入口/独立100秒守护/完整checkpoint、端点180秒FW与210秒客户端均完成；终态source{final['queryAge']:.2f}、ECM关闭全零、无事务/stage/state/模块，两物理mq/fq_codel恢复，WAN4仍down四路PBR不改。旧118 runtime逐字节保存，原始私有证据冻结。
- 下一步只提高受控上行组30→60Mbps，bulk29→59/RT1/ceil60，保留下行30和同一有界32Mbps发送器。自然选择WAN5而非改PBR；未知flow默认拒绝。先验证方向布局/原预算错误拒绝/部分恢复及payload上限，再新checkpoint与独立撤销。若不拥塞时吞吐恢复，再定位30组的拥塞/AQM，不靠同时调整RT/其它参数。
- 不动常驻classifier/upTag0，不重装/操作UI/新下载/扩WAN/共享全局预算/WiFi/autorate；最后一次集中真人CS2验收。夜间到10:00，09:50起收尾和晨间报告、推送后暂停接续。
'''
"""+s[end:]
start=s.index("p=repo/'AGENTS.md'");end=s.index("p=repo/'docs/ARTIFACT_INDEX.md'",start)
s=s[:start]+"""p=repo/'AGENTS.md';head,tail=p.read_text(encoding='utf-8').split('\\n',1);p.write_text(head+'\\n\\n最新NSS119：只给32Mbps上传增加64KiB信用上限、890项/4合同；WAN5真实完整20秒A/B/A2、ECM0/2/0、四leaf/mark/NAT/affinity/6续租及恢复通过，确认上传'+speeds+'Mbps，UDP'+udp+'、RTdrop0、上bulk36/parent9804 overlimit。A/A2约31、B约16，未验收CPU；较118 WAN1变化不作因果比较。下一步仅上行组30→60、bulk29→59/RT1/ceil60、下行30，保持有界32发送与全部期限，自然选择WAN5不改PBR。原120候选尚未现场；常驻68不变、终态4859/17139/source2.97、ECM全零、双mq/fq_codel恢复、端点关闭、旧118原字节保留。UI停用、不新下载/重装/扩WAN/WiFi/共享预算/autorate；09:50后收尾、10点前暂停本夜接续；STATE为准。\\n\\n'+tail,encoding='utf-8')
"""+s[end:]
p.write_text(s,encoding='utf-8')
