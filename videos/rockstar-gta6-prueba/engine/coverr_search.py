import sys, re, json, time, requests, os, urllib.parse
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
out_path=sys.argv[1]
db=json.load(open(out_path)) if os.path.exists(out_path) else {}
for q in sys.argv[2:]:
    if q in db: continue
    r=requests.get("https://coverr.co/s?q="+urllib.parse.quote(q),headers=UA,timeout=60)
    res=[]
    for ch in r.text.split('<coverr-video class="coverr-video"')[1:]:
        ch=ch[:ch.find('</coverr-video>')]
        t=re.search(r'title="([^"]+)"',ch); m=re.search(r'https://cdn\.coverr\.co/videos/([^"/]+)/',ch)
        if not t or not m: continue
        prem=bool(re.search(r'class="[^"]*premium',ch))
        ai=m.group(1).startswith('user-ai') or 'AI Generated' in ch
        res.append({"slug":m.group(1),"title":t.group(1),"premium":prem,"ai":ai})
    db[q]=res
    print(q,len(res),sum(1 for x in res if not x['premium'] and not x['ai']),flush=True)
    time.sleep(1.0)
json.dump(db,open(out_path,"w"),indent=0)
