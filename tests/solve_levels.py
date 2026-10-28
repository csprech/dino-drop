import pathlib
ROOT=str(pathlib.Path(__file__).resolve().parent.parent)
URL=pathlib.Path(ROOT,'index.html').as_uri()
import os
CHROME=os.environ.get("CHROME") or None
import json
from playwright.sync_api import sync_playwright
SOLVE = """((lvl)=>{const G=DINO.G; DINO.load('level',lvl); const used=[]; let t=0;
const once={};
const A=(key,k,c)=>{ if(once[key]) return; const d=G.dinos.find(d=>c(d)); if(d&&DINO.assign(d,k)){once[key]=1; used.push([key,d.id,d.x,d.y,G.tick]);} };
while(!G.result && t++<6000){ DINO.update();
 if(lvl==0){
  A('b1','build',d=>d.st=='walk'&&d.dir>0&&d.x>=318&&d.x<330);
  A('d1','dig',d=>d.st=='walk'&&d.dir>0&&d.x>=600&&d.x<615);
 } else {
  A('d1','dig',d=>d.st=='walk'&&d.dir>0&&d.x>=96&&d.x<104);
  A('b1','build',d=>d.st=='walk'&&d.dir>0&&d.x>=256&&d.x<262&&d.y>130);
  A('s1','bash',d=>d.st=='walk'&&d.x>=436&&d.x<446&&d.y>140&&d.dir>0);
 }}
return {res:G.result, used, tick:G.tick, left:G.dinos.map(d=>[d.x,d.y,d.st])};})"""
with sync_playwright() as p:
  b=p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
  pg=b.new_page(viewport={"width":1440,"height":810})
  pg.goto(URL); pg.wait_for_timeout(300)
  for l in (0,1):
    print(json.dumps(pg.evaluate(SOLVE+"(%d)"%l)))
  b.close()
