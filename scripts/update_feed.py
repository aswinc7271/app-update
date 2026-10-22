import hashlib, json, os, re, tempfile, urllib.request
from pathlib import Path
from androguard.core.apk import APK

repo = os.environ['GH_REPO']
if repo.lower() != 'aswinc7271/app-update':
    raise RuntimeError('This package is configured for aswinc7271/app-update')
headers = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
request = urllib.request.Request('https://api.github.com/repos/' + repo + '/releases/latest', headers=headers)
with urllib.request.urlopen(request, timeout=30) as response:
    release = json.load(response)
assets = [a for a in release['assets'] if a['name'].lower().endswith('.apk')]
if len(assets) != 1:
    raise RuntimeError('Latest stable release must contain exactly one APK')
asset = assets[0]
url = asset['browser_download_url']
if not url.startswith('https://github.com/' + repo + '/releases/download/'):
    raise RuntimeError('Unexpected download URL')
if not 0 < asset['size'] <= 100 * 1024 * 1024:
    raise RuntimeError('APK size must be below 100 MB')
with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / 'release.apk'
    # Public download: do not forward GitHub token to redirected asset hosts.
    with urllib.request.urlopen(url, timeout=60) as response, path.open('wb') as output:
        total = 0
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > 100 * 1024 * 1024:
                raise RuntimeError('APK download exceeds limit')
            output.write(chunk)
    if total != asset['size']:
        raise RuntimeError('Incomplete APK download')
    apk = APK(str(path))
    if apk.get_package() != 'app.greyshirts.firewall':
        raise RuntimeError('Wrong APK package')
    code = int(apk.get_androidversion_code())
    name = apk.get_androidversion_name()
    match = re.fullmatch(r'4\.0\.2-malayali\.(\d+)', name)
    if not match:
        raise RuntimeError('Expected versionName 4.0.2-malayali.N')
    certs = apk.get_certificates()
    expected = '1e08a903aef9c3a721510b64ec764d01d3d094eb954161b62544ea8f187b5953'
    if not certs or any(hashlib.sha256(c.dump()).hexdigest() != expected for c in certs):
        raise RuntimeError('APK signing certificate differs from existing app')
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    previous = Path('update.json')
    if previous.exists():
        old = json.loads(previous.read_text())
        if code < old['versionCode'] or (code == old['versionCode'] and sha != old.get('sha256')):
            raise RuntimeError('New APK requires a higher versionCode')
    notes = (release.get('body') or 'New app update available.')[:3500]
    data = dict(schemaVersion=1, versionCode=code, versionName=name,
                releaseNumber=int(match[1]), releasedAt=release['published_at'][:10],
                apkUrl=url, sizeBytes=total, sha256=sha, notes=notes,
                changes=[line.strip('- *\r ') for line in notes.splitlines() if line.strip()][:12])
    previous.write_text(json.dumps(data, indent=2) + '\n')
    print('Generated update.json for ' + name)
