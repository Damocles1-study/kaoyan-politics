# 校对看图：python3 crop_page.py 书 页索引 上沿比例 下沿比例 输出png
import fitz, sys
from PIL import Image
book, pg, a, b, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
d = fitz.open('/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/' + book + '.pdf')
x = d[pg].get_images(full=True)[0]; pix = fitz.Pixmap(d, x[0])
if pix.n > 3: pix = fitz.Pixmap(fitz.csRGB, pix)
pix.save(out); im = Image.open(out).convert('L')
W, H = im.size; im = im.crop((0, int(H * a), W, int(H * b)))
im = im.resize((W * 55 // 100, im.height * 55 // 100), Image.LANCZOS); im.save(out)
