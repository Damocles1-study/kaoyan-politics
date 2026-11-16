# 查关键词出现在哪些讲义节：python3 kw.py 词1 词2 …
import re, glob, sys, os, html
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for w in sys.argv[1:]:
    hits = []
    for f in sorted(glob.glob(f'{R}/讲义/*.html')):
        for sid, b in re.findall(r'<section class="card" id="(d\d+)">(.*?)</section>', open(f).read(), re.S):
            t = html.unescape(re.sub(r'<[^>]+>', '', b))
            if w in t:
                h = re.search(r'<h2>(.*?)</h2>', b, re.S); hits.append(f"{os.path.basename(f)[:-5]}#{sid}({re.sub('<[^>]+>','',h.group(1))[:12] if h else ''})×{t.count(w)}")
    print(w, '→', ' '.join(hits) or '无')
