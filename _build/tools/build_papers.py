# 整卷数据：work/papers_raw.json（parse_papers.py 输出）＋ notes/papers_fix.json（逐题人工校对）→ 套卷/data_papers.js
# notes/papers_fix/<卷>.json 逐题校对 ＋ global.json 全局形近字表 [[原, 改], …]（在逐题校对之后套用）
# 逐题格式：{卷k: {题号: {"字段": [[原文, 改为], ...] 或 "=整段新文本"}}}
#   字段：stem / A B C D / jx / ea / ans；原文找不到会打印 FIX MISS
import json, os, re, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(B)
CN = '一二三四五六七八'
# 2024 起五科题号分布三年一致（README「已知事实」）
def subj(no):
    if no <= 16: return 'my' if no <= 4 else 'mz' if no <= 6 else 'xg' if no <= 9 else 'sg' if no <= 13 else 'sx' if no == 14 else 'sz'
    if no <= 33: return 'my' if no <= 21 else 'mz' if no == 22 else 'xg' if no <= 26 else 'sg' if no <= 29 else 'sx' if no <= 31 else 'sz'
    return {34: 'my', 35: 'xg', 36: 'sg', 37: 'sx', 38: 'sz'}[no]

def clean(s):
    s = s or ''
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'(?<=[一-鿿，。、；：“”（）])[ \t]+(?=[一-鿿，。、；：“”（）])', '', s)
    s = s.replace('“ ', '“').replace(' ”', '”')
    # 识别时被当成缩进而断开的行：上一行不是句末就并回去
    s = re.sub(r'(?<![。！？”：；）)])\n(?![（(][1-6一二三]|第[一二三四五六]|[①②③④⑤]|材料\s*[1-6一二三]|摘|【)', '', s)
    s = re.sub(r'\s*三、\s*材料分析题.*$', '', s, flags=re.S)
    s = re.sub(r'(^|\n)(材料\s*[1-6一二三四])\s*(?=[^\n])', r'\1\2\n', s)
    return s.strip()

def asks_of(stem):
    """末尾从（1）起的那几行是设问；设问折行的续行并回上一问"""
    lines = stem.split('\n')
    idx = [i for i, l in enumerate(lines) if re.match(r'^\s*[（(]1[)）]', l)]
    if not idx: return stem.strip(), []
    i = idx[-1]; asks = []
    for l in lines[i:]:
        if re.match(r'^\s*[（(][1-4][)）]', l) or not asks: asks.append(l.strip())
        else: asks[-1] += l.strip()
    return '\n'.join(lines[:i]).strip(), asks

def main():
    raw = json.load(open(f'{B}/work/papers_raw.json'))
    zt = f'{B}/work/papers_zt.json'
    if os.path.exists(zt): raw.update(json.load(open(zt)))
    fx = {}; FD = f'{B}/notes/papers_fix'
    for f in sorted(os.listdir(FD)) if os.path.isdir(FD) else []:
        if f.endswith('.json') and f != 'global.json': fx.update(json.load(open(f'{FD}/{f}')))
    G = json.load(open(f'{FD}/global.json')) if os.path.exists(f'{FD}/global.json') else []
    def g(s):
        for a, b in G: s = re.sub(a[3:], b, s) if a.startswith('re:') else s.replace(a, b)
        return s
    out = []
    for k in sorted(raw, key=lambda k: (k[:2] != 'x8', k)):
        P = raw[k]; F = fx.get(k, {}); qs = []
        for q in P['qs']:
            no = q['no']; f = F.get(str(no), {})
            d = {'no': no, 't': q['t'], 'sj': subj(no), 'stem': q.get('stem', ''), 'pg': q.get('pg')}
            if q['t'] != 'e':
                d['opts'] = list(q.get('opts') or ['', '', '', ''])
                d['ans'] = q.get('ans', ''); d['jx'] = q.get('jx', '')
            else: d['ea'] = q.get('ea', '')
            # 先统一清洗＋全局形近字，再套逐题校对（这样校对的「原文」与 dump_paper.py 看到的一致）
            d['stem'] = g(clean(d['stem']))
            if 'opts' in d: d['opts'] = [g(clean(o)) for o in d['opts']]; d['jx'] = g(clean(d['jx']))
            else: d['ea'] = g(clean(d['ea']))
            for fld, ch in f.items():
                key, idx = (('opts', 'ABCD'.index(fld)) if fld in 'ABCD' and len(fld) == 1 else (fld, None))
                cur = d[key][idx] if idx is not None else d.get(key, '')
                if isinstance(ch, str) and ch.startswith('='): cur = ch[1:]
                else:
                    for a, b in ch:
                        if a in cur: cur = cur.replace(a, b, 1)
                        else: print('FIX MISS', k, no, fld, a)
                if idx is not None: d[key][idx] = cur
                else: d[key] = cur
            if q['t'] == 'e': d['stem'], d['asks'] = asks_of(d['stem'])
            qs.append(d)
        if k.startswith('x8'):
            n = int(k.split('-')[1])
            meta = {'k': k, 'kind': 'x8', 'name': f'肖八 · 第{CN[n-1]}套', 'sub': f'2027 考研政治冲刺 8 套卷（{CN[n-1]}）', 'src': '肖八试题册'}
        else:
            y = k.split('-')[1]
            meta = {'k': k, 'kind': 'zt', 'name': f'{y} 年真题', 'sub': f'{y} 年全国硕士研究生招生考试思想政治理论', 'src': '近 3 年真题试卷'}
        meta['proof'] = bool(F.get('_done'))
        meta['qs'] = qs; out.append(meta)
        bad = [q['no'] for q in qs if q['t'] != 'e' and (not q['ans'] or not all(q['opts']) or not q['jx'])]
        bade = [q['no'] for q in qs if q['t'] == 'e' and (not q['ea'] or not q['asks'])]
        print(k, len(qs), 'incomplete', bad, 'essay', bade)
    js = '/* 由 _build/tools/build_papers.py 生成，别手改；校对写进 _build/notes/papers_fix/ */\nwindow.PAPERS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(f'{ROOT}/套卷/data_papers.js', 'w').write(js)
    print('wrote', len(js), 'bytes')

main()
