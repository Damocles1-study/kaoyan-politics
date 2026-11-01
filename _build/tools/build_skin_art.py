#!/usr/bin/env python3
"""画展主题的展品：从维基共享资源取公有领域原作的 1280px 缩图，裁掉留白后压成 webp 放进 assets/skin/art/。
用法：python3 _build/tools/build_skin_art.py     原图缓存在 _build/work/skin_raw（不进仓库），已有就不再下载。
展品的中文名、作者、年份和裁切焦点写在 assets/skin.js 的 ART 表里，这里只管文件。"""
import json, os, sys, time, urllib.parse, urllib.request
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW = os.path.join(ROOT, '_build', 'work', 'skin_raw')
OUT = os.path.join(ROOT, 'assets', 'skin', 'art')
UA = {'User-Agent': 'kaoyan-politics-theme/1.0 (personal study site)'}
# id: (Commons 文件名, 裁切框 left top right bottom 比例, 输出宽度, webp 质量)
W = 1100; T = 440
ITEMS = {
  'starry':    ('Van Gogh - Starry Night - Google Art Project.jpg', (0, 0, 1, 1), W, 50),
  'rhone':     ('Starry Night Over the Rhone.jpg', (0, 0, 1, 1), W, 50),
  'cafe':      ('Van Gogh - Terrace of a Café at Night (Place du Forum) 1888.jpg', (0, 0, 1, 1), 760, 50),
  'almond':    ('Vincent van Gogh - Almond blossom - Google Art Project.jpg', (0, 0, 1, 1), W, 50),
  'wheat':     ('Vincent van Gogh - Wheat Field with Cypresses - Google Art Project.jpg', (0, 0, 1, 1), W, 50),
  'sunflower': ('Vincent van Gogh - Sunflowers (1888, National Gallery London).jpg', (0, 0, 1, 1), 760, 50),
  'irises':    ('Irises-Vincent van Gogh.jpg', (.01, .01, .99, .99), W, 50),
  'seasons':   ('Alfons Mucha - The Seasons, 1896.jpg', (.02, .02, .98, .98), W, 50),
  'stones':    ('Alfons Mucha - The Precious Stones (series), 1900.jpg', (.005, .005, .995, .93), W, 50),
  'moonstars': ('Alfons Mucha - The Moon and the Stars.jpg', (.03, .03, .97, .80), W, 50),
  'zodiac':    ('Alphonse Mucha - Zodiac, 1869.jpg', (.02, .012, .98, .988), 820, 50),
  'spring':    ('Alfons Mucha - The Four Seasons - Spring, 1896.jpg', (.05, .025, .95, .975), T, 58),
  'summer':    ('Alfons Mucha - The Four Seasons - Summer, 1896.jpg', (.05, .025, .95, .975), T, 58),
  'autumn':    ('Alfons Mucha - The Four Seasons - Autumn, 1896.jpg', (.05, .025, .95, .975), T, 58),
  'winter':    ('Alfons Mucha - The Four Seasons - Winter, 1896.jpg', (.05, .025, .95, .975), T, 58),
  'ruby':      ('Alfons Mucha - The Precious Stones-Ruby, 1900.jpg', (.03, .012, .97, .95), T, 58),
  'emerald':   ('Alfons Mucha - The Precious Stones-Emerald, 1900.jpg', (.03, .012, .97, .95), T, 58),
}
def fetch(k, title):
    p = os.path.join(RAW, k + '.jpg')
    if os.path.exists(p): return p
    q = urllib.parse.urlencode(dict(action='query', titles='File:' + title, prop='imageinfo', iiprop='url', iiurlwidth=1280, format='json'))
    r = json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA), timeout=30))
    i = list(r['query']['pages'].values())[0]['imageinfo'][0]
    for a in range(5):
        try:
            d = urllib.request.urlopen(urllib.request.Request(i.get('thumburl') or i['url'], headers=UA), timeout=90).read()
            open(p, 'wb').write(d); time.sleep(1.5); return p
        except Exception as e:
            print('  重试', k, e); time.sleep(8 * (a + 1))
    sys.exit('下载失败：' + k)
os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
total = 0; credits = ['# 展品来源', '', '全部为公有领域作品（梵高 1853–1890，慕夏 1860–1939），图像取自维基共享资源，裁去留白并压缩。', '']
for k, (title, box, w, q) in ITEMS.items():
    im = Image.open(fetch(k, title)).convert('RGB')
    a, b = im.size
    im = im.crop((int(box[0]*a), int(box[1]*b), int(box[2]*a), int(box[3]*b)))
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, k + '.webp'); im.save(p, 'WEBP', quality=q, method=6)
    n = os.path.getsize(p); total += n; print(f'{k:10s} {im.width}x{im.height} {n//1024} KB')
    credits.append(f'- `{k}.webp`：https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(title.replace(' ', '_')))
# 梵高厅的墙面底纹：星月夜的极淡缩影
im = Image.open(os.path.join(RAW, 'starry.jpg')).convert('RGB').resize((640, 506), Image.LANCZOS)
im.save(os.path.join(OUT, 'wall-vg.webp'), 'WEBP', quality=45, method=6)
total += os.path.getsize(os.path.join(OUT, 'wall-vg.webp'))
open(os.path.join(OUT, 'CREDITS.md'), 'w', encoding='utf8').write('\n'.join(credits) + '\n')
print('合计', total // 1024, 'KB')
