import pathlib
ROOT=str(pathlib.Path(__file__).resolve().parent.parent)
URL=pathlib.Path(ROOT,'index.html').as_uri()
import os
CHROME=os.environ.get("CHROME") or None
import json
from playwright.sync_api import sync_playwright
errs=[]
def J(pg,s): return json.loads(pg.evaluate("JSON.stringify("+s+")"))
STAGE = """(()=>{const G=DINO.G, done={}; let t=0;
const byId=i=>G.dinos.find(d=>d.id==i);
const A=(k,i,c)=>{ if(done[k]) return; const d=byId(i); if(d&&c(d)&&DINO.assign(d,k)) done[k]=G.tick; };
while(t++<1400){ DINO.update();
  A('build',1,d=>d.st=='walk'&&d.x>=318);
  A('glide',2,d=>true);
  A('bash',6,d=>d.st=='walk'&&d.x>=184);
  A('dig',7,d=>d.st=='walk'&&d.x>=140);
  A('climb',8,d=>true);
  A('block',10,d=>d.st=='walk'&&d.x>=60);
  if(done.build&&G.tick>done.build+%d) break; }
return {done, tick:G.tick, ds:G.dinos.map(d=>[d.id,d.x,d.y,d.st,d.glider?'G':'',d.climber?'C':''])};})()"""
with sync_playwright() as p:
  b=p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
  pg=b.new_page(viewport={"width":1440,"height":810})
  pg.on("console",lambda m: errs.append(m.type+": "+m.text) if m.type in("error","warning") else None)
  pg.on("pageerror",lambda e: errs.append("pageerror: "+str(e)))
  pg.goto(URL); pg.wait_for_timeout(800)
  pg.keyboard.press("1"); pg.wait_for_timeout(100)
  pg.evaluate("DINO.G.paused=true; DINO.G.banner=0")
  r=pg.evaluate(STAGE % int(__import__('sys').argv[1])); print(r)
  print(pg.evaluate("(()=>{const d=DINO.G.dinos.find(d=>d.id==9); const ok=DINO.assign(d,'climb'); for(let i=0;i<10;i++) DINO.update(); return [ok,d.st,d.x,d.y]})()"))
  pg.evaluate("DINO.G.T.flush(); DINO.G.toast=null")
  d=J(pg,"DINO.G.dinos.find(d=>d.st=='bash')||DINO.G.dinos[0]")
  x,y=J(pg,f"DINO.toClient({d['x']-5},{d['y']-14})"); pg.mouse.move(x,y); pg.mouse.move(x+1,y)
  pg.evaluate("DINO.G.paused=false; DINO.G.ff=false")
  pg.evaluate("DINO.G.paused=true; DINO.G.ui&=~16; DINO.render()")
  pg.evaluate("DINO.G.paused=false")
  pg.screenshot(path=ROOT+"/screenshots/gameplay.png")
  print(errs)
  b.close()
