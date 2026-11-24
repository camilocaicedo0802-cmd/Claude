#!/bin/bash
# usage: hf.sh submit <endpoint> <json-file> <name>   -> prints request_id, saves <name>.req.json
#        hf.sh wait <name> [maxsec]                    -> polls status, downloads outputs to <name>_N.ext
#        hf.sh upload <file> <content-type>            -> prints public_url
set -e
API=https://api.higgsfield.ai
case "$1" in
  submit)
    IK=$(python3 -c 'import uuid;print(uuid.uuid4())')
    curl -sS --max-time 60 -X POST "$API/$2" -H 'Content-Type: application/json' -H "Idempotency-Key: $IK" -d @"$3" > "$4.req.json"
    python3 -c "import json;d=json.load(open('$4.req.json'));print(d.get('request_id') or d)";;
  wait)
    RID=$(python3 -c "import json;print(json.load(open('$2.req.json'))['request_id'])")
    MAX=${3:-600}; T=0
    while [ $T -lt $MAX ]; do
      curl -sS --max-time 30 "$API/requests/$RID/status" > "$2.status.json"
      ST=$(python3 -c "import json;print(json.load(open('$2.status.json'))['status'])")
      case "$ST" in completed|failed|nsfw|canceled) break;; esac
      sleep 8; T=$((T+8))
    done
    echo "$2: $ST"
    python3 - "$2" <<'PY'
import json,sys,subprocess
n=sys.argv[1]; d=json.load(open(n+'.status.json'))
urls=[]
if d.get('video'): urls.append(d['video']['url'])
for im in d.get('images') or []: urls.append(im['url'])
for v in d.get('videos') or []: urls.append(v['url'])
for i,u in enumerate(urls):
    ext=u.split('?')[0].rsplit('.',1)[-1][:4]
    out=f"{n}_{i}.{ext}"
    subprocess.run(['curl','-sSL','--max-time','300','-o',out,u],check=True); print(out)
if d['status']!='completed': print(json.dumps(d)[:600])
PY
    ;;
  upload)
    curl -sS -X POST "$API/files/generate-upload-url" -H 'Content-Type: application/json' -d "{\"content_type\":\"$3\"}" > up.json
    UURL=$(python3 -c "import json;print(json.load(open('up.json'))['upload_url'])")
    TAG=$(python3 -c "import json;print(json.load(open('up.json'))['upload_headers'].get('x-amz-tagging',''))")
    curl -sS -o /dev/null -w '%{http_code}' -X PUT "$UURL" -H "Content-Type: $3" -H "x-amz-tagging: $TAG" --upload-file "$2" | grep -q 200 && python3 -c "import json;print(json.load(open('up.json'))['public_url'])";;
esac
