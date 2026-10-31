import numpy as np, math, wave, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
S=sys.argv[1]; OUT=S+"/op"
W,H,FPS,DUR=1920,1080,24,20.0
AH=round(W/2.39); TOP=(H-AH)//2  # 803px picture, letterbox bars
F=S+"/fonts/"
mono=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",72)
jp=ImageFont.truetype(F+"Noto_Sans_JP_wght_300.ttf",44)
jpL=ImageFont.truetype(F+"Noto_Sans_JP_wght_300.ttf",46)
en=ImageFont.truetype(F+"IBM_Plex_Mono_wght_300.ttf",24)
def load(p,mode):
  im=Image.open(p).convert("RGB")
  if mode=="mono":
    g=ImageOps.grayscale(im); g=ImageOps.autocontrast(g,cutoff=1)
    im=ImageOps.colorize(g,(14,14,16),(236,232,224))
  elif mode=="blue":
    im=ImageEnhance.Color(im).enhance(0.85)
  return im
IM={
 "tools":load(S+"/intl/met_198857.jpg","mono"),
 "p18":load(S+"/ndl/teikoku_p18.jpg","blue"),
 "p20":load(S+"/ndl/teikoku_p20.jpg","blue"),
 "room":load(S+"/ndl/kyudai_seizushitsu.jpg","mono"),
 "garnier":load(S+"/intl/met_269271.jpg","mono"),
 "p5":load(S+"/ndl/teikoku_p5.jpg","blue"),
}
A=2.39
def box(cx,cy,w,im):  # center/width in fractions -> pixel box with 2.39 aspect
  iw,ih=im.size; pw=w*iw; ph=pw/A
  return (cx*iw-pw/2, cy*ih-ph/2, cx*iw+pw/2, cy*ih+ph/2)
# shots: (start,end,key,(cx,cy,w) from,(cx,cy,w) to)
SH=[
 (5.6,8.0,"tools",(0.50,0.80,0.46),(0.50,0.81,0.34)),
 (8.0,10.4,"p18",(0.42,0.40,0.70),(0.58,0.40,0.70)),
 (10.4,10.9,"room",(0.45,0.36,0.30),(0.45,0.36,0.29)),
 (10.9,11.4,"p20",(0.55,0.45,0.35),(0.56,0.45,0.34)),
 (11.4,15.0,"room",(0.50,0.40,0.42),(0.50,0.50,1.00)),
 (15.0,17.0,"garnier",(0.50,0.50,0.62),(0.50,0.49,0.44)),
 (17.0,20.0,"p5",(0.505,0.33,0.56),(0.505,0.55,0.56)),
]
ease=lambda t:0.5-0.5*math.cos(math.pi*max(0,min(1,t)))
rng=np.random.default_rng(7)
def grain(img,amt=7):
  a=np.asarray(img).astype(np.int16); n=rng.normal(0,amt,(a.shape[0],a.shape[1],1)).astype(np.int16)
  return Image.fromarray(np.clip(a+n,0,255).astype(np.uint8))
def text_c(d,y,s,font,fill):
  w=d.textlength(s,font=font); d.text(((W-w)/2,y),s,font=font,fill=fill)
def title_frame(t):
  fr=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(fr)
  if t<1.5 or t>=5.2: return fr
  cy=H/2-50
  a_in=min(1,(t-1.5)/0.5)
  src=".dwg"; dst="Drawing"
  cw=d.textlength("M",font=mono)
  sx0=(W-cw*len(src))/2; dx0=(W-cw*len(dst))/2
  m=ease((t-3.0)/0.9)
  # map: '.'->fade, d->0,w->3,g->6 ; new letters r,a,i,n at 1,2,4,5
  mp={1:0,2:3,3:6}
  for i,ch in enumerate(src):
    if i==0: al=a_in*(1-m); x=sx0
    else: al=a_in; x=sx0+i*cw+(dx0+mp[i]*cw-(sx0+i*cw))*m
    if i==1 and m>0.5: ch="D"
    if al>0: d.text((x,cy),ch,font=mono,fill=tuple(int(235*al) for _ in range(3)))
  for j in (1,2,4,5):
    al=ease((t-3.4)/0.6)
    if al>0: d.text((dx0+j*cw,cy),dst[j],font=mono,fill=tuple(int(235*al) for _ in range(3)))
  if t<3.0 and int(t*2)%2==0:  # caret
    d.rectangle([sx0+len(src)*cw+6,cy+14,sx0+len(src)*cw+10,cy+80],fill=(int(200*a_in),)*3)
  al=ease((t-4.0)/0.5)
  if al>0: text_c(d,cy+110,"図面",jp,tuple(int(200*al) for _ in range(3)))
  return fr
def shot_frame(t):
  for (s,e,k,f0,f1) in SH:
    if s<=t<e:
      u=ease((t-s)/(e-s)); im=IM[k]
      c=[f0[i]+(f1[i]-f0[i])*u for i in range(3)]
      bx=box(c[0],c[1],c[2],im)
      pic=im.resize((W,AH),Image.BICUBIC,box=bx)
      pic=grain(pic,6)
      fr=Image.new("RGB",(W,H),(0,0,0)); fr.paste(pic,(0,TOP))
      if k=="p5":
        d=ImageDraw.Draw(fr); al=ease((t-17.7)/0.8)
        if al>0:
          # soft dark band for legibility
          yy=np.arange(H)[:,None]; band=np.exp(-((yy-(H/2-12))/120.0)**2)*0.55*al
          a=np.asarray(fr).astype(np.float32); a=a*(1-band[...,None])+np.array([4,10,28],np.float32)*band[...,None]
          fr=Image.fromarray(a.clip(0,255).astype(np.uint8)); d=ImageDraw.Draw(fr)
          text_c(d,H/2-40,"設計は、手から始まった。",jpL,tuple(int(245*al) for _ in range(3)))
          text_c(d,TOP+AH+48,"Design began with the hand.",en,tuple(int(200*al) for _ in range(3)))
      fo=max(0,(t-19.4)/0.6)
      if fo>0: fr=Image.blend(fr,Image.new("RGB",(W,H),(0,0,0)),min(1,fo))
      return fr
  return Image.new("RGB",(W,H),(0,0,0))
N=int(DUR*FPS)
for n in range(N):
  t=n/FPS
  fr=title_frame(t) if t<5.6 else shot_frame(t)
  fr.save(f"{OUT}/frames/f{n:04d}.jpg",quality=92)
# --- 仮の音：鉛筆の擦れ（帯域ノイズ）＋最後に低い持続音 ---
SR=48000; L=int(SR*DUR); y=np.zeros(L)
def bp_noise(n):
  x=rng.normal(0,1,n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR)
  X*=((f>1800)&(f<7000))*1.0; return np.fft.irfft(X,n)
def stroke(t0,dur,amp):
  n=int(dur*SR); i=int(t0*SR); env=np.sin(np.linspace(0,math.pi,n))**0.6*(0.7+0.3*np.sin(np.linspace(0,30,n)))
  seg=bp_noise(n)*env*amp; y[i:i+n]+=seg[:max(0,min(n,L-i))]
for t0,dd in [(0.3,0.35),(0.75,0.25),(1.05,0.4),(5.6,0.3),(6.0,0.45),(6.6,0.3),(11.4,0.25),(11.8,0.3)]: stroke(t0,dd,0.05)
tt=np.arange(L)/SR
pad=(np.sin(2*math.pi*55*tt)+0.5*np.sin(2*math.pi*82.5*tt)+0.3*np.sin(2*math.pi*110*tt))*0.05
penv=np.clip((tt-16.8)/1.2,0,1)*np.clip((20-tt)/0.8,0,1); y+=pad*penv
room=rng.normal(0,0.002,L); y+=room
y=np.clip(y,-1,1); pcm=(y*32767).astype(np.int16)
with wave.open(OUT+"/audio.wav","wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("frames",N)
