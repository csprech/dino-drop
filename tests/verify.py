import pathlib
ROOT=str(pathlib.Path(__file__).resolve().parent.parent)
URL=pathlib.Path(ROOT,'index.html').as_uri()
import os
CHROME=os.environ.get("CHROME") or None
import json
from playwright.sync_api import sync_playwright
errs=[]; R={}
def J(pg,s): return json.loads(pg.evaluate("JSON.stringify("+s+")"))
with sync_playwright() as p:
  b=p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
  pg=b.new_page(viewport={"width":1440,"height":810})
  pg.on("console",lambda m: errs.append(m.type+": "+m.text) if m.type in("error","warning") else None)
  pg.on("pageerror",lambda e: errs.append("pageerror: "+str(e)))
  pg.goto(URL); pg.wait_for_timeout(2500)  # menu + demo running real-time
  R['demo_dinos']=pg.evaluate("DINO.G.dinos.length")
  # click "1 FIRST STEPS" menu button with the mouse
  x,y=J(pg,"DINO.toClient(DINO.G.cam+240,112)"); pg.mouse.click(x,y); pg.wait_for_timeout(100)
  R['after_menu_click']=J(pg,"[DINO.G.mode,DINO.G.kind,DINO.G.def.name]")
  pg.wait_for_timeout(3000)  # real time play
  R['realtime_spawned']=pg.evaluate("DINO.G.spawned")
  xs0=J(pg,"DINO.G.dinos.map(d=>d.x)"); pg.wait_for_timeout(500); xs1=J(pg,"DINO.G.dinos.map(d=>d.x)")
  R['walking_moved']=sum(1 for a,c in zip(xs0,xs1) if a!=c)
  pg.keyboard.press("p")
  def click_dino(i):
    d=J(pg,f"DINO.G.dinos[{i}]"); x,y=J(pg,f"DINO.toClient({d['x']},{d['y']-6})"); pg.mouse.click(x,y); return J(pg,f"DINO.G.dinos.find(q=>q.id=={d['id']})")
  # select DIG via HUD button click
  x,y=J(pg,"DINO.toClient(DINO.G.cam+2*30+15,240)"); pg.mouse.click(x,y)
  R['sel_after_btn']=pg.evaluate("DINO.G.sel")
  e0=pg.evaluate("DINO.count(1)"); dd=click_dino(0); pg.evaluate("DINO.step(40)")
  R['dig']=[dd['st'], e0-pg.evaluate("DINO.count(1)"), pg.evaluate("DINO.G.skills.dig")]
  pg.keyboard.press("3"); b0=pg.evaluate("DINO.count(3)")
  i=pg.evaluate("DINO.G.dinos.findIndex(d=>d.st=='walk')"); db=click_dino(i); pg.evaluate("DINO.step(60)")
  R['build']=[db['st'], pg.evaluate("DINO.count(3)")-b0]
  # fast-forward + restart buttons
  pg.keyboard.press("f"); R['ff']=pg.evaluate("DINO.G.ff"); pg.keyboard.press("f")
  # nuke: double click button
  x,y=J(pg,"DINO.toClient(DINO.G.cam+8*30+15,240)"); pg.mouse.click(x,y); pg.mouse.click(x,y)
  R['nuked']=pg.evaluate("DINO.G.nuked")
  pg.evaluate("DINO.step(400)"); R['result']=J(pg,"DINO.G.result")
  pg.evaluate("DINO.G.paused=false"); pg.wait_for_timeout(200); pg.screenshot(path="/tmp/result.png")
  pg.keyboard.press("r"); R['restart']=J(pg,"[DINO.G.result,DINO.G.spawned,DINO.G.tick<10]")
  pg.keyboard.press("Escape"); pg.keyboard.press("2"); pg.wait_for_timeout(100)
  pg.evaluate("DINO.G.paused=true"); pg.evaluate("DINO.step(400)")
  R['level2']=J(pg,"[DINO.G.def.name,DINO.G.spawned,DINO.G.dead,DINO.G.dinos.length]")
  pg.evaluate("DINO.G.paused=false; DINO.G.banner=0"); pg.wait_for_timeout(100); pg.screenshot(path="/tmp/level2.png")
  # ---- sandbox
  pg.keyboard.press("Escape"); pg.keyboard.press("s"); pg.wait_for_timeout(200)
  pg.evaluate("DINO.G.paused=true")
  e0=pg.evaluate("DINO.count(1)")
  x,y=J(pg,"DINO.toClient(DINO.G.cam+44,8)"); pg.mouse.click(x,y)  # DRAW button
  def drag(pts):
    x,y=J(pg,f"DINO.toClient(DINO.G.cam+{pts[0][0]},{pts[0][1]})"); pg.mouse.move(x,y); pg.mouse.down()
    for a,c in pts[1:]:
      x,y=J(pg,f"DINO.toClient(DINO.G.cam+{a},{c})"); pg.mouse.move(x,y,steps=8)
    pg.mouse.up()
  drag([(150,110),(190,104),(230,100),(270,104)])
  R['sandbox_draw_earth']=pg.evaluate("DINO.count(1)")-e0
  # size slider drag
  x,y=J(pg,"DINO.toClient(DINO.G.cam+160,8)"); pg.mouse.click(x,y); R['brush_after_slider']=pg.evaluate("DINO.G.brush")
  pg.keyboard.press("k"); r0=pg.evaluate("DINO.count(2)"); drag([(330,70),(360,60)]); R['rock_drawn']=pg.evaluate("DINO.count(2)")-r0
  pg.keyboard.press("e"); e1=pg.evaluate("DINO.count(1)"); drag([(400,176),(430,186)]); R['erased']=e1-pg.evaluate("DINO.count(1)")
  pg.keyboard.press("["); pg.keyboard.press("["); R["brush_after_keys"]=pg.evaluate("DINO.G.brush")
  pg.keyboard.press("g"); x,y=J(pg,"DINO.toClient(DINO.G.cam+200,60)"); pg.mouse.click(x,y); R['egg']=J(pg,"DINO.G.spawn")
  pg.keyboard.press("x"); x,y=J(pg,"DINO.toClient(DINO.G.cam+455,120)"); pg.mouse.click(x,y); R['cave']=J(pg,"DINO.G.exit")
  pg.keyboard.press("u"); R['unlimited_off']=J(pg,"[DINO.G.unlimited,DINO.G.skills.dig]"); pg.keyboard.press("u")
  pg.evaluate("DINO.step(330)")
  pg.evaluate("(()=>{const ws=DINO.G.dinos.filter(d=>d.st=='walk'); const k=['build','bash','dig','block','glide','climb']; ws.slice(0,6).forEach((d,i)=>DINO.assign(d,k[i]))})()")
  pg.evaluate("DINO.step(36)")
  R['sandbox_states']=J(pg,"DINO.G.dinos.map(d=>d.st)")
  pg.keyboard.press("b")
  x,y=J(pg,"DINO.toClient(DINO.G.cam+300,40)"); pg.mouse.move(x,y)
  pg.evaluate("DINO.G.paused=false; DINO.G.toast=null"); pg.evaluate("DINO.G.paused=true; DINO.G.ui&=~16; DINO.render()")
  pg.screenshot(path=ROOT+"/screenshots/sandbox.png")
  pg.evaluate("DINO.G.paused=false"); pg.wait_for_timeout(1500)
  print(json.dumps(R,indent=0)); print("ERRORS:",errs)
  b.close()
import sys; sys.exit(1 if errs else 0)
