"""Procedural Werewolf: the Forsaken frame (palette sampled from the 2E core cover; no cover pixels used).
Writes wtf-{top,mid,bot}.jpg (light) and wtf-{top,mid,bot}-dark.jpg, 1000px wide, mid tiles vertically."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]
W, HT, HM, HB = 1000, 260, 130, 260
H = HT + HM + HB
rng = np.random.default_rng(7)
PAL = np.array([(0x25,0x14,0x0d),(0x41,0x21,0x13),(0x58,0x30,0x19),(0x76,0x44,0x22),(0xa0,0x61,0x2f),(0xc8,0x86,0x45)],float)
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
    edge = BW + 9 * sn(h, 22, key='e') + 2.5 * sn(h, 3, key='e2')
    inside = d > edge
    t = .35 + .22 * n + .12 * fine - .25 * np.clip(d / BW, 0, 1) ** 2
    rgb = ramp(t)
    # vertical bark/grain streaks on the sides
    grain = np.abs(np.sin(x * .9 + 3 * n)) ** 8 * (d < edge)
    rgb *= (1 - .25 * grain[..., None])
    # amber rim highlight on the torn inner edge
    rim = np.exp(-((d - edge) ** 2) / 4.0) * (d < edge + 6)
    rgb = rgb * (1 - .6 * rim[..., None]) + np.array([214, 150, 74]) * .6 * rim[..., None]
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
for mode in ('light', 'dark'):
    paper = np.array([238, 228, 210]) if mode == 'light' else np.array([20, 15, 12])
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
        pap = pap * (1 - (.28 if mode == 'light' else .0) * sh) + np.array([90, 45, 20]) * (.28 if mode == 'light' else .18) * sh
        img = np.where(inside[..., None], pap, rgb)
        if mode == 'dark':  # keep the frame rich but a touch deeper
            img = np.where(inside[..., None], img, img * .85)
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        if kind == 'top':
            claws(im, 14, 4, 1.05, 1.3, (24, 12, 8)); claws(im, W - 14, 4, 2.09, 1.3, (24, 12, 8))
            moon(im, W // 2, 22, 13, (226, 200, 150), tuple(int(v) for v in ramp(np.array(.42))))
        if kind == 'bot':
            claws(im, 14, 256, -1.05, 1.3, (24, 12, 8)); claws(im, W - 14, 256, -2.09, 1.3, (24, 12, 8))
        parts[kind] = im
    sfx = '' if mode == 'light' else '-dark'
    for kind, im in parts.items(): im.save(f'{out}/wtf-{kind}{sfx}.jpg', quality=88)
print('ok')
