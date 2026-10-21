# -*- coding: utf-8 -*-
# 对比试题分册「Vision 识别」与「PDF 自带文字层」逐行差异，抽样看哪一方更可靠
import fitz, sys, random, difflib
sys.path.insert(0,'/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/tools')
import ocrlines
B='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
d=fitz.open('/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/1000题_试题分册.pdf')
V=ocrlines.load(B+'/ocr/1000题_试题分册.txt')
pairs=[]
for pi in sorted(V):
    if pi<5: continue
    p=d[pi]; W,H=p.rect.width,p.rect.height
    chars=[c for b in p.get_text('rawdict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] for c in s['chars']]
    for x0,y0,x1,y1,t in V[pi]:
        X0,Y0,X1,Y1=x0*W/1000,y0*H/1000,x1*W/1000,y1*H/1000
        cand=''.join(c['c'] for c in chars if X0-2<=(c['bbox'][0]+c['bbox'][2])/2<=X1+2 and Y0-1<=(c['bbox'][1]+c['bbox'][3])/2<=Y1+1).strip()
        if cand and cand!=t and abs(len(cand)-len(t))<=1:
            sm=difflib.SequenceMatcher(None,t,cand)
            ops=[(t[a:b],cand[c:e]) for tag,a,b,c,e in sm.get_opcodes() if tag!='equal']
            if 0<len(ops)<=2: pairs.append((pi,t,cand,ops))
print('lines differing slightly:',len(pairs))
import collections
c=collections.Counter((a,b) for _,_,_,ops in pairs for a,b in ops)
print('top substitutions (Vision -> textlayer):',c.most_common(60))
