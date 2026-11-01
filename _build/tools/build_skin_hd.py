#!/usr/bin/env python3
"""Gallery hall backdrops: fetch the 1920px Commons renditions of the main works and write assets/skin/art/hd/*.webp.
These are the textures the WebGL scene samples, so brush detail matters more than file size.
Raw downloads are cached in _build/work/skin_hd (not in the repo)."""
import json, os, sys, time, urllib.parse, urllib.request
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW = os.path.join(ROOT, '_build', 'work', 'skin_hd')
OUT = os.path.join(ROOT, 'assets', 'skin', 'art', 'hd')
UA = {'User-Agent': 'kaoyan-politics-theme/1.0 (personal study site)'}
ITEMS = {
  'starry':    ('Van Gogh - Starry Night - Google Art Project.jpg', (0, 0, 1, 1)),
  'rhone':     ('Starry Night Over the Rhone.jpg', (0, 0, 1, 1)),
  'almond':    ('Vincent van Gogh - Almond blossom - Google Art Project.jpg', (0, 0, 1, 1)),
  'wheat':     ('Vincent van Gogh - Wheat Field with Cypresses - Google Art Project.jpg', (0, 0, 1, 1)),
  'irises':    ('Irises-Vincent van Gogh.jpg', (.01, .01, .99, .99)),
  'seasons':   ('Alfons Mucha - The Seasons, 1896.jpg', (.02, .02, .98, .98)),
  'stones':    ('Alfons Mucha - The Precious Stones (series), 1900.jpg', (.005, .005, .995, .93)),
  'moonstars': ('Alfons Mucha - The Moon and the Stars.jpg', (.03, .03, .97, .80)),
}
def fetch(k, title):
    p = os.path.join(RAW, k + '.jpg')
    if os.path.exists(p): return p
    q = urllib.parse.urlencode(dict(action='query', titles='File:' + title, prop='imageinfo', iiprop='url', iiurlwidth=1920, format='json'))
    r = json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA), timeout=30))
    i = list(r['query']['pages'].values())[0]['imageinfo'][0]
    for a in range(5):
        try:
            d = urllib.request.urlopen(urllib.request.Request(i.get('thumburl') or i['url'], headers=UA), timeout=120).read()
            open(p, 'wb').write(d); time.sleep(2); return p
        except Exception as e:
            print('  retry', k, e); time.sleep(8 * (a + 1))
    sys.exit('download failed: ' + k)
os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
total = 0
for k, (title, box) in ITEMS.items():
    im = Image.open(fetch(k, title)).convert('RGB')
    a, b = im.size
    im = im.crop((int(box[0]*a), int(box[1]*b), int(box[2]*a), int(box[3]*b)))
    if im.width > 1920: im = im.resize((1920, round(im.height * 1920 / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, k + '.webp'); im.save(p, 'WEBP', quality=72, method=6)
    n = os.path.getsize(p); total += n; print(k, im.size, n // 1024, 'KB')
print('total', total // 1024, 'KB')
