import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/west/edit')
from concurrent.futures import ThreadPoolExecutor
import timeline as T, core as C
jobs = []
plan = {}
for i, s in enumerate(T.SHOTS + [T.CARD]):
    f, _ = C.srcmap(s)
    a = min(f(s['t0']), f(s['t1'])) - 0.12
    b = max(f(s['t0']), f(s['t1'])) + 0.15
    a = max(0.0, a)
    jobs.append((s['src'], a, b))
    plan[i] = (s['src'], a, b)
json.dump(plan, open(C.ROOT + 'edit/int_plan.json', 'w'), indent=1)
with ThreadPoolExecutor(4) as ex:
    for p in ex.map(lambda j: C.extract(*j), jobs):
        print(p, flush=True)
print('DONE')
