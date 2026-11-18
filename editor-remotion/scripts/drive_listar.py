#!/usr/bin/env python3
"""Lista recursivamente una carpeta pública de Google Drive (vista embebida) -> TSV: id, tipo, ruta."""
import sys, re, html, subprocess, time
def fetch(fid):
    for i in range(4):
        r = subprocess.run(["curl", "-sS", "-L", "--fail", f"https://drive.google.com/embeddedfolderview?id={fid}"],
                           capture_output=True, text=True)
        if r.returncode == 0 and "flip-entry" in r.stdout or "flip-entries" in r.stdout: return r.stdout
        time.sleep(2 + i * 2)
    return r.stdout
def walk(fid, path, out, depth=0):
    page = fetch(fid)
    entries = re.findall(r'<div class="flip-entry" id="entry-([^"]+)".*?<a href="([^"]+)".*?<div class="flip-entry-title">(.*?)</div>', page, flags=re.S)
    for eid, href, title in entries:
        name = html.unescape(title).strip()
        if "/drive/folders/" in href or "folderview" in href:
            out.append((eid, "carpeta", f"{path}/{name}"))
            if depth < 4: walk(eid, f"{path}/{name}", out, depth + 1)
        else:
            out.append((eid, "archivo", f"{path}/{name}"))
root, label, dest = sys.argv[1], sys.argv[2], sys.argv[3]
out = []; walk(root, label, out)
with open(dest, "w") as f:
    for row in out: f.write("\t".join(row) + "\n")
print(dest, "entradas:", len(out), "archivos:", sum(1 for r in out if r[1] == "archivo"))
