from pathlib import Path
import base64,hashlib,shutil,subprocess,urllib.request

def download(url,path,sha):
 urllib.request.urlretrieve(url,path)
 if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha: raise RuntimeError('Checksum mismatch: '+path)
def run(*args):subprocess.run(args,check=True)
download('https://github.com/Malayalihere77/app-updates/releases/download/v15/MALAYALI-time-fixer-v15.apk','base.apk','d6ff8a69a51129f51b52c169c897beace04a19a9af1624f78c6f8b70c85cbaa7')
download('https://github.com/iBotPeaches/Apktool/releases/download/v2.11.1/apktool_2.11.1.jar','apktool.jar','56d59c524fc764263ba8d345754d8daf55b1887818b15cd3b594f555d249e2db')
download('https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar','signer.jar','e1299fd6fcf4da527dd53735b56127e8ea922a321128123b9c32d619bba1d835')
run('java','-jar','apktool.jar','d','-f','-s','base.apk','-o','decoded')
shutil.copytree('build-patch/res','decoded/res',dirs_exist_ok=True)
Path('decoded/classes3.dex').write_bytes(base64.b64decode(Path('build-patch/updater.dex.b64').read_text()))
p=Path('decoded/apktool.yml');p.write_text(p.read_text().replace('versionCode: 65','versionCode: 67').replace('4.0.2-malayali.15','4.0.2-malayali.17'))
run('java','-jar','apktool.jar','b','decoded','-o','v17-unsigned.apk')
run('java','-jar','signer.jar','--apks','v17-unsigned.apk','--out','signed')
shutil.copyfile('signed/v17-aligned-debugSigned.apk','MALAYALI-time-fixer-v17.apk')
