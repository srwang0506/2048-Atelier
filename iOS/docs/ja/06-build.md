# インストール・ビルド・開発者向け説明

## 配布物の状態

LUMINA 1.0.1 は Swift / SwiftUI 製の iPhone・iPad 共通ネイティブアプリのプロジェクトです。最低対応として設定した OS は iOS / iPadOS 16.4。WebView は使いません。コア、リソース、Xcode プロジェクト、テスト、説明書、教材動画を含みます。現状は**署名済み IPA、シミュレータービルド、TestFlight、App Store 公開のいずれもありません**。

最低 OS とコンパイラーの要件は別です。パッケージは Swift 6.0 以上のツールチェーンを要求し、Swift 5 言語モードを使います。端末の OS に対応する Xcode も必要です。この開発 Mac は Command Line Tools のみで、macOS ホスト環境の検査は済んでいますが、iOS SDK ビルドと実機受け入れ試験は未実施です。

## 自分の端末で起動する

1. Mac に完全な Xcode を入れます。Mac と端末 OS の組み合わせは Apple の [Xcode 対応表](https://developer.apple.com/xcode/system-requirements)で確認してください。`xcode-select --install` のコマンドラインツールだけでは足りません。
2. Xcode を起動し、必要な追加コンポーネントを入れます。Settings → Locations → Command Line Tools でその Xcode を選びます。
3. ソースを書き込み可能なローカルフォルダーへ展開し、`Lumina.xcodeproj` を開きます。共有 Scheme は **Lumina** です。
4. Xcode → Settings → Accounts に自分の Apple Account を追加。ターゲットの Signing & Capabilities で Team を選び、必要なら Bundle Identifier を自分用の一意なものへ変更します。
5. 端末を接続してロック解除し、信頼のペアリングを完了。Xcode・OS の案内に従って Developer Mode を有効にし、実行先にその iPhone / iPad を選びます。
6. ▶ Run を押し、初回ビルドと署名を待ちます。失敗時は最初の具体的なエラーを読みます。拡張子を変えても署名問題は直りません。
7. 起動後にクラシック移動、縦横切り替え、全モード、保存、音と触覚、入出力を確認します。

公式資料：[実機・シミュレーターでの実行](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)、[アカウントとチーム](https://help.apple.com/xcode/mac/current/en.lproj/dev60b6fbbc7.html)。資格や配布条件は利用時点の Apple の規定に従います。個人端末で Run することと TestFlight 配布は別です。

## ファイル構成

| パス | 役割 |
| --- | --- |
| `App/` | SwiftUI、GameModel、入力、音と触覚、アセット、プライバシーマニフェスト |
| `Sources/LuminaCore/` | ルール、乱数、各モード、探索、保存 |
| `Sources/LuminaCore/Resources/` | パズル十二問、レスキュー練習三問 |
| `Tests/LuminaCoreTests/` | ルール対照、保存回帰、AI 長局検査 |
| `Tests/LuminaAppTests/` | ライフサイクル、配置、任意実行の文書用収録 |
| `Lumina.xcodeproj/` | 共有 Scheme とローカルパッケージ参照 |
| `tools/` | 工程生成、検証、Archive、文書制作 |
| `docs/` | 三言語 Markdown、オフライン HTML、GIF と元動画 |
| `QA/` | 保存済み検査ログと配置画像 |

アプリ実行には第三者 SDK やリモート Swift パッケージの取得は不要です。文書制作ツールの依存関係は、ゲーム本体とは分かれています。

## 基本コマンド

プロジェクトのルートで実行します。

```sh
swift test -c release --disable-xctest
python3 tools/validate-project.py
./tools/check.sh
```

一つ目は Mac 上の Swift Testing、二つ目は設定・リソース参照検査です。三つ目は iOS Simulator ビルドも試み、SDK がなければ明確に失敗します。ホスト環境テストは iOS ビルドの代わりにはなりません。

```sh
LUMINA_BENCHMARK=1 swift test -c release --disable-xctest --filter Benchmark
LUMINA_RENDER_DIRECTORY=/tmp/lumina-layouts swift test -c release --disable-xctest --filter renderNativeLayouts
```

長局検査と静的配置画像を明示的に有効にするコマンドです。配置画像はテスト用コンテナーを使い、端末スクリーンショットではありません。教材の収録と変換は[メディア説明](../media/README.md)へ。

## Archive と配布

Xcode の Product → Archive、または次を使います。

```sh
LUMINA_TEAM_ID=YOUR_TEAM_ID ./tools/archive.sh
```

生成するのは `build/Lumina.xcarchive` のみです。自動アップロードや IPA 書き出しはしません。証明書、アカウント資格、端末、配布先に合う方法で別途書き出します。アカウント情報、証明書、端末識別子を公開ソースへ入れないでください。このコマンドで開発者資格の申し込みを代行するわけではありません。

## 保守上の注意

`App/*.swift` を増やしたら `python3 tools/generate-project.py` で参照を更新できます。生成器は Team / Bundle Identifier を初期値へ戻すため、ローカルの署名設定を先に控えてください。文書収録テストは環境変数で有効にした場合だけ動き、独立した一時保存先を使います。プレイヤーの通常データには触れません。

デスクトップとの乱数・ルール互換はフィクスチャで確認しますが、ネイティブ JSON 形式は別です。ルール、能力、問題、ボタン名を変更したら三言語すべてと関連動画を更新してください。文書改訂とゲーム版は別に管理します。今回の文書制作でルールは変えていません。

## 実機受け入れ試験

| 場面 | 合格の目安 |
| --- | --- |
| iPhone 縦・横 | 盤面全体とボタンが見え、目標・結果をスクロール可能 |
| iPad 全画面・Split View | 幅変更や回転で局がリセットされず、操作が隠れない |
| 連続入力後のメニュー | 盤面が止まり、閉じた後に古い入力が出ない |
| AI 探索中の切り替え・バックグラウンド | 古い探索が新しい局を動かしたり上書きしたりしない |
| バックグラウンド・終了後の再起動 | 保存済み状態が戻り、異常は通知される |
| 書き出し・読み込み・キャンセル | 再読込可能。キャンセルと不正ファイルでは現状を保護 |
| キーボード・VoiceOver | 対局操作とシート周辺のフォーカスが正しい |
| 六モードと能力 | 手数、報酬、アシスト区分、結果がルールどおり |
| 音・消音・触覚 | 設定とハードウェアに沿う |

これは今後実行する検査計画であり、すべて合格済みという報告ではありません。
