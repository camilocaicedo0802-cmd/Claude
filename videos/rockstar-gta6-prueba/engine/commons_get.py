import sys, hashlib, requests, os, time, urllib.parse
UA={"User-Agent":"RockstarDocEditor/1.0 (camilocaicedo0802@gmail.com) requests"}
outdir=sys.argv[1]
for spec in sys.argv[2:]:
    name, _, width = spec.partition("@")
    fn=name.replace(" ","_")
    h=hashlib.md5(fn.encode()).hexdigest()
    q=urllib.parse.quote(fn)
    if width:
        ext = ".png" if fn.lower().endswith(".svg") else ""
        url=f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}{ext}"
    else:
        url=f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"
    r=requests.get(url,headers=UA,timeout=60)
    local=os.path.join(outdir, fn if not width else f"{width}px-{fn}"+(".png" if fn.lower().endswith(".svg") else ""))
    if r.status_code==200:
        open(local,"wb").write(r.content); print("OK",len(r.content),local)
    else: print("FAIL",r.status_code,url)
    time.sleep(1)
