# macOS 签名与公证说明

macOS 的正式发布包必须使用 Apple Developer ID 证书签名，并通过 Apple notarization。
未公证的 `.dmg` 通过浏览器下载后，Gatekeeper 可能提示“已损坏，无法打开”。

## GitHub Secrets

发布 `v*` 标签前，需要在 GitHub 仓库中配置以下 secrets：

- `MACOS_CERTIFICATE_P12`：Developer ID Application 证书的 `.p12` 文件，base64 编码后写入。
- `MACOS_CERTIFICATE_PASSWORD`：`.p12` 证书导出密码。
- `MACOS_CODESIGN_IDENTITY`：签名身份，例如 `Developer ID Application: Name (TEAMID)`。
- `MACOS_NOTARY_KEY_ID`：App Store Connect API Key ID。
- `MACOS_NOTARY_ISSUER_ID`：App Store Connect Issuer ID。
- `MACOS_NOTARY_KEY_P8_BASE64`：`AuthKey_XXXX.p8` 文件，base64 编码后写入。

## 生成 base64

```bash
base64 -i DeveloperIDApplication.p12 | pbcopy
base64 -i AuthKey_XXXXXXXXXX.p8 | pbcopy
```

## 发布行为

`Release` workflow 在 tag 发布时会强制检查上述 secrets。缺少任一项时，macOS
发布包构建会失败，避免再次发布无法正常打开的 DMG。

有完整 secrets 时，workflow 会执行：

- 导入 Developer ID Application 证书到临时 keychain。
- 使用合法 bundle identifier：`com.tingfe.interferencecalculator`。
- 对 `.app` 做 hardened runtime 签名。
- 创建 `.dmg`。
- 对 `.dmg` 签名、提交 Apple notarization、staple 公证票据。
- 使用 `spctl` 校验 DMG 可被 Gatekeeper 接受。

## 临时绕过

只用于内部测试。正式用户不应依赖该方法。

如果已经下载了未公证的旧版 DMG，先把应用拖到 `Applications`，然后运行：

```bash
xattr -dr com.apple.quarantine "/Applications/Interference Calculator.app"
```

之后再打开应用。这个命令只是移除本机隔离属性，不能替代正式签名和公证。

# macOS Signing And Notarization

Official macOS releases must be signed with an Apple Developer ID Application
certificate and notarized by Apple. A non-notarized `.dmg` downloaded through a
browser can be blocked by Gatekeeper as damaged.

## GitHub Secrets

Configure these repository secrets before pushing a `v*` release tag:

- `MACOS_CERTIFICATE_P12`: base64-encoded Developer ID Application `.p12`.
- `MACOS_CERTIFICATE_PASSWORD`: password for the `.p12` certificate.
- `MACOS_CODESIGN_IDENTITY`: signing identity, for example `Developer ID Application: Name (TEAMID)`.
- `MACOS_NOTARY_KEY_ID`: App Store Connect API key ID.
- `MACOS_NOTARY_ISSUER_ID`: App Store Connect issuer ID.
- `MACOS_NOTARY_KEY_P8_BASE64`: base64-encoded `AuthKey_XXXX.p8`.

Tagged releases fail fast when these secrets are missing, so the workflow does
not publish a DMG that normal macOS users cannot open.
