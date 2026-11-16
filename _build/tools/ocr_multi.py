# 同一本书多跑几遍不同分辨率的 Vision 识别，供 ocr_vote.py 逐字投票
# 用法：python3 ocr_multi.py 书名.pdf 模式   模式 = d250（按 250dpi 渲染）| raw（直接取扫描原图）
import fitz, subprocess, os, sys
S='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
SRC='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/'
name, mode = sys.argv[1], sys.argv[2]
tag=name[:-4]
img=f'{S}/ocrimg/{tag}_{mode}'; os.makedirs(img,exist_ok=True)
out=f'{S}/ocr/{tag}__{mode}.txt'
d=fitz.open(SRC+name)
done=set()
if os.path.exists(out):
    for l in open(out):
        if l.startswith('##FILE'): done.add(int(l.strip().split('_')[-1][:-4]))
pages=[i for i in range(d.page_count) if i not in done]
B=12
for k in range(0,len(pages),B):
    batch=pages[k:k+B]; files=[]
    for i in batch:
        f=f'{img}/p_{i:04d}.png'
        if mode=='raw':
            x=d[i].get_images(full=True)[0]; pix=fitz.Pixmap(d,x[0])
            if pix.alpha or pix.n>3: pix=fitz.Pixmap(fitz.csRGB,pix)
            pix.save(f)
        else: d[i].get_pixmap(dpi=int(mode[1:])).save(f)
        files.append(f)
    r=subprocess.run(['osascript','-l','JavaScript',f'{S}/tools/ocr.js']+files,capture_output=True,text=True)
    with open(out,'a') as o: o.write(r.stdout.strip()+'\n')
    for f in files: os.remove(f)
    print(tag, mode, batch[-1], flush=True)
