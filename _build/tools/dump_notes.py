# 写套卷秒杀笔记用的紧凑通读稿：python3 dump_notes.py 卷k [起 止] [jx截断字数]
import json, sys, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s = open(f'{R}/套卷/data_papers.js').read(); P = {p['k']: p for p in json.loads(s[s.index('=') + 1:s.rindex(';')])}
A = json.load(open(f'{R}/_build/work/paper_lk_auto.json'))
k = sys.argv[1]; a = int(sys.argv[2]) if len(sys.argv) > 2 else 1; b = int(sys.argv[3]) if len(sys.argv) > 3 else 38
J = int(sys.argv[4]) if len(sys.argv) > 4 else 160
def cut(t, n=60, m=90): return t if len(t) <= n + m + 10 else t[:n] + '…' + t[-m:]
for q in P[k]['qs']:
    if not a <= q['no'] <= b: continue
    lk = ' / '.join(f"{i+1}.{x[1][:18]}" for i, x in enumerate(A.get(f"{k}:{q['no']}", [])))
    if q['t'] != 'e':
        print(f"#{q['no']} {q['ans']} [{q['sj']}] {cut(q['stem'])}")
        print('  ' + ' | '.join(f'{L}.{o}' for L, o in zip('ABCD', q['opts'])))
        if q.get('jx'): print('  J:', q['jx'][:J].replace('\n', ' '))
    else:
        print(f"#{q['no']} 分析 [{q['sj']}] {cut(q['stem'], 150, 150)}")
        for x in q['asks']: print('  Q', x)
        print('  E:', (q.get('ea') or '')[:J * 4].replace('\n', ' '))
    print('  L:', lk)
