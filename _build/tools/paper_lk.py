# 套卷题 → 讲义节 的候选匹配（只给建议；最终以 notes/paper_notes/*.json 里的 lk 为准）
# 打分＝题面（题干＋正确选项＋解析）与讲义节正文的字二元组 TF-IDF 余弦 ＋ 相似的 1000 题已登记的 lk 加分
# 输出 work/paper_lk_auto.json：{"卷:题号": [["讲义/xx.html#dN", 标题, 分], ...前 3]}
import json, os, re, glob, math, html, collections, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(B)
PREF = {'my': ['马原'], 'mz': ['毛中特'], 'xg': ['习概'], 'sg': ['史纲'], 'sx': ['思法'], 'sz': ['习概', '毛中特', '思法']}

def txt(s): return html.unescape(re.sub(r'<[^>]+>', '', s or ''))
def grams(s):
    s = re.sub(r'[^一-鿿A-Za-z0-9]', '', s)
    return collections.Counter(s[i:i + 2] for i in range(len(s) - 1))

def sections():
    out = []
    for f in sorted(glob.glob(f'{ROOT}/讲义/*.html')):
        rel = '讲义/' + os.path.basename(f); src = open(f, encoding='utf-8').read()
        for sid, body in re.findall(r'<section class="card" id="(d\d+)">(.*?)</section>', src, re.S):
            h = re.search(r'<h2>(.*?)</h2>', body, re.S)
            title = re.sub(r'^\d+', '', txt(h.group(1)).strip()) if h else sid
            if '一页纸' in title: continue
            out.append({'u': f'{rel}#{sid}', 'title': title, 'subj': os.path.basename(f).split('_')[0], 'g': grams(title * 3 + txt(body))})
    return out

def load_js(p):
    s = open(p, encoding='utf-8').read(); i = re.search(r'POL\.\w+\s*=', s).end()
    return json.JSONDecoder().raw_decode(s[i:].lstrip())[0]

def main():
    S = sections(); N = len(S)
    df = collections.Counter(g for x in S for g in x['g'])
    idf = {g: math.log(N / (1 + c)) + 1 for g, c in df.items()}
    def vec(c): v = {g: n * idf.get(g, 1) for g, n in c.items() if g in idf}; z = math.sqrt(sum(x * x for x in v.values())) or 1; return {g: x / z for g, x in v.items()}
    for x in S: x['v'] = vec(x['g'])
    # 1000 题（带 lk 的）
    Q1 = []
    for p in ['my', 'mz', 'xg', 'sg', 'sx']:
        d = load_js(f'{ROOT}/题库/data_{p}.js')
        for q in d['qs']:
            if q.get('lk'): Q1.append((vec(grams(q['stem'] + ''.join(q.get('opts') or []))), q['lk'].split('|')[0]))
    s = open(f'{ROOT}/套卷/data_papers.js').read(); P = json.loads(s[s.index('=') + 1:s.rindex(';')])
    out = {}
    for p in P:
        for q in p['qs']:
            t = q['stem'] + ''.join(q.get('asks') or [])
            if q['t'] != 'e': t += ''.join(o for L, o in zip('ABCD', q['opts']) if L in q['ans']) + (q.get('jx') or '')[:300]
            else: t += (q.get('ea') or '')[:400]
            v = vec(grams(t))
            v1 = vec(grams(q['stem'] + ''.join(q.get('opts') or [])))
            bonus = collections.Counter()
            for qv, lk in Q1:
                c = sum(w * qv.get(g, 0) for g, w in v1.items())
                if c > 0.45: bonus[lk] += c
            sc = []
            for x in S:
                if x['subj'] not in PREF[q['sj']]: continue
                c = sum(w * x['v'].get(g, 0) for g, w in v.items()) + 0.5 * bonus.get(x['u'], 0)
                sc.append((round(c, 3), x['u'], x['title']))
            sc.sort(reverse=True)
            out[f"{p['k']}:{q['no']}"] = [[u, t, c] for c, u, t in sc[:3]]
    json.dump(out, open(f'{B}/work/paper_lk_auto.json', 'w'), ensure_ascii=False, indent=0)
    print('wrote', len(out))

if __name__ == '__main__': main()
