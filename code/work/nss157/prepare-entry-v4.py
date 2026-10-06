from pathlib import Path

r = Path(__file__).resolve().parent
def put(name, text):
    p = r / name
    assert not p.exists(), name
    p.write_text(text, encoding='utf-8', newline='')

s = (r/'module-stage.mjs').read_text(encoding='utf-8')
assert s.count("'./payload-v2.mjs'") == 1
assert s.count("'work/nss149/classifier.lua'") == 1
s = s.replace("'./payload-v2.mjs'", "'./payload-v3.mjs'").replace("'work/nss149/classifier.lua'", "'work/nss157/classifier-current-full.lua'")
put('module-stage-v2.mjs', s)
s = (r/'epoch-driver-v3.mjs').read_text(encoding='utf-8').replace("'./session-binding-v3.mjs'", "'./session-binding-v4.mjs'").replace("'./module-stage.mjs'", "'./module-stage-v2.mjs'").replace('/run5/', '/run7/').replace('/run6/', '/run8/')
put('epoch-driver-v4.mjs', s)
s = (r/'pilot-supervisor-v3.mjs').read_text(encoding='utf-8').replace("'./session-binding-v3.mjs'", "'./session-binding-v4.mjs'").replace("'./epoch-driver-v3.mjs'", "'./epoch-driver-v4.mjs'").replace("?'/run5':'/run6'", "?'/run7':'/run8'")
put('pilot-supervisor-v4.mjs', s)
s = (r/'session-binding-v3.mjs').read_text(encoding='utf-8').replace("'./session-binding-v2.mjs'", "'./session-binding-v3.mjs'").replace('/entry-qualified-v3.json', '/entry-qualified-v4.json')
put('session-binding-v4.mjs', s)
print('New active complete-query adapter and exact codec prepared; failed run5 retained, new run7/run8 only.')
