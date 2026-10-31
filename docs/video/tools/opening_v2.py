# 冒頭の試作 v2：速いモンタージュ → 手の時代のコピー → デジタイザでなぞる → 数値（DXF）の壁
import numpy as np, math, wave, sys, io
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import ezdxf
S=sys.argv[1]; OUT=S+"/op2"
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
  else: im=ImageEnhance.Color(im).enhance(0.85)
  return im
IM={k:load(p,m) for k,(p,m) in {
 "tools":(S+"/intl/met_198857.jpg","mono"),"p18":(S+"/ndl/teikoku_p18.jpg","blue"),"p20":(S+"/ndl/teikoku_p20.jpg","blue"),
 "p23":(S+"/ndl/teikoku_p23.jpg","blue"),"p5":(S+"/ndl/teikoku_p5.jpg","blue"),"room":(S+"/ndl/kyudai_seizushitsu.jpg","mono"),
 "garnier":(S+"/intl/met_269271.jpg","mono"),"crystal":(S+"/intl/met_269619.jpg","mono"),"sagrada":(S+"/intl/sf_gili1905.jpg","mono"),
 "plan":(S+"/ndl/kyudai_p6.jpg","mono")}.items()}
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
def title(t):
  fr=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(fr)
  if t<1.0: return fr
  cy=H/2-50; a_in=min(1,(t-1.0)/0.3); cw=d.textlength("M",font=mono)
  src,dst=".dwg","Drawing"; sx0=(W-cw*4)/2; dx0=(W-cw*7)/2; m=ease((t-1.8)/0.6); mp={1:0,2:3,3:6}
  for i,ch in enumerate(src):
    if i==0: al=a_in*(1-m); x=sx0
    else: al=a_in; x=sx0+i*cw+(dx0+mp[i]*cw-(sx0+i*cw))*m
    if i==1 and m>0.5: ch="D"
    if al>0: d.text((x,cy),ch,font=mono,fill=gray(235,al))
  for j in (1,2,4,5):
    al=ease((t-2.1)/0.4)
    if al>0: d.text((dx0+j*cw,cy),dst[j],font=mono,fill=gray(235,al))
  if t<1.8 and int(t*3)%2==0: d.rectangle([sx0+4*cw+6,cy+14,sx0+4*cw+10,cy+80],fill=gray(200,a_in))
  al=ease((t-2.6)/0.4)
  if al>0: text_c(d,cy+110,"図面",jp,gray(200,al))
  return fr
# ---- 2) montage ----
MON=[("tools",(0.42,0.82,0.24),(0.43,0.82,0.21)),("p18",(0.30,0.30,0.32),(0.33,0.30,0.30)),("room",(0.55,0.40,0.26),(0.55,0.40,0.24)),
 ("sagrada",(0.50,0.50,1.00),(0.50,0.50,0.92)),("p20",(0.60,0.50,0.42),(0.62,0.50,0.40)),("garnier",(0.50,0.66,0.36),(0.50,0.66,0.33)),
 ("crystal",(0.50,0.50,0.85),(0.50,0.50,0.78)),("p23",(0.50,0.42,0.50),(0.52,0.42,0.46)),("plan",(0.47,0.47,0.40),(0.47,0.47,0.36)),
 ("tools",(0.62,0.30,0.30),(0.63,0.30,0.27)),("garnier",(0.50,0.50,0.64),(0.50,0.50,0.60)),("room",(0.50,0.50,0.80),(0.50,0.52,1.00))]
M0=3.8; MD=[0.6]*11+[1.2]
MT=[M0+sum(MD[:i]) for i in range(len(MD)+1)]   # cut times
def montage(t):
  for i in range(len(MON)):
    if MT[i]<=t<MT[i+1]:
      k,a,b=MON[i]; u=(t-MT[i])/(MT[i+1]-MT[i]); c=[a[j]+(b[j]-a[j])*u for j in range(3)]
      return letterbox(grain(IM[k].resize((W,AH),Image.BICUBIC,box=box(c,IM[k]))))
# ---- 3) p5 + copy ; 4) digitizer ----
T3=MT[-1]; T4=T3+2.8
# p5 placed whole: source window y 300..1360 -> AH
SY0,SY1=300,1360; SC=AH/(SY1-SY0); P5W=int(1800*SC)
p5s=IM["p5"].crop((0,SY0,1800,SY1)).resize((P5W,AH),Image.BICUBIC); P5X=(W-P5W)//2
def P(x,y): return (P5X+x*SC, TOP+(y-SY0)*SC)
PTS=[(605,1310),(605,590),(578,530),(864,346),(1164,530),(1148,590),(1148,1310),(605,1310)]
WIN=[(806,660),(914,660),(914,1010),(806,1010),(806,660)]
SEQ=PTS+WIN
def coord(x,y): return f"X {int((x-605)*20):>6,}  Y {int((1310-y)*20):>6,}"
SEG=0.42; DIG0=T4+0.5
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
DIG_END=DIG0+SEG*(len(SEQ)-1)+0.3
T5=DIG_END+2.2
def digit(t):
  if t<T4:
    fr=base_p5(0); d=ImageDraw.Draw(fr); al=ease((t-T3-0.4)/0.6)
    if al>0:
      yy=np.arange(H)[:,None]; band=np.exp(-((yy-(H/2-12))/120.0)**2)*0.55*al
      a=np.asarray(fr).astype(np.float32); a=a*(1-band[...,None])+np.array([4,10,28],np.float32)*band[...,None]
      fr=Image.fromarray(a.clip(0,255).astype(np.uint8)); d=ImageDraw.Draw(fr)
      text_c(d,H/2-40,"設計は、手から始まった。",jpL,gray(245,al)); text_c(d,TOP+AH+48,"Design began with the hand.",en,gray(200,al))
    return fr
  dim=ease((t-DIG_END)/1.0)*0.92
  fr=base_p5(dim); d=ImageDraw.Draw(fr)
  c,fin=draw_trace(d,t)
  if not fin: cursor(d,c)
  al=ease((t-(DIG_END+0.3))/0.6)
  if al>0:
    d.text((1240,H/2-60),"手の動きが、",font=jpL,fill=gray(245,al)); d.text((1240,H/2+4),"はじめて数値になった。",font=jpL,fill=gray(245,al))
    text_c(d,TOP+AH+48,"The hand's motion became numbers.",en,gray(200,al))
  return fr
# ---- 5) 数値の壁（同じ線から作った DXF の中身）----
doc=ezdxf.new("R2018"); msp=doc.modelspace()
wpt=lambda p:((p[0]-605)*20,(1310-p[1])*20)
msp.add_lwpolyline([wpt(p) for p in PTS]); msp.add_lwpolyline([wpt(p) for p in WIN])
sio=io.StringIO(); doc.write(sio); DX=[l.strip() for l in sio.getvalue().splitlines() if l.strip()]
open(OUT+"/trace.dxf","w").write(sio.getvalue())
k0=next(i for i,l in enumerate(DX) if l=="ENTITIES"); BODY=DX[k0:]+DX[:k0]
END=T5+3.4
def wall(t):
  u=(t-T5); fr=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(fr)
  cols=7; cwid=W/cols; lh=24; speed=520+900*ease(u/3.0)
  for c in range(cols):
    off=(u*speed*(0.8+0.12*c)+c*977)%(len(BODY)*lh)
    st=int(off//lh); dy=off%lh
    for r in range(int(AH/lh)+2):
      s=BODY[(st+r+c*131)%len(BODY)]; y=TOP+r*lh-dy
      if TOP-lh<y<TOP+AH: d.text((c*cwid+24,y),s[:16],font=monoS,fill=(70+30*(c%2),150,210) if s.replace('.','').replace('-','').isdigit() else (110,120,135))
  # 線は薄く残す
  for i in range(1,len(PTS)): d.line([P(*PTS[i-1]),P(*PTS[i])],fill=(200,230,255),width=2)
  for i in range(1,len(WIN)): d.line([P(*WIN[i-1]),P(*WIN[i])],fill=(200,230,255),width=2)
  a=np.asarray(fr).astype(np.float32); a[:TOP]=0; a[TOP+AH:]=0
  fo=ease((t-(END-0.6))/0.6); a*=1-fo
  return Image.fromarray(a.astype(np.uint8))
N=int(END*FPS)
for n in range(N):
  t=n/FPS
  if t<M0: fr=title(t)
  elif t<T3: fr=montage(t)
  elif t<T5: fr=digit(t)
  else: fr=wall(t)
  fr.save(f"{OUT}/frames/f{n:04d}.jpg",quality=92)
# ---- 仮の音 ----
SR=48000; L=int(SR*END); y=np.zeros(L)
def bp(n,lo,hi):
  x=rng.normal(0,1,n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR); X*=((f>lo)&(f<hi)); return np.fft.irfft(X,n)
def add(t0,seg):
  i=int(t0*SR); m=max(0,min(len(seg),L-i)); y[i:i+m]+=seg[:m]
def stroke(t0,dur,amp=0.05):
  n=int(dur*SR); env=np.sin(np.linspace(0,math.pi,n))**0.6; add(t0,bp(n,1800,7000)*env*amp)
def click(t0,amp=0.18,dur=0.012,lo=2500,hi=9000):
  n=int(dur*SR); env=np.exp(-np.linspace(0,8,n)); add(t0,bp(n,lo,hi)*env*amp)
for t0,dd in [(0.15,0.3),(0.5,0.22),(0.78,0.3)]: stroke(t0,dd)
for tc in MT[:-1]: click(tc,0.10,0.03,800,6000)          # カットごとの紙の音
for i in range(len(SEQ)): click(DIG0+SEG*i,0.22)           # デジタイザのクリック
tt=np.arange(L)/SR
sw=bp(L,300,4000)*np.clip((tt-T5)/2.5,0,1)*np.clip((END-tt)/0.6,0,1)*0.04; y+=sw
pad=(np.sin(2*math.pi*55*tt)+0.5*np.sin(2*math.pi*82.5*tt))*0.045*np.clip((tt-T3)/1.0,0,1)*np.clip((T5+0.5-tt)/1.0,0,1); y+=pad
y+=rng.normal(0,0.002,L); y=np.clip(y,-1,1)
with wave.open(OUT+"/audio.wav","wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y*32767).astype(np.int16).tobytes())
print("frames",N,"dur",round(END,2),"T3",round(T3,2),"T4",round(T4,2),"T5",round(T5,2))
