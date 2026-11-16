# 三遍 Vision 识别逐字投票：<书>.txt（150dpi 基准）＋ <书>__d250.txt ＋ <书>__raw.txt（扫描原图）
# 按坐标配对同一行 → difflib 逐字对齐 → 分歧处用参考语料的二元字频打分（外加每多一遍识别支持 +1.2）
# 参考语料：1000 题（PDF 文字层）＋ 精讲精练 / 背诵手册的识别文字
# 输出：<书>__vote.txt（格式同 ocr.js 输出），改动清单写到 work/vote_<书>.log
import sys, os, re, json, math, difflib, collections
import fitz
sys.path.insert(0, os.path.dirname(__file__))
from ocrlines import load
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = '/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/'

def corpus():
    cache = f'{B}/work/bigram.json'
    if os.path.exists(cache):
        d = json.load(open(cache)); return collections.Counter(d['u']), collections.Counter(d['b'])
    texts = []
    for f in ['questions2.json', 'answers.json']:
        def walk(x):
            if isinstance(x, str): texts.append(x)
            elif isinstance(x, dict): [walk(v) for v in x.values()]
            elif isinstance(x, list): [walk(v) for v in x]
        walk(json.load(open(f'{B}/work/{f}')))
    for f in ['精讲精练.txt', '背诵手册_上册.txt', '背诵手册_下册.txt']:
        for l in open(f'{B}/ocr/{f}', encoding='utf-8'):
            if '\t' in l: texts.append(l.split('\t', 1)[1].strip())
    u = collections.Counter(); b = collections.Counter()
    for t in texts:
        u.update(t)
        b.update(t[i:i + 2] for i in range(len(t) - 1))
    json.dump({'u': u, 'b': b}, open(cache, 'w'), ensure_ascii=False)
    return u, b

U, BG = corpus()
N = sum(U.values()); V = len(U) + 1
def lp(a, c):
    pc = (U.get(c, 0) + 0.5) / (N + V)
    return math.log((BG.get(a + c, 0) + 2.0 * pc) / (U.get(a, 0) + 2.0))
def score(s):
    return sum(lp(s[i], s[i + 1]) for i in range(len(s) - 1))

def xform(book, mode):
    """把 raw 模式（扫描原图坐标）换算到页面坐标：图在页上的横向位置因页而异"""
    if mode != 'raw': return None
    d = fitz.open(PDF + book + '.pdf'); T = {}
    for i, p in enumerate(d):
        bb = max(p.get_image_info(), key=lambda x: x['bbox'][2] - x['bbox'][0])['bbox']
        W, H = p.rect.width, p.rect.height
        T[i] = (bb[0] / W * 1000, (bb[2] - bb[0]) / W, bb[1] / H * 1000, (bb[3] - bb[1]) / H)
    return T

def match(z, others):
    x0, y0, x1, y1, t = z; best = None
    for o in others:
        ov = min(y1, o[3]) - max(y0, o[1])
        if ov < 0.5 * (y1 - y0): continue
        if abs(o[0] - x0) < 18 and abs(o[2] - x1) < 18:
            d = abs(o[0] - x0) + abs(o[2] - x1)
            if best is None or d < best[0]: best = (d, o)
    return best[1][4] if best else None

def vote(base, cands):
    """base 串 + 若干候选串 → 投票后的串"""
    cands = [c for c in cands if c and c != base]
    if not cands: return base, []
    # 以 base 为骨架，找出每个候选与 base 的差异区间
    regions = []   # (i1, i2, alt)
    for c in cands:
        sm = difflib.SequenceMatcher(None, base, c, autojunk=False)
        if sm.ratio() < 0.6: continue
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != 'equal': regions.append((i1, i2, c[j1:j2]))
    if not regions: return base, []
    # 合并重叠区间
    regions.sort()
    groups = []
    for r in regions:
        if groups and r[0] <= groups[-1]['i2'] and (r[0] < groups[-1]['i2'] or r[0] == r[1] == groups[-1]['i1']):
            g = groups[-1]; g['i2'] = max(g['i2'], r[1]); g['alts'].append(r)
        else: groups.append({'i1': r[0], 'i2': r[1], 'alts': [r]})
    out = []; pos = 0; changes = []
    for g in groups:
        i1, i2 = g['i1'], g['i2']
        out.append(base[pos:i1])
        opts = collections.Counter()
        opts[base[i1:i2]] += 1
        for a1, a2, alt in g['alts']:
            opts[base[i1:a1] + alt + base[a2:i2]] += 1
        L = base[max(0, i1 - 1):i1]; R = base[i2:i2 + 1]
        best = max(opts, key=lambda s: score(L + s + R) + 1.2 * opts[s] - 0.8 * sum(1 for ch in s if ord(ch) < 128 and not ch.isalnum()))
        if best != base[i1:i2]: changes.append((base[max(0, i1 - 4):i2 + 4], best))
        out.append(best); pos = i2
    out.append(base[pos:])
    return ''.join(out), changes

if __name__ == '__main__':
    book = sys.argv[1]
    P0 = load(f'{B}/ocr/{book}.txt')
    runs = []
    for mode in ['d250', 'raw']:
        f = f'{B}/ocr/{book}__{mode}.txt'
        if not os.path.exists(f): continue
        P = load(f); T = xform(book, mode)
        if T:
            for pg in P:
                ox, sx, oy, sy = T[pg]
                P[pg] = [(round(ox + x0 * sx), round(oy + y0 * sy), round(ox + x1 * sx), round(oy + y1 * sy), t) for x0, y0, x1, y1, t in P[pg]]
        runs.append(P)
    log = open(f'{B}/work/vote_{book}.log', 'w'); n = 0
    with open(f'{B}/ocr/{book}__vote.txt', 'w') as o:
        for pg in sorted(P0):
            o.write(f'##FILE p_{pg:04d}.png\n')
            for z in P0[pg]:
                cands = [match(z, R.get(pg, [])) for R in runs]
                t, ch = vote(z[4], cands)
                for a, b in ch: log.write(f'p{pg}\t{a}\t→ {b}\n'); n += 1
                o.write(f'{z[0]} {z[1]} {z[2]} {z[3]}\t{t}\n')
    print(book, 'changes', n)
