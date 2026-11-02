"""Draw the d10 roller icon (kite face + pentagonal lower facets + number) into assets/."""
from PIL import Image, ImageDraw, ImageFont
S=4; W=128*S
def P(x,y): return (x*S*1.28, y*S*1.28)
def make(fill, face, edge, txt, name):
    im=Image.new('RGBA',(W,W),(0,0,0,0)); d=ImageDraw.Draw(im)
    top=P(50,3); ul=P(8,40); ur=P(92,40); ll=P(8,62); lr=P(92,62); bot=P(50,97)
    kl=P(27,56); kr=P(73,56); kb=P(50,70)
    d.polygon([top,ur,lr,bot,ll,ul],fill=fill,outline=edge,width=3*S)
    d.polygon([ul,kl,kb,P(50,70),bot,ll],fill=tuple(max(0,c-40) for c in fill[:3])+(255,))
    d.polygon([ur,kr,kb,bot,lr],fill=tuple(max(0,c-60) for c in fill[:3])+(255,))
    d.polygon([top,kr,kb,kl],fill=face,outline=edge,width=3*S)
    for a,b in [(ul,kl),(ur,kr),(kb,bot),(ll,kl),(lr,kr)]: d.line([a,b],fill=edge,width=3*S)
    d.polygon([top,ur,lr,bot,ll,ul],outline=edge,width=4*S)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(22*S*1.28))
    bx=d.textbbox((0,0),'10',font=f); tw=bx[2]-bx[0]; th=bx[3]-bx[1]
    cx,cy=P(50,44); d.text((cx-tw/2-bx[0],cy-th/2-bx[1]),'10',font=f,fill=txt)
    im.resize((128,128),Image.LANCZOS).save(f'assets/{name}.png')
make((150,150,158,255),(232,232,238,255),(20,20,24,255),(15,15,18,255),'d10')
make((185,185,195,255),(255,255,255,255),(20,20,24,255),(140,0,0,255),'d10-hover')
make((110,110,118,255),(190,190,198,255),(10,10,12,255),(15,15,18,255),'d10-pressed')
