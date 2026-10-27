import json, sys
keep = ['id','title','upload_date','duration','view_count','like_count','comment_count','tags','categories',
        'chapters','channel','channel_id','channel_follower_count','language','description','thumbnail','live_status','availability']
raw = sys.stdin.read().strip()
if raw:
    d = json.loads(raw.splitlines()[0])
    out = {k: d.get(k) for k in keep}
    out['has_manual_subs'] = list((d.get('subtitles') or {}).keys())
    out['auto_caption_langs_orig'] = [k for k in (d.get('automatic_captions') or {}) if k.endswith('-orig')]
    out['audio_tracks'] = sorted({f.get('language') for f in d.get('formats', []) if f.get('acodec') not in (None, 'none') and f.get('language')})
    print(json.dumps(out, ensure_ascii=False))
