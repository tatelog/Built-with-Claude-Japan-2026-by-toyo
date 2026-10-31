# 冒頭の試作 v2：速いモンタージュ → 手の時代のコピー → デジタイザでなぞる → 数値（DXF）の壁
import numpy as np, math, wave, sys, io
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import ezdxf
S=sys.argv[1]; OUT=S+"/op4"
W,H,FPS=1920,1080,24
AH=round(W/2.39); TOP=(H-AH)//2
F=S+"/fonts/"
mono=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",72)
monoS=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",22)
monoXS=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",17)
jp=ImageFont.truetype(F+"Noto_Sans_JP_wght_300.ttf",44)
jpL=ImageFont.truetype(F+"Noto_Sans_JP_wght_300.ttf",46)
en=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",24)
rng=np.random.default_rng(7)
def load(p,mode):
  im=Image.open(p).convert("RGB")
  if mode=="mono":
    g=ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=1); im=ImageOps.colorize(g,(14,14,16),(236,232,224))
  elif mode=="color": im=ImageEnhance.Color(im).enhance(0.9)
  else: im=ImageEnhance.Color(im).enhance(0.85)
  return im
IM={k:load(p,m) for k,(p,m) in {
 "tools":(S+"/intl/met_198857.jpg","mono"),"p18":(S+"/ndl/teikoku_p18.jpg","blue"),"p20":(S+"/ndl/teikoku_p20.jpg","blue"),
 "p23":(S+"/ndl/teikoku_p23.jpg","blue"),"p5":(S+"/ndl/teikoku_p5.jpg","blue"),"room":(S+"/ndl/kyudai_seizushitsu.jpg","mono"),
 "garnier":(S+"/intl/met_269271.jpg","mono"),"crystal":(S+"/intl/met_269619.jpg","mono"),"sagrada":(S+"/intl/sf_gili1905.jpg","mono"),
 "plan":(S+"/ndl/kyudai_p6.jpg","mono"),
 "scott":(S+"/cma/cma_153714.jpg","mono"),"notre":(S+"/cma/cma_156101.jpg","mono"),"taj":(S+"/cma/cma_668288.jpg","mono"),"arc":(S+"/cma/cma_452645.jpg","mono"),
 "d25":(S+"/dt/dt_p25.jpg","color"),"d26":(S+"/dt/dt_p26.jpg","color"),"d55":(S+"/dt/dt_p55.jpg","mono"),"d61":(S+"/dt/dt_p61.jpg","mono"),
 "d23":(S+"/dt/dt_p23.jpg","color"),"d28":(S+"/dt/dt_p28.jpg","color"),"d7":(S+"/dt/dt_p7.jpg","color"),"d27":(S+"/dt/dt_p27.jpg","color")}.items()}
A=2.39
ease=lambda t:0.5-0.5*math.cos(math.pi*max(0,min(1,t)))
def box(c,im):
  iw,ih=im.size; pw=c[2]*iw; ph=pw/A; return (c[0]*iw-pw/2,c[1]*ih-ph/2,c[0]*iw+pw/2,c[1]*ih+ph/2)
def grain(img,amt=6):
  a=np.asarray(img).astype(np.int16); n=rng.normal(0,amt,(a.shape[0],a.shape[1],1)).astype(np.int16)
  return Image.fromarray(np.clip(a+n,0,255).astype(np.uint8))
def letterbox(pic):
  fr=Image.new("RGB",(W,H),(0,0,0)); fr.paste(pic,(0,TOP)); return fr
def text_c(d,y,s,font,fill):
  w=d.textlength(s,font=font); d.text(((W-w)/2,y),s,font=font,fill=fill)
def gray(v,a): return tuple(int(v*a) for _ in range(3))
# ---- 1) .dwg -> Drawing ----
TYPE=[]   # (time, action, char)
_t=0.6
for ch in ".dwg": TYPE.append((_t,"key",ch)); _t+=0.16
_t+=0.45
for _ in range(4): TYPE.append((_t,"bs","")); _t+=0.08
_t+=0.25
for ch in "Drawing": TYPE.append((_t,"key",ch)); _t+=0.15
TYPE_JP=_t+0.25
for ch in "図面": TYPE.append((_t+0.25,"jp",ch)); _t+=0.2
def title(t):
  fr=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(fr)
  buf=""; jpb=""
  for tt,a,ch in TYPE:
    if tt>t: break
    if a=="key": buf+=ch
    elif a=="bs": buf=buf[:-1]
    else: jpb+=ch
  cw=d.textlength("M",font=mono); cy=H/2-50
  x0=(W-cw*max(len(buf),4))/2 if buf.startswith(".") or len(buf)<=4 and not buf.startswith("D") else (W-cw*7)/2
  if buf.startswith("D") or buf=="" and t>1.5: x0=(W-cw*7)/2
  else: x0=(W-cw*4)/2
  d.text((x0,cy),buf,font=mono,fill=(235,235,235))
  if int(t*3)%2==0 or (TYPE[0][0]<t<TYPE[-1][0]+0.3):
    cx=x0+len(buf)*cw+4; d.rectangle([cx,cy+14,cx+4,cy+80],fill=(200,200,200))
  if jpb: text_c(d,cy+110,jpb,jp,(205,205,205))
  return fr
# ---- 2) montage ----
MON=[("tools",(0.42,0.82,0.24),(0.43,0.82,0.21)),("p18",(0.30,0.30,0.32),(0.33,0.30,0.30)),("room",(0.55,0.40,0.26),(0.55,0.40,0.24)),
 ("sagrada",(0.50,0.50,1.00),(0.50,0.50,0.92)),("p20",(0.60,0.50,0.42),(0.62,0.50,0.40)),("garnier",(0.50,0.66,0.36),(0.50,0.66,0.33)),
 ("crystal",(0.50,0.50,0.85),(0.50,0.50,0.78)),("p23",(0.50,0.42,0.50),(0.52,0.42,0.46)),("plan",(0.47,0.47,0.40),(0.47,0.47,0.36)),
 ("tools",(0.62,0.30,0.30),(0.63,0.30,0.27)),("garnier",(0.50,0.50,0.64),(0.50,0.50,0.60)),("room",(0.50,0.50,0.80),(0.50,0.52,1.00))]
M0=4.2; MD=[0.6]*11+[1.2]
MT=[M0+sum(MD[:i]) for i in range(len(MD)+1)]   # cut times
def montage(t):
  for i in range(len(MON)):
    if MT[i]<=t<MT[i+1]:
      k,a,b=MON[i]; u=(t-MT[i])/(MT[i+1]-MT[i]); c=[a[j]+(b[j]-a[j])*u for j in range(3)]
      return letterbox(grain(IM[k].resize((W,AH),Image.BICUBIC,box=box(c,IM[k]))))
# ---- 3) p5 + copy ; 4) digitizer ----
T3=MT[-1]; T4=T3+2.0
# p5 placed whole: source window y 300..1360 -> AH
SY0,SY1=300,1360; SC=AH/(SY1-SY0); P5W=int(1800*SC)
p5s=IM["p5"].crop((0,SY0,1800,SY1)).resize((P5W,AH),Image.BICUBIC); P5X=(W-P5W)//2
def P(x,y): return (P5X+x*SC, TOP+(y-SY0)*SC)
PTS=[(605,1310),(605,590),(578,530),(864,346),(1164,530),(1148,590),(1148,1310),(605,1310)]
WIN=[(806,660),(914,660),(914,1010),(806,1010),(806,660)]
SEQ=PTS+WIN
def coord(x,y): return f"X {int((x-605)*20):>6,}  Y {int((1310-y)*20):>6,}"
SEG=0.16; DIG0=T4+0.3
def base_p5(dim):
  fr=Image.new("RGB",(W,AH),(9,16,32)); fr.paste(p5s,(P5X,0))
  if dim>0: fr=Image.blend(fr,Image.new("RGB",(W,AH),(0,0,0)),dim)
  return letterbox(grain(fr,5))
def draw_trace(d,t,glow=1.0):
  k=(t-DIG0)/SEG; n=len(SEQ)
  done=int(max(0,min(n-1,math.floor(k)))); frac=max(0,min(1,k-math.floor(k))) if k<n-1 else 0
  cur=None
  for i in range(n):
    if i==len(PTS): pass
    if i>done: break
    x,y=P(*SEQ[i])
    if i>0 and not (i==len(PTS)):  # segment from previous (skip jump to window)
      px,py=P(*SEQ[i-1]); d.line([(px,py),(x,y)],fill=(220,240,255),width=3)
    d.ellipse([x-5,y-5,x+5,y+5],fill=(255,255,255))
    lab=coord(*SEQ[i]); left=SEQ[i][0]<(860 if i<len(PTS) else 860)
    lx=x-12-d.textlength(lab,font=monoXS) if left else x+12
    d.text((lx,y-26),lab,font=monoXS,fill=(150,220,255))
    cur=(x,y)
  if k<n-1 and done+1<n and done+1!=len(PTS):
    x0,y0=P(*SEQ[done]); x1,y1=P(*SEQ[done+1]); e=ease(frac); cx,cy=x0+(x1-x0)*e,y0+(y1-y0)*e
    d.line([(x0,y0),(cx,cy)],fill=(220,240,255),width=3); cur=(cx,cy)
  elif k<n-1 and done+1==len(PTS):
    x0,y0=P(*SEQ[done]); x1,y1=P(*SEQ[done+1]); e=ease(frac); cur=(x0+(x1-x0)*e,y0+(y1-y0)*e)
  return cur, k>=n-1
def cursor(d,c,a=1.0):
  if not c: return
  x,y=c; col=(255,190,60)
  d.ellipse([x-20,y-20,x+20,y+20],outline=col,width=2); d.line([(x-42,y),(x+42,y)],fill=col,width=2); d.line([(x,y-42),(x,y+42)],fill=col,width=2)
DIG_END=DIG0+SEG*(len(SEQ)-1)+0.2
T5=DIG_END+1.6
def digit(t):
  if t<T4:
    fr=base_p5(0); d=ImageDraw.Draw(fr); al=ease((t-T3-0.4)/0.6)
    if al>0:
      yy=np.arange(H)[:,None]; band=np.exp(-((yy-(H/2-12))/120.0)**2)*0.55*al
      a=np.asarray(fr).astype(np.float32); a=a*(1-band[...,None])+np.array([4,10,28],np.float32)*band[...,None]
      fr=Image.fromarray(a.clip(0,255).astype(np.uint8)); d=ImageDraw.Draw(fr)
      text_c(d,H/2-40,"設計は、手から始まった。",jpL,gray(245,al)); text_c(d,TOP+AH+48,"Design began with the hand.",en,gray(200,al))
    return fr
  dim=ease((t-DIG_END)/0.6)*0.92
  fr=base_p5(dim); d=ImageDraw.Draw(fr)
  c,fin=draw_trace(d,t)
  if not fin: cursor(d,c)
  al=ease((t-(DIG_END+0.1))/0.4)
  if al>0:
    d.text((1240,H/2-60),"手の動きが、",font=jpL,fill=gray(245,al)); d.text((1240,H/2+4),"はじめて数値になった。",font=jpL,fill=gray(245,al))
    text_c(d,TOP+AH+48,"The hand's motion became numbers.",en,gray(200,al))
  return fr

# ---- 5) CAD 風デスクトップ（汎用の見た目。特定製品のロゴ・名称は出さない）----
uiF=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",18); uiS=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",15)
CAD0=T5; CAD1=CAD0+5.6
def cad(t):
  u=t-CAD0; fr=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(fr)
  x0,y0,x1,y1=0,TOP,W,TOP+AH
  # 窓枠・ツールバー・パネル
  d.rectangle([x0,y0,x1,y0+34],fill=(46,50,58)); d.text((x0+16,y0+7),"Drawing1.dwg",font=uiF,fill=(210,214,220))
  for k in range(3): d.ellipse([x1-90+k*26,y0+11,x1-78+k*26,y0+23],fill=(90,96,108))
  d.rectangle([x0,y0+34,x1,y0+86],fill=(58,63,72))
  for k in range(26): d.rectangle([x0+16+k*44,y0+44,x0+48+k*44,y0+76],outline=(120,128,140),width=1)
  d.rectangle([x0,y0+86,x0+56,y1-70],fill=(50,54,62))
  for k in range(12): d.rectangle([x0+12,y0+98+k*44,x0+44,y0+130+k*44],outline=(120,128,140),width=1)
  d.rectangle([x1-260,y0+86,x1,y1-70],fill=(50,54,62))
  for k,nm in enumerate(["0","A-WALL","A-GLAZ","A-ROOF","S-GRID","DIM"]):
    d.text((x1-240,y0+100+k*30),("■ " if k else "□ ")+nm,font=uiS,fill=(190,196,206))
  # 作図領域
  mx0,my0,mx1,my1=x0+56,y0+86,x1-260,y1-70
  d.rectangle([mx0,my0,mx1,my1],fill=(22,24,28))
  # ズーム：1棟 → 横に並ぶ → 街
  z=1.0-0.78*ease((u-2.6)/2.4)
  cx=(mx0+mx1)/2; cy=(my0+my1)/2+40
  sp=12; gx=(mx1-mx0)/40
  for gxi in range(-60,61):
    for gyi in range(-30,31,1):
      if gxi%2==0 and gyi%2==0:
        px=cx+gxi*gx*z*2; py=cy+gyi*gx*z*2
        if mx0<px<mx1 and my0<py<my1: d.point((px,py),fill=(60,64,72))
  # 建物の線（デジタイザでなぞった形）を CAD の線として描く
  bw=(1148-605); bh=(1310-346)
  sc=0.5*z
  n_copy=1 if u<1.6 else int(1+min(14,(u-1.6)*10))
  prog=min(1,u/1.2)
  segs=[(PTS[i-1],PTS[i]) for i in range(1,len(PTS))]+[(WIN[i-1],WIN[i]) for i in range(1,len(WIN))]
  for c in range(n_copy):
    off=(c-(0 if n_copy==1 else 0))
    ox=cx+(c-n_copy//2)*bw*sc*1.15 if n_copy>1 else cx
    for j,(a,b) in enumerate(segs):
      f=1 if c>0 else max(0,min(1,prog*len(segs)-j))
      if f<=0: continue
      ax=ox+(a[0]-876)*sc; ay=cy+(a[1]-828)*sc; bx=ox+(b[0]-876)*sc; by=cy+(b[1]-828)*sc
      ex,ey=ax+(bx-ax)*f,ay+(by-ay)*f
      if mx0<ax<mx1 and mx0<ex<mx1: d.line([(ax,ay),(ex,ey)],fill=(235,235,235) if c==0 else (120,200,255),width=2)
  # 十字カーソル
  if u<1.4:
    k=min(len(segs)-1,int(prog*len(segs))); a,b=segs[k]; f=prog*len(segs)-k
    px=cx+((a[0]+(b[0]-a[0])*f)-876)*sc; py=cy+((a[1]+(b[1]-a[1])*f)-828)*sc
  else: px,py=cx+180,cy-120
  d.line([(mx0,py),(mx1,py)],fill=(180,180,180),width=1); d.line([(px,my0),(px,my1)],fill=(180,180,180),width=1)
  d.rectangle([px-6,py-6,px+6,py+6],outline=(230,230,230),width=1)
  # コマンドライン・座標表示
  d.rectangle([x0,y1-70,x1,y1],fill=(40,43,50))
  cmds=["LINE","Specify first point: 0,0","Specify next point: @0,19280","ARRAY  Rows: 1  Columns: 15","ZOOM  Extents"]
  ci=min(len(cmds)-1,int(u/1.1)); txt=cmds[ci]; typed=txt[:int(len(txt)*min(1,(u-ci*1.1)/0.5))]
  d.text((x0+16,y1-62),"Command: "+typed+("_" if int(u*4)%2 else ""),font=uiF,fill=(220,224,230))
  d.text((x0+16,y1-32),f"{(px-cx)/sc*20:10.1f}, {(cy-py)/sc*20:10.1f}, 0.0      GRID  SNAP  ORTHO",font=uiS,fill=(150,156,168))
  al=ease((u-0.2)/0.4)*(1-ease((u-4.6)/0.5))
  if al>0:
    d.text((mx0+40,my0+30),"正確になった。",font=jpL,fill=gray(245,al))
    text_c(d,TOP+AH+48,"More precise.",en,gray(200,al))
  fo=ease((u-5.1)/0.5)
  if fo>0: fr=Image.blend(fr,Image.new("RGB",(W,H),(0,0,0)),fo)
  return fr
# ---- 6) 写真：白黒 → 昭和 → 現代（差し替え枠つき）----
PH0=CAD1
PH=[("img","scott",(0.5,0.45,1.0)),("img","notre",(0.5,0.5,0.95)),("img","taj",(0.5,0.5,0.95)),("img","sagrada",(0.5,0.5,0.95)),("img","arc",(0.5,0.5,0.95)),
    ("img","d55",(0.5,0.45,1.0)),("img","d61",(0.5,0.45,1.0)),("img","d7",(0.5,0.45,1.0)),("img","d25",(0.5,0.55,1.0)),("img","d26",(0.5,0.5,1.0)),("img","d27",(0.5,0.45,1.0)),("img","d23",(0.5,0.5,1.0)),("img","d28",(0.5,0.5,1.0)),
    ("slot","現代：代表の現場写真 1（Google フォト）",(70,96,120)),
    ("slot","現代：代表の現場写真 2（Google フォト）",(80,110,130)),
    ("slot","現代：代表の現場写真 3（Google フォト）",(90,120,140))]
PD=[0.55,0.5,0.45,0.42,0.4, 0.5,0.45,0.42,0.4,0.38,0.36,0.35,0.6, 0.6,0.6,1.2]
PT=[PH0+sum(PD[:i]) for i in range(len(PD)+1)]
END=PT[-1]+0.6
slotF=ImageFont.truetype(F+"Noto_Sans_JP_wght_300.ttf",30)
def photos(t):
  for i,(kind,a,b) in enumerate(PH):
    if PT[i]<=t<PT[i+1]:
      u=(t-PT[i])/(PT[i+1]-PT[i])
      if kind=="img":
        c=(b[0],b[1],b[2]*(1-0.05*u)); return letterbox(grain(IM[a].resize((W,AH),Image.BICUBIC,box=box(c,IM[a]))))
      pic=Image.new("RGB",(W,AH),b); d=ImageDraw.Draw(pic)
      for k in range(0,W,80): d.line([(k,0),(k,AH)],fill=tuple(min(255,v+10) for v in b))
      w=d.textlength(a,font=slotF); d.text(((W-w)/2,AH/2-20),a,font=slotF,fill=(235,235,235))
      d.text((40,AH-50),"差し替え予定",font=slotF,fill=(200,200,200))
      fr=letterbox(pic)
      if i==len(PH)-1:
        fo=ease((t-(PT[-1]-0.4))/0.4); fr=Image.blend(fr,Image.new("RGB",(W,H),(0,0,0)),fo)
      return fr
  return Image.new("RGB",(W,H),(0,0,0))
N=int(END*FPS)
for n in range(N):
  t=n/FPS
  if t<M0: fr=title(t)
  elif t<T3: fr=montage(t)
  elif t<T5: fr=digit(t)
  elif t<CAD1: fr=cad(t)
  else: fr=photos(t)
  fr.save(f"{OUT}/frames/f{n:04d}.jpg",quality=90)
# ---- 音（すべて合成の仮音）：タイプライター → 鉛筆・ペン・紙 ----
SR=48000; L=int(SR*END); y=np.zeros(L)
def bp(n,lo,hi):
  x=rng.normal(0,1,n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR); X*=((f>lo)&(f<hi)); return np.fft.irfft(X,n)
def add(t0,seg,g=1.0):
  i=int(t0*SR)
  if i>=L: return
  m=min(len(seg),L-i); y[i:i+m]+=seg[:m]*g
def tw_key(t0,amp=0.5):
  n=int(0.09*SR); tt=np.arange(n)/SR
  click=bp(n,2500,9000)*np.exp(-tt*500)*0.6
  thud=bp(n,90,500)*np.exp(-tt*60)*0.9
  ring=np.sin(2*np.pi*2350*tt)*np.exp(-tt*70)*0.05
  add(t0,(click+thud+ring)*amp)
def tw_bs(t0): tw_key(t0,0.28)
def pencil(t0,dur,amp=0.05,lo=1800,hi=7000):
  n=int(dur*SR); tt=np.linspace(0,1,n)
  env=np.sin(np.pi*tt)**0.5*(0.6+0.4*np.abs(np.sin(tt*rng.uniform(8,30))))
  grain=1+0.5*rng.normal(0,1,n).cumsum()/np.sqrt(n)
  add(t0,bp(n,lo,hi)*env*np.clip(grain,0.3,2)*amp)
def write(t0,dur,amp=0.04):  # 字を書く：短い線の連続
  t=t0
  while t<t0+dur:
    d=rng.uniform(0.04,0.12); pencil(t,d,amp*rng.uniform(0.6,1.2),2500,8000); t+=d+rng.uniform(0.01,0.05)
def flip(t0,amp=0.09):  # 紙をめくる
  n=int(0.32*SR); tt=np.linspace(0,1,n); x=rng.normal(0,1,n)
  X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR); X*=(f<5000)*(f>200); x=np.fft.irfft(X,n)
  env=np.exp(-((tt-0.35)/0.18)**2); crk=(rng.random(n)<0.002)*rng.normal(0,3,n)
  add(t0,(x*env+bp(n,3000,9000)*crk*0.3)*amp)
def click(t0,amp=0.18,dur=0.012,lo=2500,hi=9000):
  n=int(dur*SR); env=np.exp(-np.linspace(0,8,n)); add(t0,bp(n,lo,hi)*env*amp)
# 1) タイプライター
for tt,a,ch in TYPE:
  if a=="key": tw_key(tt)
  elif a=="bs": tw_bs(tt)
  else: tw_key(tt,0.35)
# 2) モンタージュ：カットごとに線を引く音、だんだん密に・重ねる
for k,tc in enumerate(MT[:-1]):
  dens=1+k//3
  for j in range(dens): pencil(tc+j*0.12,rng.uniform(0.18,0.4),0.045)
  if k%4==0: flip(tc-0.05)
  if k%3==1: write(tc+0.1,0.4)
# 3) 青焼きにコピー → なぞり（クリック）＋線の音
write(T3+0.3,0.9,0.03)
for i in range(len(SEQ)): click(DIG0+SEG*i,0.22); pencil(DIG0+SEG*i,SEG*0.9,0.03,1200,5000)
# 4) CAD：キー入力
for k in range(26): click(CAD0+0.05+k*0.09+rng.uniform(0,0.03),0.07,0.008,3000,9000)
for k in range(8): click(CAD0+2.6+k*0.2,0.12,0.01,1500,6000)
# 5) 写真の流れ：切り替えごとに書く音・線の音を重ね、紙をめくる
for k,tc in enumerate(PT[:-1]):
  layers=1+min(4,k//3)
  for j in range(layers): pencil(tc+j*0.07,rng.uniform(0.15,0.35),0.04)
  if k%2==0: write(tc,0.3,0.03)
  if k in (0,5,13): flip(tc-0.08,0.11)
tt=np.arange(L)/SR
pad=(np.sin(2*math.pi*55*tt)+0.5*np.sin(2*math.pi*82.5*tt))*0.035*np.clip((tt-T3)/1.0,0,1)*np.clip((END-tt)/0.8,0,1); y+=pad
y+=rng.normal(0,0.0015,L)
y=y/max(1e-6,np.max(np.abs(y)))*0.9
with wave.open(OUT+"/audio.wav","wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y*32767).astype(np.int16).tobytes())
print("frames",N,"dur",round(END,2))
