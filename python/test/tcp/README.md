# TCP テスト

このディレクトリには、TCP通信機能のテストファイルが含まれています。

## テストファイル

- `debug.py` - デバッグ出力機能のテスト
- `integration.py` - 本番/デバッグモード切り替えの統合テスト
- `all_run.py` - 全テスト実行スクリプト

## 実行方法

### 個別テスト実行

```bash
cd python/test/tcp
python debug.py
python integration.py
```

### 全テスト一括実行

```bash
cd python/test/tcp
python all_run.py
```

## 必要な設定

テストを実行する前に、`python/config.yaml`ファイルが存在することを確認してください。
存在しない場合は、以下の内容で作成してください：

```yaml
tcp:
  mode: debug  # 'production' または 'debug'
  debug_options:
    show_timestamp: true
    show_colors: true
```

## テスト内容

### debug.py
- デバッグ出力の基本機能
- 各種データ識別子の表示テスト
- エラーハンドリングのテスト

### integration.py
- 本番モードとデバッグモードの切り替え
- 設定ファイルの読み込みテスト
- エラー時のフォールバック動作テスト