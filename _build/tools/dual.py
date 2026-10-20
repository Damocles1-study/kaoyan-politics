# Build an improved OCR file for 试题: per Vision line, swap in the PDF text-layer line if it is cleaner.
import fitz, collections, sys, re
sys.path.insert(0,'/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/tools')
import ocrlines
S='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
d=fitz.open('/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/1000题_试题分册.pdf')
V=ocrlines.load(S+'/ocr/1000题_试题分册.txt')
freq=collections.Counter()
for b in ['1000题_解析分册','背诵手册_上册','背诵手册_下册','精讲精练']:
    for pg in ocrlines.load(f'{S}/ocr/{b}.txt').values():
        for z in pg: freq.update(c for c in z[4] if '一'<=c<='鿿')
def bad(t): return sum(1 for c in t if '一'<=c<='鿿' and freq[c]<=2)
out=open(S+'/ocr/1000题_试题分册_dual.txt','w'); swaps=0; ex=[]
for pi in sorted(V):
    p=d[pi]; W,H=p.rect.width,p.rect.height
    TL=[]
    for b in p.get_text('rawdict')['blocks']:
        for l in b.get('lines',[]):
            chars=[c for s in l['spans'] for c in s['chars']]
            if not chars: continue
            TL.append(chars)
    out.write(f'##FILE p_{pi:04d}.png\n')
    for x0,y0,x1,y1,t in V[pi]:
        X0,Y0,X1,Y1=x0*W/1000,y0*H/1000,x1*W/1000,y1*H/1000
        cand=''.join(c['c'] for chars in TL for c in chars if X0-2<=(c['bbox'][0]+c['bbox'][2])/2<=X1+2 and Y0-1<=(c['bbox'][1]+c['bbox'][3])/2<=Y1+1)
        cand=cand.strip()
        if cand and abs(len(cand)-len(t))<=max(2,len(t)*0.12) and bad(cand)<bad(t):
            swaps+=1
            if len(ex)<12: ex.append((t,cand))
            t=cand
        out.write(f'{x0} {y0} {x1} {y1}\t{t}\n')
out.close()
print('swaps',swaps); [print(' V:',a,'\n T:',b) for a,b in ex]
