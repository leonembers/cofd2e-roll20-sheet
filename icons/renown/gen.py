from PIL import Image, ImageDraw
import math
S=4; N=48*S
C={'cunning':(214,140,60),'glory':(232,182,72),'honor':(190,170,140),'purity':(150,190,200),'wisdom':(170,140,200)}
def base():
    im=Image.new('RGBA',(N,N),(0,0,0,0)); d=ImageDraw.Draw(im); return im,d
def ring(d,c): d.ellipse([3*S,3*S,N-3*S,N-3*S],outline=c+(255,),width=3*S)
def P(x,y): return (x*S,y*S)
def draw(name):
    im,d=base(); c=C[name]; col=c+(255,); w=4*S
    ring(d,c)
    if name=='cunning':  # crooked fox-like zigzag
        d.line([P(13,32),P(20,16),P(24,28),P(28,16),P(35,32)],fill=col,width=w,joint='curve')
    elif name=='glory':  # sunburst spear
        d.line([P(24,10),P(24,38)],fill=col,width=w); d.polygon([P(24,8),P(30,18),P(18,18)],fill=col)
        d.line([P(15,26),P(33,26)],fill=col,width=w-S)
    elif name=='honor':  # balance / pillar
        d.line([P(24,12),P(24,36)],fill=col,width=w); d.line([P(14,18),P(34,18)],fill=col,width=w)
        d.line([P(16,36),P(32,36)],fill=col,width=w)
    elif name=='purity':  # crescent + drop
        d.ellipse([P(13,12),P(35,34)],fill=col); d.ellipse([P(19,10),P(39,32)],fill=(0,0,0,0))
    elif name=='wisdom':  # eye
        d.arc([P(10,14),P(38,42)],200,340,fill=col,width=w); d.arc([P(10,6),P(38,34)],20,160,fill=col,width=w)
        d.ellipse([P(20,20),P(28,28)],fill=col)
    im=im.resize((48,48),Image.LANCZOS); im.save(f'{name}.png')
for n in C: draw(n)
# preview on dark bg
pv=Image.new('RGBA',(5*60,60),(30,22,18,255))
for i,n in enumerate(C): pv.alpha_composite(Image.open(f'{n}.png'),(i*60+6,6))
pv.save('/workspace/cofd/roll20/shots/r6-renown-icons-raw.png')
