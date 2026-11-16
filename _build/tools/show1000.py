# 看 1000 题若干题全文：python3 show1000.py id1 id2 …
import json, re, sys, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = {}
for p in ['my', 'mz', 'xg', 'sg', 'sx']:
    s = open(f'{R}/题库/data_{p}.js').read(); i = re.search(r'POL\.\w+\s*=', s).end()
    for q in json.JSONDecoder().raw_decode(s[i:].lstrip())[0]['qs']: P[q['id']] = q
J = int(os.environ.get('J', 150))
for k in sys.argv[1:]:
    q = P[k]; st = q['stem'].replace('\n', ' ')
    print(f"## {k} {q.get('ans','')} | {st if len(st) < 260 else st[:90] + '…' + st[-150:]}")
    if q.get('opts'): print('   ' + ' | '.join(f'{L}.{o}' for L, o in zip('ABCD', q['opts'])))
    jx = (q.get('jx') or '') + (q.get('db') or '')
    if jx: print('   J:', jx[:J].replace('\n', ' '))
    elif q.get('jj'): print('   JJ:', q['jj']['t'][:J].replace('\n', ' '))
    if q.get('my'): print('   M:', re.sub('<[^>]+>', '', q['my'])[:120])
