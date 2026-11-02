import sys
exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    for t in sys.argv[1].split(','):
      for w in (700,1000,1300):
        go(pg,t,page='1',w=w)
        r=pg.evaluate("""()=>{const bs=[...document.querySelectorAll('.sheet-skills button.sheet-toggle')].filter(b=>b.getClientRects().length);
          const bad=bs.filter(b=>b.scrollWidth>b.clientWidth+0.5).map(b=>b.innerText.trim());
          const b=bs.find(x=>/Animal/.test(x.innerText))||bs[0]; const row=b.parentElement, dots=row.nextElementSibling, col=row.parentElement;
          return {bad, name:Math.round(b.getBoundingClientRect().width), row:Math.round(row.getBoundingClientRect().width), dots:Math.round(dots.getBoundingClientRect().width), col:Math.round(col.getBoundingClientRect().width), colDisp:getComputedStyle(col).gridTemplateColumns||getComputedStyle(col).display, fs:getComputedStyle(b).fontSize, ov:getComputedStyle(b).textOverflow}}""")
        print(t,w,r)
''')
