#!/usr/bin/env python3
"""Fixes the Record button in the arc42 slides page.

Usage:  python3 apply-recording-fix.py slides.html
Writes: slides.fixed.html  (your original is left untouched)

What it fixes
1. Blank screen: the <body> got the class "rec", which also matched the REC badge
   rule (.rec{display:none}), so the whole page was hidden. The badge is now
   .recb and the body state class is "recording".
2. Leaving full screen: Chrome exits full screen when the screen-share picker
   opens. The fix returns to full screen once recording starts, or shows a
   one-click prompt if the browser refuses.
3. Also: records only the slide area where the browser supports Region Capture,
   keeps recording if you switch tabs, stops cleanly when you press "Stop
   sharing", records without narration if the microphone is blocked, and
   releases the camera and screen after stopping.
"""
import re, sys

JS = r"""var rcd=null,rch=[],rst=null,rsrc=[],rac=null,rwasFs=false,rbusy=false;
function fsAsk(on){var el=document.getElementById("fsask");el.style.display=on?"block":"none";if(!on)return;
var h=function(){document.removeEventListener("pointerdown",h,true);document.removeEventListener("keydown",h,true);el.style.display="none";document.documentElement.requestFullscreen().then(function(){if(navigator.wakeLock)navigator.wakeLock.request("screen").then(function(w){wl=w}).catch(function(){})}).catch(function(){})};
document.addEventListener("pointerdown",h,true);document.addEventListener("keydown",h,true)}
function recUI(on){document.body.classList.toggle("recording",on);if(!on)document.body.classList.remove("idle");document.getElementById("b-rec").textContent=on?"Stop recording (R)":"Record (R)"}
async function recStart(){
  if(rbusy)return;rbusy=true;
  try{
    rwasFs=!!document.fullscreenElement;
    var ds=null,ms=null;
    try{ds=await navigator.mediaDevices.getDisplayMedia({video:{frameRate:30},audio:true,preferCurrentTab:true,selfBrowserSurface:"include",surfaceSwitching:"exclude"})}
    catch(e){console.warn("Screen capture cancelled:",e);return}
    var vt=ds.getVideoTracks()[0];
    try{if(window.CropTarget&&vt.cropTo&&vt.getSettings().displaySurface==="browser"){await vt.cropTo(await CropTarget.fromElement(document.getElementById("stage")))}}
    catch(e){console.warn("Recording the whole tab (region capture unavailable):",e)}
    try{ms=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true,channelCount:1}})}
    catch(e){console.warn("No microphone: recording without narration",e)}
    rac=new AudioContext();try{await rac.resume()}catch(e){}
    var dst=rac.createMediaStreamDestination();
    if(ms)rac.createMediaStreamSource(ms).connect(dst);
    if(ds.getAudioTracks().length)rac.createMediaStreamSource(new MediaStream(ds.getAudioTracks())).connect(dst);
    rsrc=[ds,ms];
    rst=new MediaStream([vt].concat(dst.stream.getAudioTracks()));
    var mt=['video/mp4;codecs=avc1,mp4a.40.2','video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus','video/webm'].find(function(t){return MediaRecorder.isTypeSupported(t)});
    rch=[];
    rcd=mt?new MediaRecorder(rst,{mimeType:mt,videoBitsPerSecond:3000000,audioBitsPerSecond:64000}):new MediaRecorder(rst);
    rcd.ondataavailable=function(e){if(e.data&&e.data.size)rch.push(e.data)};
    rcd.onstop=function(){
      var type=rcd.mimeType||mt||"video/webm",b=new Blob(rch,{type:type}),u=URL.createObjectURL(b),a=document.createElement("a");
      a.href=u;a.download="arc42-"+Date.now()+(type.indexOf("mp4")>-1?".mp4":".webm");document.body.appendChild(a);a.click();a.remove();
      setTimeout(function(){URL.revokeObjectURL(u)},10000);rch=[];
      rsrc.forEach(function(s){if(s)s.getTracks().forEach(function(t){t.stop()})});rsrc=[];
      if(rac){rac.close();rac=null}
      fsAsk(false);recUI(false);rcd=null};
    vt.onended=function(){recStop()};
    rcd.start(1000);
    recUI(true);
    if(rwasFs&&!document.fullscreenElement){try{await document.documentElement.requestFullscreen()}catch(e){fsAsk(true)}}
    if(document.fullscreenElement)document.body.classList.add("idle");
  }finally{rbusy=false}
}
function recStop(){if(rcd&&rcd.state!=="inactive")rcd.stop()}
function recToggle(){document.body.classList.contains("recording")?recStop():recStart()}"""

CSS_NEW = ('.recb{position:fixed;top:14px;left:18px;z-index:9;display:none;align-items:center;gap:8px;background:#c0392b;color:#fff;'
 'font:800 20px "Bricolage Grotesque",sans-serif;padding:6px 14px;border-radius:8px}body.recording .recb{display:flex}'
 '.recb i{width:12px;height:12px;background:#fff;border-radius:50%;animation:blink 1s infinite}@keyframes blink{50%{opacity:.2}}'
 '#fsask{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:9;display:none;background:#f2b631;color:#0b1721;'
 'font:600 18px system-ui,sans-serif;padding:8px 18px;border-radius:8px}')

def must(pattern, repl, s, flags=0, label=""):
    new, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if n != 1:
        sys.exit("Could not find: " + label + ". The file may already be fixed or edited.")
    return new

def main(path):
    s = open(path, encoding="utf-8").read()
    s = must(r'\.rec\{position:fixed;top:14px;left:18px;[^}]*\}body\.rec \.rec\{display:flex\}\.rec i\{[^}]*\}@keyframes blink\{50%\{opacity:\.2\}\}', CSS_NEW, s, label="REC badge CSS")
    s = must(r'#cd,\.rec\{display:none!important\}', '#cd,.recb,#fsask{display:none!important}', s, label="print rule")
    s = must(r'<div class="rec"><i></i>REC</div>', '<div class="recb"><i></i>REC</div>\n<div id="fsask">Recording. Click or press any key to return to full screen.</div>', s, label="REC badge element")
    s = must(r'function fit\(\)\{var s=', 'function fit(){if(!innerWidth||!innerHeight)return;var s=', s, label="fit()")
    s = must(r'var rcd=null,rch=\[\],rst=null;.*?document\.addEventListener\("visibilitychange",function\(\)\{if\(document\.hidden&&rcd&&rcd\.state==="recording"\)recStop\(\)\}\);', JS, s, flags=re.S, label="recording code")
    out = re.sub(r'\.html$', '', path) + ".fixed.html"
    open(out, "w", encoding="utf-8").write(s)
    print("Wrote", out)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
