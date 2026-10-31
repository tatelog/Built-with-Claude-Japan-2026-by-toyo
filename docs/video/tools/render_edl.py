# 編集ページと同じ編集データ（EDL）から、高画質版を書き出す。効果音トラックも作る。
# 使い方: render_edl.py <edl.json> <assetmap.json> <outdir> [--sfx-only]
import json, sys, math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
EDL=json.load(open(sys.argv[1])); AM=json.load(open(sys.argv[2])); OUT=sys.argv[3]; SFX_ONLY="--sfx-only" in sys.argv
os.makedirs(OUT+"/frames",exist_ok=True)
W,H,FPS=1920,1080,24
FONTS=os.path.dirname(os.path.abspath(sys.argv[2]))+"/../fonts/"
jpT=ImageFont.truetype(FONTS+"Noto_Sans_JP_wght_300.ttf",64); jpS=ImageFont.truetype(FONTS+"Noto_Sans_JP_wght_300.ttf",50)
en=ImageFont.truetype(FONTS+"IBM_Plex_Mono_wght_300.ttf",26); mono=ImageFont.truetype(FONTS+"IBM_Plex_Mono_wght_300.ttf",80)
clips=EDL["clips"]; scope=EDL.get("aspect","scope")=="scope"
AH=round(W/2.39) if scope else H; TOP=(H-AH)//2
starts=[]; a=0
for c in clips: starts.append(a); a+=max(0.1,float(c.get("dur",1)))
TOTAL=a
EASE={"linear":lambda u:u,"inout":lambda u:0.5-0.5*math.cos(math.pi*u),"in":lambda u:u**3,"out":lambda u:1-(1-u)**3}
cache={}
def load(c):
  key=(c.get("img"),bool(c.get("mono")))
  if key in cache: return cache[key]
  im=Image.open(AM[c["img"]]).convert("RGB")
  if c.get("mono"):
    g=ImageOps.grayscale(im); im=ImageOps.colorize(g,(10,10,12),(240,236,228))
  cache[key]=im; return im
vframes={}
def vframe(c,t_in):
  aid=c["asset"]
  if aid not in vframes:
    d=f"{OUT}/v_{aid}"; os.makedirs(d,exist_ok=True)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",AM[aid],"-vf",f"fps={FPS},scale={W}:-2",f"{d}/%05d.jpg"],check=True)
    vframes[aid]=sorted(os.listdir(d))
  fl=vframes[aid]; k=min(len(fl)-1,max(0,int(t_in*FPS)))
  return Image.open(f"{OUT}/v_{aid}/{fl[k]}").convert("RGB")
rng=np.random.default_rng(3)
def lerp(a,b,u): return a+(b-a)*u
def draw_clip(fr,k,t,alpha=1.0):
  c=clips[k]; dur=max(0.1,float(c["dur"])); u=min(1,max(0,(t-starts[k])/dur))
  ms=float(c.get("ms",0)); me=float(c.get("me",1)); um=EASE.get(c.get("ease","inout"),EASE["inout"])(min(1,max(0,(u-ms)/max(0.01,me-ms))))
  layer=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(layer)
  if c["kind"]=="text":
    bg={"white":(244,244,242),"blue":(29,63,110)}.get(c.get("bg"),(0,0,0)); d.rectangle([0,TOP,W,TOP+AH],fill=bg)
  else:
    src=load(c) if c["kind"]=="image" else vframe(c,float(c.get("in",0))+(t-starts[k])*float(c.get("speed",1)))
    sw,sh=src.size; z=lerp(float(c.get("z0",1)),float(c.get("z1",1)),um); px=lerp(float(c.get("x0",0)),float(c.get("x1",0)),um); py=lerp(float(c.get("y0",0)),float(c.get("y1",0)),um)
    rot=lerp(float(c.get("rot0",0)),float(c.get("rot1",0)),um)
    sc=max(W/sw,AH/sh)*z; w,h=sw*sc,sh*sc
    ox=(W-w)/2-px*(w-W)/2; oy=TOP+(AH-h)/2-py*(h-AH)/2
    # 見える範囲だけを切り出して拡大（回転があれば少し広めに）
    pad=1.25 if rot else 1.0
    bx0=(-ox)/sc; by0=(TOP-oy)/sc; bw=W/sc; bh=AH/sc
    cx,cy=bx0+bw/2,by0+bh/2; bw2,bh2=bw*pad,bh*pad
    piece=src.resize((int(W*pad),int(AH*pad)),Image.BICUBIC,box=(cx-bw2/2,cy-bh2/2,cx+bw2/2,cy+bh2/2))
    if rot: piece=piece.rotate(-rot,resample=Image.BICUBIC,center=(piece.width/2,piece.height/2))
    piece=piece.crop(((piece.width-W)//2,(piece.height-AH)//2,(piece.width-W)//2+W,(piece.height-AH)//2+AH))
    a_=np.asarray(piece).astype(np.int16); a_+=rng.normal(0,5,(a_.shape[0],a_.shape[1],1)).astype(np.int16); piece=Image.fromarray(np.clip(a_,0,255).astype(np.uint8))
    layer.paste(piece,(0,TOP))
  ja=c.get("textJa","")
  if ja:
    if c["kind"]=="text" and c.get("typing"):
      chars=list(ja); n=int(min(1,u*1.6)*len(chars)); ja="".join(chars[:n])
    lines=ja.split("\n"); font=(mono if c["kind"]=="text" and all(ord(ch)<128 for ch in ja.replace("\n","")) else (jpT if c["kind"]=="text" else jpS))
    col=(20,20,20) if c.get("bg")=="white" else (240,240,240)
    for i,ln in enumerate(lines):
      f=font if i==0 else jpS
      tw=d.textlength(ln,font=f); d.text(((W-tw)/2,H/2-40+(i-(len(lines)-1)/2)*90),ln,font=f,fill=col)
    if c["kind"]=="text" and c.get("typing") and u<0.75 and int(t*3)%2==0 and lines:
      lw=d.textlength(lines[-1],font=font if len(lines)==1 else jpS); y=H/2-40+((len(lines)-1)/2)*90
      d.rectangle([(W+lw)/2+6,y+12,(W+lw)/2+11,y+88],fill=col)
  if c.get("textEn"):
    tw=d.textlength(c["textEn"],font=en); d.text(((W-tw)/2,TOP+AH+(H-TOP-AH)/2-14 if scope else H-60),c["textEn"],font=en,fill=(205,205,205))
  if alpha>=1: return layer
  return Image.blend(fr,layer,alpha)
if not SFX_ONLY:
  N=int(TOTAL*FPS)
  for n in range(N):
    t=n/FPS; k=next(i for i in range(len(clips)) if starts[i]<=t<starts[i]+max(0.1,float(clips[i]["dur"]))) if t<TOTAL else len(clips)-1
    c=clips[k]
    if c.get("trans")=="fade" and k>0 and t-starts[k]<0.4:
      fr=draw_clip(None,k-1,t); fr=draw_clip(fr,k,t,(t-starts[k])/0.4)
    else: fr=draw_clip(None,k,t)
    fr.save(f"{OUT}/frames/f{n:05d}.jpg",quality=90)
# ---- 効果音トラック（編集データのタイミングから作る。合成の仮音）----
SR=48000; L=int(SR*(TOTAL+0.5)); y=np.zeros(L)
def bp(n,lo,hi):
  x=rng.normal(0,1,n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR); X*=((f>lo)&(f<hi)); return np.fft.irfft(X,n)
def add(t0,seg,g=1.0):
  i=int(t0*SR)
  if i<0 or i>=L: return
  m=min(len(seg),L-i); y[i:i+m]+=seg[:m]*g
def tw_key(t0,amp=0.5):
  n=int(0.09*SR); tt=np.arange(n)/SR
  add(t0,(bp(n,2500,9000)*np.exp(-tt*500)*0.6+bp(n,90,500)*np.exp(-tt*60)*0.9+np.sin(2*np.pi*2350*tt)*np.exp(-tt*70)*0.05)*amp)
def pencil(t0,dur,amp=0.05,lo=1800,hi=7000):
  n=max(10,int(dur*SR)); tt=np.linspace(0,1,n); env=np.sin(np.pi*tt)**0.5*(0.6+0.4*np.abs(np.sin(tt*rng.uniform(8,30))))
  add(t0,bp(n,lo,hi)*env*amp)
def write(t0,dur,amp=0.035):
  t=t0
  while t<t0+dur:
    d=rng.uniform(0.04,0.12); pencil(t,d,amp*rng.uniform(0.6,1.2),2500,8000); t+=d+rng.uniform(0.01,0.05)
def flip(t0,amp=0.1):
  n=int(0.32*SR); tt=np.linspace(0,1,n); x=bp(n,200,5000); env=np.exp(-((tt-0.35)/0.18)**2); add(t0,x*env*amp)
img_i=0
for k,c in enumerate(clips):
  s=starts[k]; dur=float(c["dur"])
  if c["kind"]=="text" and c.get("typing"):
    chars=[ch for ch in c.get("textJa","") if ch!="\n"]
    for j in range(len(chars)): tw_key(s+dur*(j+1)/(len(chars)*1.6)-0.02)
  elif c["kind"]=="image":
    layers=1+min(4,img_i//4)
    for j in range(layers): pencil(s+j*0.06,rng.uniform(0.15,0.38),0.045)
    if img_i%3==1: write(s+0.05,min(0.4,dur))
    if img_i%5==0: flip(s-0.06)
    img_i+=1
y=y/max(1e-6,np.max(np.abs(y)))*0.85
with wave.open(OUT+"/sfx.wav","wb") as w_: w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((y*32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+"/sfx.wav","-c:a","aac","-b:a","160k","-movflags","+faststart",OUT+"/sfx.mp4"],check=True)
print("total",round(TOTAL,2),"clips",len(clips))
