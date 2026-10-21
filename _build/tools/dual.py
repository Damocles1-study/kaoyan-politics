# -*- coding: utf-8 -*-
# 试题分册双源合并（v2）：版面 / 行序用 Vision，文字内容优先用 PDF 自带文字层（字符准确率明显更高）；
# 只有文字层这一行明显更差（生僻字更多＝坏页）才保留 Vision。顺带从两源差异里学习 Vision 形近字纠错表 → notes/ocr_fix.json
import fitz, collections, sys, re, json, difflib
sys.path.insert(0,'/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/tools')
import ocrlines
B='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
d=fitz.open('/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/1000题_试题分册.pdf')
V=ocrlines.load(B+'/ocr/1000题_试题分册.txt')
freq=collections.Counter()
for b in ['1000题_解析分册','背诵手册_上册','背诵手册_下册','精讲精练']:
    for pg in ocrlines.load(f'{B}/ocr/{b}.txt').values():
        for z in pg: freq.update(ch for ch in z[4] if '一'<=ch<='鿿')
def bad(t): return sum(1 for c in t if '一'<=c<='鿿' and freq[c]<=2)
CJK=r'[一-鿿“”‘’《》（）]'
def norm(t):
    t=t.replace('?','？').replace('!','！').replace(';','；').replace('(','（').replace(')','）')
    t=re.sub(r'(?<=%s),|,(?=%s)'%(CJK,CJK),'，',t)
    t=re.sub(r'(?<=%s):|:(?=%s)'%(CJK,CJK),'：',t)
    t=re.sub(r'(?<=[一-鿿]) +(?=[一-鿿])','',t)
    return t
out=open(B+'/ocr/1000题_试题分册_dual.txt','w',encoding='utf-8'); used=kept=0
sub=collections.Counter(); tl_corpus=[]
for pi in sorted(V):
    p=d[pi]; W,H=p.rect.width,p.rect.height
    chars=[]
    for b in p.get_text('rawdict')['blocks']:
        for l in b.get('lines',[]):
            lt=''.join(c['c'] for s in l['spans'] for c in s['chars'])
            if re.search(r'考研|1000|试题分册|分册|^[\d\s]{1,4}$',lt) or re.fullmatch(r'.{0,8}[·•，,.\-]?\s*(单选|多选|分析)\s*',lt): continue
            if l['dir'][1]!=0: continue
            chars+=[c for s in l['spans'] for c in s['chars']]
    out.write(f'##FILE p_{pi:04d}.png\n')
    for x0,y0,x1,y1,t in V[pi]:
        X0,Y0,X1,Y1=x0*W/1000,y0*H/1000,x1*W/1000,y1*H/1000
        cand=''.join(c['c'] for c in chars if X0-2<=(c['bbox'][0]+c['bbox'][2])/2<=X1+2 and Y0-1<=(c['bbox'][1]+c['bbox'][3])/2<=Y1+1).strip()
        cand=norm(cand)
        tok=re.match(r'^\s*(\d{1,3}\s*[.．、,，]|[A-D]\s*[.．、,，])',t)
        same_head = (not tok) or cand.replace(' ','').startswith(tok.group(1).replace(' ','').replace('．','.').replace('，',',')[:-1])
        ratio=difflib.SequenceMatcher(None,t,cand).ratio() if cand else 0
        if cand and pi>=5 and same_head and ratio>=0.6 and abs(len(cand)-len(t))<=max(2,len(t)*0.15) and bad(cand)<=bad(t):
            if cand!=t:
                for tag,a,b2,c,e in difflib.SequenceMatcher(None,t,cand).get_opcodes():
                    if tag=='replace' and b2-a==1 and e-c==1 and '一'<=t[a]<='鿿' and '一'<=cand[c]<='鿿':
                        L=t[a-1] if a>0 else ''; R=t[a+1] if a+1<len(t) else ''
                        if L: sub[(L+t[a], L+cand[c])]+=1
                        if R: sub[(t[a]+R, cand[c]+R)]+=1
            tl_corpus.append(cand); t=cand; used+=1
        else: kept+=1
        out.write(f'{x0} {y0} {x1} {y1}\t{t}\n')
out.close()
print('text-layer lines used',used,'vision kept',kept)
# 学习纠错表：Vision 的错误二字组在干净语料里几乎不出现、改正后的二字组常见
corpus=''.join(tl_corpus); bg=collections.Counter(corpus[i:i+2] for i in range(len(corpus)-1))
fix={}
for (wrong,right),n in sub.most_common():
    if n>=2 and bg[wrong]<=1 and bg[right]>=3 and wrong not in fix: fix[wrong]=right
json.dump(fix,open(B+'/notes/ocr_fix.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('learned fixes',len(fix),list(fix.items())[:40])
