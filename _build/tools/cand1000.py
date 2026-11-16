# 押题卷选题用：列 1000 题候选（长题干＝材料型优先）。python3 cand1000.py 科 题型 [最短题干] [每章上限]
import json, re, sys, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHK = json.load(open(f'{R}/_build/notes/check_book.json'))
p, t = sys.argv[1], sys.argv[2]; mn = int(sys.argv[3]) if len(sys.argv) > 3 else 90; per = int(sys.argv[4]) if len(sys.argv) > 4 else 99
s = open(f'{R}/题库/data_{p}.js').read(); i = re.search(r'POL\.\w+\s*=', s).end(); d = json.JSONDecoder().raw_decode(s[i:].lstrip())[0]
used = set()
for f in os.listdir(f'{R}/_build/notes/yati') if os.path.isdir(f'{R}/_build/notes/yati') else []:
    if f.endswith('.json'): used |= {q.get('from') for q in json.load(open(f'{R}/_build/notes/yati/{f}'))['qs']}
import collections, math
def G(t):
    t = re.sub(r'[^一-鿿A-Za-z0-9]', '', t); return collections.Counter(t[i:i+2] for i in range(len(t)-1))
def cos(a, b):
    n = sum(v * b.get(k, 0) for k, v in a.items()); return n / (math.sqrt(sum(v*v for v in a.values())) * math.sqrt(sum(v*v for v in b.values())) or 1)
ps = open(f'{R}/套卷/data_papers.js').read(); PP = json.loads(ps[ps.index('=')+1:ps.rindex(';')])
PG = [G(q['stem'][-80:] + ''.join(q.get('opts') or [])) for pp in PP if pp['kind'] != 'yt' for q in pp['qs']]
def dup(q):
    g = G(q['stem'][-80:] + ''.join(q['opts'])); return max(cos(g, x) for x in PG) > 0.5
by = {}
for q in d['qs']:
    if q['t'] != t or q['id'] in CHK or len(q['stem']) < mn or q['id'] in used or dup(q): continue
    by.setdefault(q['ch'], []).append(q)
for ch in sorted(by):
    for q in sorted(by[ch], key=lambda q: -len(q['stem']))[:per]:
        st = q['stem'].replace('\n', ' ')
        lk = (q.get('lk') or '|').split('|')[1][:10]
        print(f"{q['id']} {q['ans']} c{ch} [{lk}] …{st[-70:]} || " + ' | '.join(f"{L}.{o[:22]}" for L, o in zip('ABCD', q['opts'])))
