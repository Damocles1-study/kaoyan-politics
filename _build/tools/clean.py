import fitz, numpy as np, sys, os, time
SRC='/Users/zyx/Downloads/新威考研-资料/11408相关/政治'
DST=SRC+'/教材_去水印'
os.makedirs(DST,exist_ok=True)
JOBS=[('27肖1000试题.pdf','1000题_试题分册.pdf','text'),
      ('27肖1000解析.pdf','1000题_解析分册.pdf','text'),
      ('27肖秀荣-背诵手册【上册】.pdf','背诵手册_上册.pdf','text+qr'),
      ('27肖秀荣-背诵手册【下册】《190题》《干扰项总结》《234速查》《学科总结》《分析题必备专题》.pdf','背诵手册_下册.pdf','text+qr'),
      ('27肖秀荣《精讲精练》.pdf','精讲精练.pdf','text'),
      ('政治近3年试卷.pdf','近3年真题试卷.pdf','pixqr'),
      ('讲真题-试卷分册.pdf','讲真题_试卷分册.pdf','pixqr'),
      ('讲真题-试卷解析.pdf','讲真题_解析分册.pdf','pixqr')]
only=sys.argv[1:]
def strip_visible_text(page):
    rects=[fitz.Rect(t['bbox']) for t in page.get_texttrace() if t['type']==0]
    if not rects: return 0
    for r in rects: page.add_redact_annot(r, fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    return len(rects)
def find_qr(a):
    H,W=a.shape
    y0=H-165; x0=W-140
    reg=a[y0:,x0:]<140
    cols=np.where(reg.sum(0)>15)[0]
    if len(cols)==0: return None
    runs=np.split(cols,np.where(np.diff(cols)>8)[0]+1)
    r=runs[-1]
    if not (90<=r[-1]-r[0]<=120): return None
    rows=np.where(reg[:,r[0]:r[-1]+1].sum(1)>3)[0]
    return (x0+r[0]-6, y0+rows[0]-6, min(W,x0+r[-1]+8), min(H,y0+rows[-1]+8))
log=open(DST+'/_清洗日志.txt','a')
for src,dst,mode in JOBS:
    if only and dst not in only: continue
    t=time.time(); d=fitz.open(SRC+'/'+src); nt=0; nq=0; miss=[]
    if 'qr' in mode and mode!='pixqr':
        xr=None
        for p in d:
            for x in p.get_images(full=True):
                if x[2]==430 and x[3]==430: xr=x[0]; p.delete_image(xr); break
            if xr: break
        nq=1 if xr else 0
    for i,p in enumerate(d):
        if 'text' in mode: nt+=strip_visible_text(p)
        if mode=='pixqr':
            x=p.get_images(full=True)[0]
            pix=fitz.Pixmap(d,x[0])
            if pix.alpha: pix=fitz.Pixmap(pix,0)
            g=fitz.Pixmap(fitz.csGRAY,pix) if pix.n>=3 else pix
            a=np.frombuffer(g.samples,dtype=np.uint8).reshape(g.h,g.w)
            box=find_qr(a)
            if box is None: miss.append(i); continue
            rgb=fitz.Pixmap(fitz.csRGB,pix) if pix.n!=3 else pix
            arr=np.frombuffer(rgb.samples,dtype=np.uint8).reshape(rgb.h,rgb.w,3).copy()
            x0,y0,x1,y1=box; arr[y0:y1,x0:x1]=255
            import io
            from PIL import Image
            bio=io.BytesIO(); Image.fromarray(arr).save(bio,'JPEG',quality=88,optimize=True)
            p.replace_image(x[0],stream=bio.getvalue()); nq+=1
    d.set_metadata({'title':dst[:-4],'author':'','subject':'','keywords':'','creator':'','producer':''})
    d.save(DST+'/'+dst,garbage=3,deflate=True)
    msg=f'{dst}: pages={d.page_count} text_spans_removed={nt} qr_removed={nq} qr_miss={miss} {time.time()-t:.0f}s'
    print(msg); log.write(msg+'\n'); log.flush()
