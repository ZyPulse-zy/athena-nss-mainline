from pathlib import Path
r=Path('work/nss117');r.mkdir(exist_ok=True)
s=Path('work/nss106/retry-existing.mjs').read_text(encoding='utf-8').replace('nss106','nss117').replace('nss105','nss116').replace('NSS105','NSS116').replace('after all eight natural candidates missed the UDP WAN','after publication changed during the protected read').replace('retry after natural WAN mismatch','upload retry after publication coherence refusal')
(r/'retry-existing.mjs').write_text(s,encoding='utf-8')
print('Prepared one unchanged-entry retry; no TTL or routing change')
