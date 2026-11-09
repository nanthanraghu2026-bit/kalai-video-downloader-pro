import time, uuid, threading, shutil
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, send_file, abort
import yt_dlp

BASE=Path(__file__).resolve().parent
OUT=BASE/"downloads"; OUT.mkdir(exist_ok=True)
app=Flask(__name__)
JOBS={}; LOCK=threading.Lock()
ALLOWED={"facebook.com","www.facebook.com","m.facebook.com","fb.watch","instagram.com","www.instagram.com"}

def valid_url(u):
    try:
        p=urlparse(u)
        return p.scheme in ("http","https") and (p.hostname or "").lower() in ALLOWED and len(u)<2048
    except Exception: return False

def run_job(jid,url,mode,quality):
    folder=OUT/jid; folder.mkdir(parents=True,exist_ok=True)
    def hook(d):
        with LOCK:
            j=JOBS.get(jid)
            if not j: return
            if d["status"]=="downloading":
                total=d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                j["progress"]=round(100*d.get("downloaded_bytes",0)/total,1) if total else 0
                j["speed"]=d.get("_speed_str","")
            elif d["status"]=="finished":
                j["progress"]=100; j["state"]="processing"
    opts={"outtmpl":str(folder/"%(title).90B_%(id)s.%(ext)s"),"noplaylist":True,
          "quiet":True,"no_warnings":True,"progress_hooks":[hook],"retries":2,
          "socket_timeout":20,"restrictfilenames":True,"max_filesize":300*1024*1024}
    if mode=="audio":
        opts.update(format="bestaudio/best",postprocessors=[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":quality}])
    else:
        opts.update(format="best[ext=mp4][height<=1080]/best[height<=1080]/best",merge_output_format="mp4")
    try:
        with yt_dlp.YoutubeDL(opts) as y: y.download([url])
        fs=[p for p in folder.iterdir() if p.is_file() and not p.name.endswith((".part",".ytdl"))]
        if not fs: raise RuntimeError("No output file was created.")
        f=max(fs,key=lambda p:p.stat().st_mtime)
        with LOCK: JOBS[jid].update(state="done",progress=100,filename=f.name)
    except Exception as e:
        with LOCK: JOBS[jid].update(state="error",error=str(e)[:300])

@app.route("/")
def home(): return render_template("index.html")
@app.route("/privacy.html")
def privacy(): return send_file(BASE/"privacy.html")
@app.route("/terms.html")
def terms(): return send_file(BASE/"terms.html")
@app.route("/api/jobs",methods=["POST"])
def create():
    d=request.get_json(silent=True) or {}; u=(d.get("url") or "").strip()
    mode=d.get("mode","video"); q=str(d.get("quality","192"))
    if not valid_url(u): return jsonify(error="Enter a public Facebook or Instagram URL."),400
    if mode not in ("video","audio") or q not in ("128","192","256","320"): return jsonify(error="Invalid option."),400
    jid=uuid.uuid4().hex
    with LOCK: JOBS[jid]={"state":"queued","progress":0,"speed":"","filename":"","error":"","created":time.time()}
    threading.Thread(target=run_job,args=(jid,u,mode,q),daemon=True).start()
    return jsonify(id=jid)
@app.route("/api/jobs/<jid>")
def status(jid):
    with LOCK:
        j=JOBS.get(jid)
        if not j or time.time()-j["created"]>3600:
            if j: shutil.rmtree(OUT/jid,ignore_errors=True); JOBS.pop(jid,None)
            return jsonify(error="Job expired."),404
        return jsonify({k:j[k] for k in ("state","progress","speed","filename","error")})
@app.route("/api/jobs/<jid>/file")
def get_file(jid):
    with LOCK:
        j=JOBS.get(jid)
        if not j or j["state"]!="done": abort(404)
        name=j["filename"]
    f=OUT/jid/name
    if not f.is_file(): abort(404)
    return send_file(f,as_attachment=True,download_name=name)
if __name__=="__main__": app.run(host="127.0.0.1",port=5000)
