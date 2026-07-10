from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import hashlib, json
from datetime import datetime, timezone

ROOT=Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/plan-you-never-wrote-down-2026-07')
OUT=ROOT/'v02-marcus-variety-review-pack'; OUT.mkdir(parents=True,exist_ok=True)
FONT={'xb':'/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Extrabold.ttf','bold':'/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Bold.ttf','reg':'/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Regular.ttf'}
LOGO='/Users/bettybot/clawd/TBT-logos/TBT Logo/White text/The better traders 1_text white.png'
BASES={
1:'/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_173335_acb3fd88.png',
2:'/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_173450_786655e9.png',
3:'/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_173559_8421af03.png',
4:'/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_173746_3ed6e43e.png',
5:'/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_174121_638f6088.png',
6:'/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_174230_77421c87.png',
7:'/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_174344_d798ae79.png'}
COPY={
1:('You Have a Plan\nIn Your Head','Marcus can explain every rule. But if it only lives in his head, it changes when the pressure does.',58),
2:('So You\nWing It','Without a written plan, every decision starts feeling urgent.',60),
3:('Then The\nMarket Moves','When the moment gets loud, memory is not a system.',60),
4:('And The Plan?\nGone','Nothing written down. Nothing solid to come back to.',56),
5:('That Is When\nIt Clicks','A real plan is decided before emotion gets a vote.',58),
6:('Write It Down.\nEvery Rule.','Entries. Risk. What invalidates the idea. Let calm Marcus make the call first.',54),
7:('The Plan You\nFinally Wrote','The Better Traders Journal turns a good intention into something you can follow.',58)}
WHITE=(246,248,251,255); BODY=(234,239,243,255); TEAL=(0,230,198,255)
def ft(n,k): return ImageFont.truetype(FONT[k],n)
def wrap(d,t,w,f):
 lines=[]
 for paragraph in t.split('\n'):
  cur=''
  for word in paragraph.split():
   candidate=(cur+' '+word).strip()
   if not cur or d.textbbox((0,0),candidate,font=f)[2]<=w: cur=candidate
   else: lines.append(cur); cur=word
  if cur: lines.append(cur)
 return lines
def text(d,t,x,y,w,f,fill,leading):
 for line in wrap(d,t,w,f):
  d.text((x+2,y+2),line,font=f,fill=(0,0,0,180)); d.text((x,y),line,font=f,fill=fill); y+=leading
 return y
def gradient(im):
 w,h=im.size; overlay=Image.new('RGBA',(w,h),(0,0,0,0)); p=overlay.load()
 if p is None: raise RuntimeError('could not access gradient pixels')
 for y in range(h):
  for x in range(w):
   a=min(238,int(215*max(0,1-x/680)+60*max(0,1-y/620)+90*max(0,(y-850)/230)))
   p[x,y]=(0,4,10,a)
 return Image.alpha_composite(im,overlay)
def nav(d,n):
 y=1018; d.text((70,y),f'{n:02d}',font=ft(18,'bold'),fill=TEAL)
 for i in range(7):
  x=540+(i-3)*22; d.ellipse((x-5,y+4,x+5,y+14),fill=TEAL if i==n-1 else WHITE)
 if n!=7: d.text((930,y),'Swipe ->',font=ft(18,'bold'),fill=TEAL)
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
exports=[]
for n in range(1,8):
 im=Image.open(BASES[n]).convert('RGB').resize((1080,1080),Image.Resampling.LANCZOS)
 im=ImageEnhance.Brightness(im).enhance(1.02).convert('RGBA'); im=gradient(im)
 if n in (1,7):
  logo=Image.open(LOGO).convert('RGBA'); logo=logo.resize((140,int(logo.height*140/logo.width)),Image.Resampling.LANCZOS); im.alpha_composite(logo,(54,56))
 d=ImageDraw.Draw(im); title,body,size=COPY[n]
 yy=text(d,title,70,166,650,ft(size,'xb'),WHITE,int(size*1.02)); yy+=22
 text(d,body,70,yy,635,ft(27,'reg'),BODY,33); nav(d,n)
 if n==7: d.text((70,1052),'Educational content only. Not financial advice.',font=ft(12,'reg'),fill=(210,220,225,230))
 p=OUT/f'tbt-plan-you-never-wrote-down-slide-{n:02d}-v02-review.png'; im.convert('RGB').save(p,quality=95); exports.append(p)
TW=360; GAP=34; LH=45
sheet=Image.new('RGB',(3*TW+4*GAP,3*(TW+LH)+4*GAP),(4,10,18)); d=ImageDraw.Draw(sheet)
for i,p in enumerate(exports):
 x=GAP+(i%3)*(TW+GAP); y=GAP+(i//3)*(TW+LH+GAP); sheet.paste(Image.open(p).resize((TW,TW),Image.Resampling.LANCZOS),(x,y)); d.text((x,y+TW+8),f'Slide {i+1:02d}',font=ft(26,'bold'),fill=WHITE)
contact=OUT/'tbt-plan-you-never-wrote-down-contact-sheet-v02-review.png'; sheet.save(contact,quality=95)
manifest={'carousel_id':'plan-you-never-wrote-down-2026-07','revision':'v02','title':'The Plan You Never Wrote Down','status':'REVIEW READY','review_only':True,'scheduled':False,'created_at':datetime.now(timezone.utc).isoformat(),'lead':'MARCUS','style_lock':'/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/','base_images':BASES,'slides':[{'path':str(p),'sha256':sha(p),'dimensions':Image.open(p).size} for p in exports],'contact_sheet':str(contact),'copy_gate':'Claude Worker creative direction used for slide-by-slide visual variance.','review_gate':'review-only; Aaron feedback/approval required.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(contact)
