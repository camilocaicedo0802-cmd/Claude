import re, sys, time, json, requests
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
out={}
for cat in sys.argv[2:]:
    r=requests.get(f"https://mixkit.co/free-sound-effects/{cat}/",headers=UA,timeout=30)
    if r.status_code!=200 or 'Just a moment' in r.text[:500]: print(cat,"BLOCKED",r.status_code); time.sleep(5); continue
    urls=re.findall(r'data-audio-player-preview-url-value="([^"]+)"',r.text)
    titles=re.findall(r'class="item-grid-card__title"[^>]*>\s*([^<]+?)\s*<',r.text)
    lic=set(re.findall(r'data-license="([a-zA-Z]+)"',r.text))
    out[cat]=[{"t":t,"u":u} for t,u in zip(titles,urls)]
    print("##",cat,lic," | ".join(f"{u.split('/')[-2]}:{t}" for t,u in zip(titles,urls)),flush=True)
    time.sleep(4)
json.dump(out,open(sys.argv[1],"w"),indent=0)
