"""Procedural Werewolf: the Forsaken frame (palette sampled from the 2E core cover; no cover pixels used).
Writes wtf-{top,mid,bot}.jpg (light) and wtf-{top,mid,bot}-dark.jpg, 1000px wide, mid tiles vertically."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]; SPL = sys.argv[2] if len(sys.argv) > 2 else "wtf"
W, HT, HM, HB = 1000, 260, 130, 260
H = HT + HM + HB
rng = np.random.default_rng(7)
H2 = lambda *h: np.array([tuple(int(x[i:i+2], 16) for i in (1, 3, 5)) for x in h], float)
# palettes: k-means of each 2E core cover (no cover pixels are used, only these colours)
CFG = {
 'wtf':    dict(pal=H2('#25140d','#412113','#583019','#764422','#a0612f','#c88645'), rim=(214,150,74), tear=9, shade=(90,45,20), paper=(238,228,210), dpaper=(20,15,12)),
 'mortal': dict(pal=H2('#090b12','#1a2336','#293653','#3b4d74','#576d99','#8697b9'), rim=(202,210,226), tear=4, shade=(30,40,70), paper=(232,234,240), dpaper=(12,14,20)),
 'hunter': dict(pal=H2('#081311','#152c28','#27403c','#3d5753','#57726d','#79928d'), rim=(176,189,187), tear=6, shade=(20,45,40), paper=(230,234,230), dpaper=(10,16,15)),
 'mage':   dict(pal=H2('#224744','#327a7e','#5c7e68','#53b1af','#78a584','#9adad0'), rim=(222,196,120), tear=5, shade=(30,80,80), paper=(234,240,236), dpaper=(10,20,20)),
 'demon':  dict(pal=H2('#1f1f24','#2a2c36','#3b3e4a','#50525f','#686b77','#a3a5ac'), rim=(190,192,200), tear=2, shade=(40,42,55), paper=(234,234,236), dpaper=(15,15,18)),
 'beast':  dict(pal=H2('#241a23','#3b2b3a','#523c51','#6e516c','#8b6d89','#ae93ac'), rim=(207,188,205), tear=8, shade=(60,35,58), paper=(238,232,236), dpaper=(18,13,17)),
}[SPL]
PAL = CFG['pal']
def fbm(h, w, oct=6, per_y=None):
    acc = np.zeros((h, w)); amp = 1; tot = 0
    for o in range(oct):
        f = np.fft.fft2(rng.standard_normal((h, w)))
        ky = np.fft.fftfreq(h)[:, None]; kx = np.fft.fftfreq(w)[None, :]
        k = np.sqrt(kx**2 + ky**2) + 1e-6
        band = np.exp(-((np.log2(k) + 1.5 + o) ** 2) / 0.6)
        acc += amp * np.real(np.fft.ifft2(f * band)); tot += amp; amp *= .6
    acc /= tot; return (acc - acc.mean()) / acc.std()
def ramp(t):
    t = np.clip(t, 0, 1) * (len(PAL) - 1); i = np.floor(t).astype(int).clip(0, len(PAL) - 2); f = (t - i)[..., None]
    return PAL[i] * (1 - f) + PAL[i + 1] * f
# periodic noise: build the full strip so mid section is vertically periodic (periodic FFT on HM-tall tile, tops/bottoms separate)
from scipy.ndimage import gaussian_filter
_cache = {}
def sn(h, s, wrap=False, key=None):
    # every field is periodic with period HM in y and tiled to h, so the side borders and paper are continuous across top/mid/bot
    k = (s, key)
    if k not in _cache:
        g = gaussian_filter(rng.standard_normal((HM, W)), s, mode='wrap'); _cache[k] = (g - g.mean()) / (g.std() + 1e-9)
    return np.tile(_cache[k], (h // HM + 1, 1))[:h]
def strip(h): return sn(h, 2)
BW = 42  # border width px at 1000
def section(h, kind):
    wr = kind == 'mid'
    n = sn(h, 14, key='n'); fine = sn(h, 1.2, key='f') * .6
    y, x = np.mgrid[0:h, 0:W]
    yy = y if kind != 'bot' else (h - 1 - y)
    # distance into the frame (0 at outer edge); torn inner edge from noise
    d = np.minimum(x, W - 1 - x).astype(float)
    if kind in ('top', 'bot'): d = np.minimum(d, yy * 1.0)
    edge = BW + CFG['tear'] * sn(h, 22, key='e') + 2.5 * sn(h, 3, key='e2')
    inside = d > edge
    t = .35 + .22 * n + .12 * fine - .25 * np.clip(d / BW, 0, 1) ** 2
    rgb = ramp(t)
    # vertical bark/grain streaks on the sides
    grain = (np.abs(np.sin(x * .9 + 3 * n)) ** 8 if SPL in ('wtf', 'beast') else MOT_TEX(x, y, n)) * (d < edge)
    rgb *= (1 - .25 * grain[..., None])
    # amber rim highlight on the torn inner edge
    rim = np.exp(-((d - edge) ** 2) / 4.0) * (d < edge + 6)
    rgb = rgb * (1 - .6 * rim[..., None]) + np.array(CFG['rim']) * .6 * rim[..., None]
    return rgb, inside, edge
def claws(img, cx, cy, ang, scale, col):
    d = ImageDraw.Draw(img)
    for k in range(3):
        pts = []
        for s in np.linspace(0, 1, 24):
            px = cx + (k - 1) * 16 * scale + s * 120 * scale * np.cos(ang) + 10 * np.sin(s * 3.1) * scale
            py = cy + s * 120 * scale * np.sin(ang)
            pts.append((px, py))
        for i in range(len(pts) - 1):
            w = int(1 + 7 * scale * np.sin(np.pi * i / (len(pts) - 1)))
            d.line([(pts[i][0] + 2, pts[i][1] + 1), (pts[i + 1][0] + 2, pts[i + 1][1] + 1)], fill=(220, 150, 70), width=max(1, w - 2))
            d.line([pts[i], pts[i + 1]], fill=col, width=w)
def moon(img, cx, cy, r, col, bg):
    d = ImageDraw.Draw(img); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col); d.ellipse([cx - r + r * .45, cy - r - r * .1, cx + r + r * .45, cy + r - r * .1], fill=bg)

def MOT_TEX(x, y, n):
    if SPL == 'mortal':  # wet cobblestones: rounded cell seams
        return (np.abs(np.sin(x * .32 + 2 * n) * np.sin(y * 2 * np.pi / 13 + (x // 10) * 1.7)) < .18) * 1.0
    if SPL == 'hunter':  # grimy diagonal scratches
        return (np.abs(np.sin((x + y) * .6 + 4 * n)) ** 12)
    if SPL == 'mage':    # water caustics
        return np.clip(1 - np.abs(np.sin(x * .21 + 3 * n) + np.sin(y * 2 * np.pi / 26 + 2.5 * n)), 0, 1) ** 3 * -1.6
    if SPL == 'demon':   # cracked-glass / wire lines
        return (np.abs(np.sin(x * .15 + y * 2 * np.pi / 65 + 5 * n)) < .05) * 1.0
    return 0
def _glow(im, cx, cy, r, col, a):
    g = Image.new('L', im.size, 0); ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(255 * a))
    g = g.filter(ImageFilter.GaussianBlur(r / 2)); im.paste(Image.new('RGB', im.size, col), (0, 0), g)
def MOTIF(im, kind, h):
    d = ImageDraw.Draw(im); r = tuple(CFG['rim']); dk = tuple(int(v) for v in PAL[0])
    if SPL == 'mortal':   # street-lamp glow + God-Machine polygon eye at top; lamp posts in corners
        if kind == 'top':
            _glow(im, W // 2, 22, 26, (230, 236, 255), .55)
            pts = [(W // 2 + 15 * np.cos(a), 22 + 15 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 7)[:-1] + np.pi / 6]
            d.polygon(pts, outline=r); d.ellipse([W // 2 - 5, 17, W // 2 + 5, 27], outline=r, width=2)
            for cx in (20, W - 20): d.line([(cx, 0), (cx, 60)], fill=dk, width=4); _glow(im, cx, 62, 10, (240, 230, 190), .7)
        if kind == 'bot':
            for cx in (20, W - 20): d.line([(cx, h - 70), (cx, h)], fill=dk, width=4)
    if SPL == 'hunter':   # tally marks in corners + crosshair at top
        for (cx, cy, s) in ((10, 10, 1), (W - 60, 10, 1)) if kind == 'top' else ((10, h - 40, 1), (W - 60, h - 40, 1)) if kind == 'bot' else ():
            for k in range(4): d.line([(cx + k * 9, cy), (cx + k * 9 - 3, cy + 28)], fill=r, width=3)
            d.line([(cx - 6, cy + 22), (cx + 36, cy + 4)], fill=r, width=3)
        if kind == 'top':
            c = (W // 2, 22); d.ellipse([c[0] - 14, 8, c[0] + 14, 36], outline=r, width=2)
            for a, b in (((c[0] - 22, 22), (c[0] - 6, 22)), ((c[0] + 6, 22), (c[0] + 22, 22)), ((c[0], 0), (c[0], 16)), ((c[0], 28), (c[0], 44))): d.line([a, b], fill=r, width=2)
    if SPL == 'mage':     # golden arcane circle at top, spiral sigils in corners
        if kind == 'top':
            cx = W // 2; d.ellipse([cx - 17, 5, cx + 17, 39], outline=r, width=2); d.ellipse([cx - 11, 11, cx + 11, 33], outline=r, width=1)
            pts = [(cx + 17 * np.cos(a), 22 + 17 * np.sin(a)) for a in np.linspace(-np.pi / 2, 1.5 * np.pi, 6)[:-1]]
            d.line([pts[i] for i in (0, 2, 4, 1, 3, 0)], fill=r, width=1)
        for cy in ((26,) if kind == 'top' else (h - 26,) if kind == 'bot' else ()):
            for cx in (22, W - 22):
                sp = [(cx + t * 1.3 * np.cos(t * .5), cy + t * 1.3 * np.sin(t * .5)) for t in np.linspace(0, 16, 60)]
                d.line(sp, fill=r, width=2)
    if SPL == 'demon':    # angular stained-glass eye at top, wire web from the corners
        for (cx, cy, sg) in ((0, 0, 1), (W, 0, -1)) if kind == 'top' else ((0, h, 1), (W, h, -1)) if kind == 'bot' else ():
            for a in np.linspace(.15, 1.4, 6):
                d.line([(cx, cy), (cx + sg * 120 * np.cos(a), cy + (1 if cy == 0 else -1) * 120 * np.sin(a))], fill=r, width=1)
            for rr in (40, 75, 110): d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 0, 360, fill=r, width=1)
        if kind == 'top':
            cx = W // 2; d.polygon([(cx - 24, 22), (cx, 8), (cx + 24, 22), (cx, 36)], outline=r); d.polygon([(cx - 7, 22), (cx, 14), (cx + 7, 22), (cx, 30)], fill=r)
    if SPL == 'beast':    # fangs along the top and bottom edges (the cover's maw), horns at top
        if kind in ('top', 'bot'):
            for i, cx in enumerate(range(30, W - 20, 64)):
                L = 22 + 8 * ((i * 7) % 3)
                tri = [(cx - 9, 0), (cx + 9, 0), (cx, L)] if kind == 'top' else [(cx - 9, h - 1), (cx + 9, h - 1), (cx, h - 1 - L)]
                d.polygon(tri, fill=(226, 214, 222)); d.line(tri[1:], fill=dk, width=2)
for mode in ('light', 'dark'):
    paper = np.array(CFG['paper']) if mode == 'light' else np.array(CFG['dpaper'])
    parts = {}
    for kind, h in (('top', HT), ('mid', HM), ('bot', HB)):
        rgb, inside, edge = section(h, kind)
        pn = sn(h, 6, key='p') * (6 if mode == 'light' else 3)
        pap = paper[None, None, :] + pn[..., None]
        # inner shadow cast by the frame
        y, x = np.mgrid[0:h, 0:W]; d = np.minimum(x, W - 1 - x).astype(float)
        if kind == 'top': d = np.minimum(d, y)
        if kind == 'bot': d = np.minimum(d, h - 1 - y)
        sh = np.exp(-np.clip(d - edge, 0, None) / 18)[..., None]
        pap = pap * (1 - (.28 if mode == 'light' else .0) * sh) + np.array(CFG['shade']) * (.28 if mode == 'light' else .18) * sh
        img = np.where(inside[..., None], pap, rgb)
        if mode == 'dark':  # keep the frame rich but a touch deeper
            img = np.where(inside[..., None], img, img * .85)
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        if SPL != 'wtf': MOTIF(im, kind, h)
        elif kind == 'top':
            claws(im, 14, 4, 1.05, 1.3, (24, 12, 8)); claws(im, W - 14, 4, 2.09, 1.3, (24, 12, 8))
            moon(im, W // 2, 22, 13, (226, 200, 150), tuple(int(v) for v in ramp(np.array(.42))))
        if SPL == 'wtf' and kind == 'bot':
            claws(im, 14, 256, -1.05, 1.3, (24, 12, 8)); claws(im, W - 14, 256, -2.09, 1.3, (24, 12, 8))
        parts[kind] = im
    sfx = '' if mode == 'light' else '-dark'
    for kind, im in parts.items(): im.save(f'{out}/{SPL}-{kind}{sfx}.jpg', quality=88)
print('ok')
