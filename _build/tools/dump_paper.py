# 通读稿：python3 dump_paper.py 卷k [题号起 题号止] [字段 s/o/j/e]
import json, sys, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s = open(f'{R}/套卷/data_papers.js').read(); P = {p['k']: p for p in json.loads(s[s.index('=') + 1:s.rindex(';')])}
k = sys.argv[1]; a = int(sys.argv[2]) if len(sys.argv) > 2 else 1; b = int(sys.argv[3]) if len(sys.argv) > 3 else 38
F = sys.argv[4] if len(sys.argv) > 4 else 'soje'
for q in P[k]['qs']:
    if not a <= q['no'] <= b: continue
    print(f"#{q['no']} {q.get('ans','')}")
    if 's' in F: print('S', q['stem'] + (' ‖ ' + ' ‖ '.join(q['asks']) if q.get('asks') else ''))
    if 'o' in F and q.get('opts'): print('O', ' | '.join(f'{L}{o}' for L, o in zip('ABCD', q['opts'])))
    if 'j' in F and q.get('jx'): print('J', q['jx'])
    if 'e' in F and q.get('ea'): print('E', q['ea'])
