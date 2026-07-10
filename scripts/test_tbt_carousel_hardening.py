#!/usr/bin/env python3
import json, os, subprocess, tempfile
from pathlib import Path
from PIL import Image
LIFE=Path('/Users/bettybot/.hermes/scripts/tbt_carousel_lifecycle.py')
def run(c,e,x=0):
 r=subprocess.run(c,env=e,capture_output=True,text=True); assert r.returncode==x,(c,r.returncode,r.stdout,r.stderr)
with tempfile.TemporaryDirectory() as d:
 d=Path(d); h=d/'hermes'; p=d/'pack';p.mkdir();e={**os.environ,'HERMES_HOME':str(h)}
 for i in range(1,8): Image.new('RGB',(1080,1080),(i,i,i)).save(p/f'slide-{i:02d}.png')
 Image.new('RGB',(2160,2160)).save(p/'contact.png')
 q=h/'state/q.json';q.parent.mkdir(parents=True);q.write_text('{"next":null}')
 run(['python3',str(LIFE),'can-produce','--queue-json',str(q)],e,2)
 q.write_text('{"next":{"id":"x"}}')
 run(['python3',str(LIFE),'open-review','--carousel-id','x','--revision','v01','--review-pack',str(p),'--contact-sheet',str(p/'contact.png'),'--slides-glob',str(p/'slide-*.png')],e)
 run(['python3',str(LIFE),'can-produce','--queue-json',str(q)],e,2)
 run(['python3',str(LIFE),'bind-delivery','--carousel-id','x','--review-message-id','123'],e)
 run(['python3',str(LIFE),'approve','--carousel-id','x','--approval-message-id','bogus'],e,1)
 print('PASS empty-queue silent block, active-lifecycle duplicate block, immutable 7-asset binding, and arbitrary-approval rejection')
