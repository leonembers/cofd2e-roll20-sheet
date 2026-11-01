"""Procedural seamless (wrap-around) splat background textures -> img/tex/<splat>-tex.jpg"""
import numpy as np
from PIL import Image, ImageFilter
N = 640
rng = np.random.default_rng(7)
fy, fx = np.meshgrid(np.fft.fftfreq(N), np.fft.fftfreq(N), indexing='ij')
FR = np.sqrt(fx**2 + fy**2) + 1e-6
def noise(beta=2.0, seed=0, aniso=(1, 1)):
    r = np.random.default_rng(seed)
    f = np.sqrt((fx*aniso[0])**2 + (fy*aniso[1])**2) + 1e-6
    s = np.fft.ifft2(np.fft.fft2(r.standard_normal((N, N))) / f**(beta/2)).real
    return (s - s.min()) / (s.max() - s.min())
Y, X = np.mgrid[0:N, 0:N] / N
def warp(a, b, amt):  # periodic domain warp
    i = (np.mgrid[0:N, 0:N][0] + (b - .5) * amt * N).astype(int) % N
    j = (np.mgrid[0:N, 0:N][1] + (a - .5) * amt * N).astype(int) % N
    return i, j
def cmap(v, stops):
    v = np.clip(v, 0, 1); out = np.zeros(v.shape + (3,))
    xs = [s[0] for s in stops]; cs = np.array([s[1] for s in stops], float)
    for k in range(3): out[..., k] = np.interp(v, xs, cs[:, k])
    return out
def ring(cx, cy, r, w):  # periodic circle outline
    dx = (X - cx + .5) % 1 - .5; dy = (Y - cy + .5) % 1 - .5
    return np.exp(-((np.sqrt(dx*dx + dy*dy) - r) / w)**2)
def line(ang, off, w):  # periodic straight line (integer slopes only keep it seamless)
    a, b = ang
    d = ((a*X + b*Y + off) % 1); d = np.minimum(d, 1 - d) / np.hypot(a, b)
    return np.exp(-(d / w)**2)
T = {}
n1, n2, n3 = noise(2.2, 1), noise(2.0, 2), noise(3.0, 3)
# Vampire: blood-red marbling
s1, s2 = noise(4.0, 61), noise(3.6, 62); m = (1 - np.abs(np.sin(np.pi * (3 * s1 + 2 * s2))))**2.5; m = np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) / 255
T['vampire'] = cmap(.35 * s2 + .15 * n2 + .65 * m, [(0, (8, 2, 3)), (.5, (45, 6, 10)), (.8, (95, 14, 20)), (1, (170, 30, 36))])
# Werewolf: dark misty forest - trunk silhouettes (wrap horizontally), mist bands
tr = np.zeros((N, N)); r = np.random.default_rng(11)
for _ in range(38):
    x0 = r.random(); w = r.uniform(.004, .02); sway = r.uniform(-.02, .02); depth = r.uniform(.3, 1)
    dx = (X - x0 - sway * np.sin(2 * np.pi * Y) + .5) % 1 - .5
    tr = np.maximum(tr, depth * (np.abs(dx) < w * (1 + .3 * np.sin(2*np.pi*(Y*3 + x0)))))
mist = noise(2.6, 5, (1, 3)); fog = .5 + .5 * np.sin(2 * np.pi * (Y * 2 + .15 * mist))
v = .3 + .35 * mist + .35 * fog * n1; v = v * (1 - .97 * tr)
T['werewolf'] = cmap(v, [(0, (2, 6, 4)), (.3, (8, 22, 14)), (.55, (20, 44, 30)), (.8, (46, 70, 54)), (1, (80, 100, 86))])
# Mage: arcane geometry over deep indigo nebula
g = sum(ring(c, d, rr, .003) for c, d, rr in [(.5, .5, .3), (.5, .5, .22), (0, 0, .3), (.5, .5, .12)])
g += sum(line(a, o, .0018) for a, o in [((1, 1), 0), ((1, -1), .5), ((2, 1), .25), ((1, 2), .75)])
T['mage'] = cmap(.6 * n1 + .25 * n3 + .35 * np.clip(g, 0, 1), [(0, (6, 6, 20)), (.5, (24, 22, 62)), (.8, (70, 60, 120)), (1, (190, 160, 90))])
# Changeling: thorny briar greens
i, j = warp(n2, n3, .5); th = np.abs(np.sin(30 * noise(1.6, 9)[i, j] * np.pi))**8
T['changeling'] = cmap(.55 * n1 + .5 * th * n2, [(0, (3, 12, 8)), (.45, (10, 40, 26)), (.75, (30, 80, 50)), (1, (110, 150, 90))])
# Hunter: gritty brushed steel
br = noise(2.0, 21, (8, 1)); gr = rng.random((N, N))
T['hunter'] = cmap(.55 * br + .25 * n1 + .2 * gr, [(0, (10, 14, 16)), (.5, (32, 40, 44)), (.8, (60, 72, 76)), (1, (100, 112, 116))])
# Promethean: alchemical copper verdigris + circles
v = .6 * n1 + .25 * np.clip(ring(.5, .5, .25, .004) + ring(.5, .5, .18, .002) + line((1, 0), .5, .0015) + line((0, 1), .5, .0015), 0, 1) + .15 * n3
T['promethean'] = cmap(v, [(0, (14, 8, 4)), (.45, (60, 30, 14)), (.7, (120, 64, 30)), (.85, (60, 110, 96)), (1, (200, 140, 80))])
# Geist: ghostly teal wisps
i, j = warp(n1, n3, .6); w = noise(2.4, 31)[i, j]**3
T['geist'] = cmap(.4 * n2 + .7 * w, [(0, (4, 10, 12)), (.5, (14, 40, 46)), (.8, (50, 110, 116)), (1, (170, 220, 220))])
# Mummy: sand dunes and gold
du = .5 + .5 * np.sin(2 * np.pi * (Y * 6 + .6 * noise(2.4, 41)))
T['mummy'] = cmap(.25 * du + .5 * n1 + .1 * rng.random((N, N)), [(0, (20, 14, 6)), (.5, (70, 50, 22)), (.8, (90, 66, 30)), (1, (150, 116, 56))])
# Demon: infernal circuitry - grid traces glowing over black
q = 32; cell = rng.random((q, q)); tr = np.zeros((N, N)); s = N // q
for a in range(q):
    for b in range(q):
        if cell[a, b] < .45: tr[a*s + s//2, b*s:(b+1)*s] = 1
        elif cell[a, b] < .8: tr[a*s:(a+1)*s, b*s + s//2] = 1
tr = np.array(Image.fromarray((tr * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))) / 255; tr = tr / tr.max()
T['demon'] = cmap(.35 * n1 + .8 * tr * (.4 + n2), [(0, (6, 4, 8)), (.4, (30, 12, 20)), (.7, (130, 40, 20)), (1, (240, 140, 50))])
# Beast: primal cave - claw rakes over earth
cl = np.clip(sum(line((1, 3), o, .002) for o in (.1, .13, .16, .6, .63, .66)), 0, 1)
T['beast'] = cmap(.65 * n1 + .25 * n3 - .3 * cl, [(0, (6, 3, 8)), (.5, (40, 22, 40)), (.8, (80, 50, 70)), (1, (130, 90, 100))])
# Deviant: clinical - tiles + scan lines, cold red stain
tile = np.maximum(line((8, 0), 0, .0015), line((0, 8), 0, .0015))
T['deviant'] = cmap(.5 * n2 + .25 * tile + .15 * (np.sin(2*np.pi*Y*160) > .9) + .1 * n3, [(0, (10, 12, 14)), (.5, (34, 36, 40)), (.8, (60, 40, 44)), (1, (140, 40, 40))])
# Breeds: animal earth / leaf litter
T['breeds'] = cmap(.5 * n1 + .5 * noise(1.4, 51), [(0, (10, 6, 3)), (.5, (44, 30, 16)), (.8, (80, 60, 30)), (1, (130, 110, 60))])
# Mortal: neutral grey concrete
T['mortal'] = cmap(.6 * n1 + .3 * n3 + .1 * rng.random((N, N)), [(0, (12, 12, 14)), (.5, (34, 34, 38)), (.8, (58, 58, 62)), (1, (90, 90, 96))])
for k, a in T.items():
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f'img/tex/{k}-tex.jpg', quality=80, optimize=True, progressive=True)
    print(k)
