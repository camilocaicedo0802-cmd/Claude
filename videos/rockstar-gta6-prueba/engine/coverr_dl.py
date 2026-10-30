import json, sys, os, requests, concurrent.futures as cf
S=sys.argv[1]
pick=json.load(open(f"{S}/assets/meta/coverr_pick.json")); idx=json.load(open(f"{S}/assets/meta/coverr_idx.json"))
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
def get(item):
    key,n=item; slug=idx[str(n)]; out=f"{S}/assets/coverr/{key}.mp4"
    if os.path.exists(out) and os.path.getsize(out)>100000: return key,"exists"
    for q in ("1080p","720p"):
        r=requests.get(f"https://cdn.coverr.co/videos/{slug}/{q}.mp4",headers=UA,timeout=180)
        if r.status_code==200 and len(r.content)>100000:
            open(out,"wb").write(r.content); return key,f"{q} {len(r.content)//1024}KB {slug}"
    return key,f"FAIL {r.status_code} {slug}"
with cf.ThreadPoolExecutor(4) as ex:
    for k,msg in ex.map(get,pick.items()): print(k,msg,flush=True)
