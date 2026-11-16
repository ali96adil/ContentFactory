import concurrent.futures, json, urllib.request
repos = [
 "OHF-Voice/piper1-gpl","KittenML/KittenTTS","SWivid/Habibi-TTS","inkscape/inkscape",
 "blender/blender","motion-canvas/motion-canvas","remotion-dev/remotion","adbar/trafilatura",
 "openclaw-easy/ViralMint","OpenMontageInc/OpenMontage","n8n-io/n8n","PrefectHQ/prefect",
 "restic/restic","FFmpeg/FFmpeg","harry0703/MoneyPrinterTurbo","wj-sidiss/otopilot"
]
def get(url):
    try:
        req=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","User-Agent":"contentfactory-qualification"})
        with urllib.request.urlopen(req,timeout=12) as response:
            return json.load(response)
    except Exception as exc:
        return {"error":str(exc)}
def check(repo):
    root="https://api.github.com/repos/"+repo
    meta=get(root)
    branch=meta.get("default_branch")
    release=get(root+"/releases/latest")
    head=get(root+"/commits/"+branch) if branch else {}
    return dict(repo=repo, repository_error=meta.get("error"), license=(meta.get("license") or {}).get("spdx_id"),
                pushed_at=meta.get("pushed_at"), head=head.get("sha"), head_error=head.get("error"),
                release=release.get("tag_name"), release_error=release.get("error"),
                release_date=release.get("published_at"))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    print(json.dumps(list(pool.map(check,repos)),indent=2))
