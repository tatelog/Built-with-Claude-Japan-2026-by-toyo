# v5 の編集データ（編集ページと同じ形）を段階ごとに書き出す
import json, sys
OUT = sys.argv[1]
CAM = {
 "lock":{"z0":1,"z1":1,"x0":0,"x1":0,"y0":0,"y1":0,"rot0":0,"rot1":0},
 "est":{"z0":1,"z1":1.06,"x0":0,"x1":0,"y0":0,"y1":0,"rot0":0,"rot1":0,"ease":"inout"},
 "dollyin":{"z0":1,"z1":1.25,"x0":0,"x1":0,"y0":0,"y1":0,"rot0":0,"rot1":0,"ease":"inout"},
 "dollyout":{"z0":1.6,"z1":1,"x0":0,"x1":0,"y0":0,"y1":0,"rot0":0,"rot1":0,"ease":"out"},
 "pedestal":{"z0":1.3,"z1":1.3,"x0":0,"x1":0,"y0":-0.8,"y1":0.8,"rot0":0,"rot1":0,"ease":"inout"},
 "truck":{"z0":1.3,"z1":1.3,"x0":-0.8,"x1":0.8,"y0":0,"y1":0,"rot0":0,"rot1":0,"ease":"inout"},
 "barrel":{"z0":1.35,"z1":1.35,"x0":0,"x1":0,"y0":0,"y1":0,"rot0":-8,"rot1":8,"ease":"inout"},
 "fly":{"z0":1,"z1":2.6,"x0":0,"x1":0,"y0":0,"y1":0,"rot0":0,"rot1":0,"ease":"in"},
}
n=[0]
def img(a,title,cam,dur,mono=True,ja="",en="",trans="cut"):
  n[0]+=1; c={"id":f"v5c{n[0]}","kind":"image","img":a,"title":title,"dur":dur,"mono":mono,"cam":cam,"ms":0,"me":1,"trans":trans,"textJa":ja,"textEn":en}; c.update(CAM[cam]); return c
def text(ja,dur,bg="black",typing=True,en=""):
  n[0]+=1; return {"id":f"v5c{n[0]}","kind":"text","textJa":ja,"textEn":en,"bg":bg,"typing":typing,"dur":dur,"trans":"cut"}
A={ "tools":"2f4d794e124cc14dd4793d83f0188638","p18":"a35810047d184de6ad6fc13b5eb3fd2a","room":"2786ed7029631a2a89401386d353a21d",
 "sagrada":"8e59705e76c8241a198518f194a2385a","p20":"026f01650cda728753ad2f982482ca7b","garnier":"9de93009f60ba84c6d2bdad64a07bb30",
 "crystal":"7c664412b77a2101dc94129f4542ca2e","p23":"7c68f112b565d6db57e44c1097d5286b","plan":"d51bd49bc22df4dcd044f32dbfbd2aed",
 "scott":"bda5588a34c821c813ce9b37489e25f7","notre":"906383b0222f0471cb5b4a192f9e68e3","taj":"ccceb737c744d972f4bba4840ce09786",
 "arc":"06c1807bfaba9c407a361808d71dcbec","d55":"193a65afdc8d29fef1535ea61866f424","d61":"5c36c4dd24c1880dc50e60535cdc73a3",
 "d7":"4b7b3f9ab333ff9aec561a59f13d6861","d25":"4417416f165c370f38b81d35e930877e","d26":"5574427bebcbf5dbb7f6b010a2aef49b",
 "d27":"710aeaa86b7f9d35b96edc88d8d2368d","d23":"9397732558e2a2162a3e2cdfa1d1ccd0","d28":"28471acb906178da56a2bace1e7fce0b"}
SEG="83cdce17c35769f2b4c0e64d1ba2af38"
steps=[]
clips=[]
log=[]
def L(t): log.append({"at":"2026-10-31T23:2%d:00.000Z"%min(9,len(log)),"by":"Claude","text":t})
def snap(): steps.append(json.loads(json.dumps({"title":"冒頭 v5","aspect":"scope","clips":clips,"audio":audio,"log":log})))
audio=[]
L("v5 の編集を作成。v4 の流れを、編集ページの部品で組み直す"); snap()
clips+= [text(".dwg",1.3), text("Drawing\n図面",2.4)]
L("タイトル：文字カード2枚（.dwg → Drawing／図面）をタイプライター表示で"); snap()
mon=[("tools","製図器具","dollyin"),("p18","帝国図書館の青焼き","truck",False),("room","九州帝大 製図室（寄り）","dollyout"),("sagrada","サグラダ・ファミリア 1905","pedestal"),
     ("p20","青焼きの断面","dollyin",False),("garnier","ガルニエの製図室","truck"),("crystal","水晶宮の作業場","barrel"),("p23","青焼きの平面","fly",False),
     ("plan","九州帝大 医学部平面図","pedestal"),("scott","建設中のスコット記念塔 1844","dollyin"),("notre","ノートルダム大聖堂","truck")]
for i,m in enumerate(mon):
  clips.append(img(A[m[0]],m[1],m[2],[0.62,0.6,0.58,0.56,0.54,0.52,0.5,0.48,0.46,0.45,0.45][i],mono=(m[3] if len(m)>3 else True)))
clips.append(img(A["room"],"九州帝大 製図室（引き）","est",1.3))
L("手の時代のモンタージュ：12カット。0.62秒から0.45秒へ少しずつ速く。カメラワークを1カットずつ変える"); snap()
n[0]+=1; clips.append({"id":f"v5c{n[0]}","kind":"video","asset":SEG,"title":"デジタイザ〜CAD（v4 の部品）","dur":11.6,"in":0,"speed":1,"trans":"cut","z0":1,"z1":1,"x0":0,"x1":0,"y0":0,"y1":0,"rot0":0,"rot1":0,"textJa":"","textEn":""})
L("デジタイザ〜CAD の部品動画（11.6秒）を挿入"); snap()
start_seg=sum(c["dur"] for c in clips[:-1])
audio.append({"id":"v5a1","asset":SEG,"name":"「デジタイザ〜CAD」の音（動画から分離）","start":round(start_seg,2),"in":0,"len":11.6,"vol":0.9})
L("部品動画の音を音トラックに分離して配置"); snap()
ph=[("taj","タージ・マハル","pedestal",True,0.5),("arc","凱旋門","dollyin",True,0.48),("d55","銀座のビル街 1930","truck",True,0.46),("d61","銀座の二大デパート","pedestal",True,0.44),
    ("d7","丸の内の街並み（カラー）","dollyout",False,0.44),("d25","空から見た東京駅（カラー）","fly",False,0.42),("d26","空から見た日本橋（カラー）","barrel",False,0.4),
    ("d27","隅田川の橋（カラー）","truck",False,0.38),("d23","夜の銀座（カラー）","dollyin",False,0.38),("d28","夜の鉄橋","est",False,1.4)]
for k,(a,t,cm,mono,d) in enumerate(ph): clips.append(img(A[a],t,cm,d,mono=mono,trans="fade" if k==len(ph)-1 else "cut"))
L("写真の流れ：白黒の世界の建築 → 昭和初期の東京（白黒 → カラー）。後ろほど速く、最後は夜の鉄橋をふわっと"); snap()
clips.append(text("現代の現場\n（代表の写真に差し替え予定）",1.6,bg="blue",typing=False))
L("現代の差し替え枠（文字カード）を末尾に"); snap()
json.dump(steps,open(OUT,"w"),ensure_ascii=False)
print(len(steps), "total", round(sum(c["dur"] for c in clips),2))
