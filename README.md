# MALAYALI time fixer updates

Publish a stable GitHub Release containing exactly one APK. The workflow reads its internal version, verifies the signing certificate, generates update.json and publishes the download website.

One-time Pages setting: Settings → Pages → Source → GitHub Actions.

V17 migrates update checks to https://aswinc7271.github.io/app-update/update.json. Users of V15/V16 must install V17 once manually because those builds check the previous repository.

Each future APK must keep package app.greyshirts.firewall, the same signing certificate, a higher versionCode and versionName 4.0.2-malayali.N.

The initial workflow builds V17 from the published V15 APK and the checked-in resource/updater patch. Tool and base APK downloads are SHA256 checked. Existing debug signing identity is preserved for compatibility. Android installation requires user confirmation. No device runtime test has been performed.
