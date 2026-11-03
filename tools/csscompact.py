import re,subprocess,sys,os,tempfile
def compact(c,html=None):
    import tinycss2
    c=re.sub(r'(border(?:-left|-right|-top|-bottom)?)\s*:\s*none\b',r'\1: medium none',c)
    c=re.sub(r'/\*.*?\*/','',c,flags=re.S)
    head=[];rt=[];rest=[]
    for r in tinycss2.parse_stylesheet(c,skip_whitespace=True,skip_comments=True):
        t=r.serialize().strip()
        if r.type=='at-rule' and r.lower_at_keyword in ('import','font-face','charset'): head.append(re.sub(r'\s+',' ',t))
        elif r.type=='qualified-rule' and 'rolltemplate-' in tinycss2.serialize(r.prelude): rt.append(re.sub(r'\s*\n\s*',' ',t))
        else: rest.append(t)
    return '\n'.join(head+['/* roll templates (kept first and uncompressed: Roll20 legacy sanitizer) */']+rt+['/* sheet */'])+'\n'+_prune(_sheet('\n'.join(rest)),html)
def _sheet(c):
    d=tempfile.mkdtemp(); a=os.path.join(d,'i.css'); b=os.path.join(d,'o.css')
    open(a,'w').write(c)
    subprocess.run(['npx','--yes','csso-cli',a,'-o',b],check=True)
    m=open(b).read()
    m=re.sub(r'\btransparent\b','rgba(0,0,0,0)',m)
    m=re.sub(r'\)(?=[a-z#])',') ',m); m=re.sub(r'%(?=[a-z])','% ',m)
    m=re.sub(r'\.charsheet((?:\.charsheet)+)',lambda x:'.charsheet'+'[class]'*(len(x.group(1))//10),m)
    out=[];depth=0;buf='';q=None
    for ch in m:
        buf+=ch
        if q:
            if ch==q:q=None
            continue
        if ch in '"\'':q=ch
        elif ch=='{':depth+=1
        elif ch=='}':
            depth-=1
            if depth==0: out.append(buf.strip());buf=''
        elif ch==';' and depth==0: out.append(buf.strip());buf=''
    if buf.strip(): out.append(buf.strip())
    res=[]
    for r in out:
        if not r.startswith('@') and '{' in r:
            sel,body=r.split('{',1)
            parts=re.split(r',(?![^()]*\))',sel)
            if len(parts)>16:
                for k in range(0,len(parts),12): res.append(','.join(parts[k:k+12])+'{'+body)
                continue
        res.append(r)
    return '\n'.join(res)+'\n'
def _prune(css,html):
    # drop selectors that name a sheet-* class that never appears in the HTML/worker (never matches); :not/:is/:where/:has args are
    # only consulted for :has (a dead class there can never match), the others are left alone
    if not html or os.environ.get('CSS_NOPRUNE'): return css
    cls=set(re.findall(r'sheet-[\w-]+',html))
    def strip(p):
        while True:
            m=re.search(r':(?:not|is|where)\((?:[^()]|\([^()]*\))*\)',p)
            if not m: return p
            p=p[:m.start()]+p[m.end():]
    def live(p): return all(x in cls or 'darkmode' in x for x in re.findall(r'\.(sheet-[\w-]+)',strip(p)))
    out=[]
    for line in css.split('\n'):
        if line.startswith('@') or '{' not in line: out.append(line); continue
        sel,body=line.split('{',1)
        ps=re.split(r',(?![^()]*\))',sel); k=[p for p in ps if live(p)]
        if k: out.append(','.join(k)+'{'+body)
    return '\n'.join(out)
if __name__=='__main__':
    open(sys.argv[2],'w').write(compact(open(sys.argv[1]).read()))
