import fitz, subprocess, os, sys
S='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
SRC='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/'
name, dpi = sys.argv[1], int(sys.argv[2])
tag=name[:-4]
img=f'{S}/ocrimg/{tag}'; os.makedirs(img,exist_ok=True)
out=f'{S}/ocr/{tag}.txt'; os.makedirs(f'{S}/ocr',exist_ok=True)
d=fitz.open(SRC+name)
done=set()
if os.path.exists(out):
    for l in open(out):
        if l.startswith('##FILE'): done.add(int(l.strip().split('_')[-1][:-4]))
B=12
pages=[i for i in range(d.page_count) if i not in done]
for k in range(0,len(pages),B):
    batch=pages[k:k+B]; files=[]
    for i in batch:
        f=f'{img}/p_{i:04d}.png'; d[i].get_pixmap(dpi=dpi).save(f); files.append(f)
    r=subprocess.run(['osascript','-l','JavaScript',f'{S}/tools/ocr.js']+files,capture_output=True,text=True)
    with open(out,'a') as o: o.write(r.stdout.strip()+'\n')
    for f in files: os.remove(f)
    print(tag, batch[-1], flush=True)
