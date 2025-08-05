# オーバーライドマッピング機能ガイド

## 概要

オーバーライドマッピング機能は、選択した操作プリセットの一部のキー設定だけを変更したい場合に使用します。プリセット全体を新しく作成する必要がなく、必要な部分だけをカスタマイズできます。

## 設定方法

### config.yamlでの設定

```yaml
key_mapping:
  # 使用する操作プリセット名
  operation_preset: "basic_individual"
  
  # プリセットのオーバーライド（オプション）
  override_mappings:
    system_connect: "Y"      # STARTの代わりにYボタン
    servo_batt_0: "X"        # Aの代わりにXボタン
    motor_forward: "B"       # R2の代わりにBボタン
```

## 優先順位

設定の適用順序は以下の通りです（数字が小さいほど優先度が高い）：

1. **override_mappings** (最優先)
2. 選択された **operation_preset** の設定
3. **basic_individual** のデフォルト設定 (フォールバック)

### 例

```yaml
key_mapping:
  operation_preset: "my_custom_preset"  # カスタムプリセット
  override_mappings:
    system_connect: "HOME"              # この設定が最優先
```

この場合：
- `system_connect`機能は`HOME`ボタンにマッピング（オーバーライド）
- その他の機能は`my_custom_preset`の設定を使用
- `my_custom_preset`に定義されていない機能は`basic_individual`の設定を使用

## 利用可能な機能名

### システム制御機能
- `system_connect`: ESP接続開始
- `system_setup`: ESPセットアップ
- `system_config3`: ESP設定3
- `system_exit`: プログラム終了

### 個別制御モード専用機能
- `servo_batt_0`: バッテリーサーボ0番
- `servo_batt_1`: バッテリーサーボ1番
- `servo_batt_2`: バッテリーサーボ2番
- `servo_batt_3`: バッテリーサーボ3番
- `motor_forward`: 前進制御
- `motor_backward`: 後進制御

### 統合制御モード専用機能
- `forward`: 前進制御（サーボ+モーター統合）
- `backward`: 後進制御（サーボ+モーター統合）

### 共通機能
- `servo_angle_switch`: サーボ角度切り替え
- `stick_legs_control`: 脚部サーボ制御

## 利用可能なボタン名

### デジタルボタン
- `A`, `B`, `X`, `Y`: フェイスボタン
- `L1`, `R1`: 肩ボタン
- `L2`, `R2`: トリガーボタン（一部のコントローラーのみ）
- `START`, `SELECT`: システムボタン
- `HOME`: ホームボタン
- `UP`, `DOWN`, `LEFT`, `RIGHT`: 十字キー（ProConのみ）

### アナログスティック
- `L_STICK`, `R_STICK`: スティック押し込み

**注意**: 利用可能なボタンはコントローラータイプ（`pro_con`, `logi_x`, `logi_d`）によって異なります。

## エラーハンドリング

### 無効な機能名
```yaml
override_mappings:
  unknown_function: "A"  # 存在しない機能名
```
→ 警告メッセージが表示され、この設定はスキップされます

### 無効なボタン名
```yaml
override_mappings:
  system_connect: "INVALID_BUTTON"  # 存在しないボタン名
```
→ 警告メッセージが表示され、デフォルトボタンが使用されます

### 操作モードに対応しない機能
```yaml
key_mapping:
  operation_preset: "basic_integrated"  # 統合制御モード
  override_mappings:
    servo_batt_0: "A"  # 個別制御専用機能
```
→ 警告メッセージが表示され、この設定はスキップされます

### 無効な型
```yaml
override_mappings: "invalid_type"  # 辞書ではない
```
→ 警告メッセージが表示され、オーバーライドは適用されません

## 使用例

### 例1: 基本的なオーバーライド

```yaml
key_mapping:
  operation_preset: "basic_individual"
  override_mappings:
    system_connect: "HOME"    # 接続開始をHOMEボタンに変更
    system_exit: "MINUS"      # 終了をMINUSボタンに変更
```

### 例2: 統合制御モードでのオーバーライド

```yaml
key_mapping:
  operation_preset: "basic_integrated"
  override_mappings:
    forward: "A"              # 前進をAボタンに変更
    backward: "B"             # 後進をBボタンに変更
    system_connect: "PLUS"    # 接続開始をPLUSボタンに変更
```

### 例3: カスタムプリセットとの組み合わせ

```yaml
key_mapping:
  operation_preset: "my_racing_style"  # カスタムプリセット
  override_mappings:
    system_exit: "SELECT"             # 終了ボタンだけ変更
```

## デバッグ情報

オーバーライドマッピングが正しく適用されているかは、起動時のログメッセージで確認できます：

```
✓ キーマッピング設定を読み込みました: プリセット='basic_individual', オーバーライド=2個
✓ オーバーライドマッピングを 2 個適用しました。
```

また、プログラム内で現在の設定を確認することも可能です：

```python
config_info = key_mapping.get_config_info()
print(f"現在のマッピング: {config_info['current_mappings']}")
```

## 注意事項

1. **操作モードの制限**: 各機能は特定の操作モードでのみ利用可能です
2. **ボタンの重複**: 複数の機能を同じボタンにマッピングすることは可能ですが、推奨されません
3. **設定の検証**: 無効な設定は自動的にスキップされ、デフォルト値が使用されます
4. **大文字小文字**: 機能名とボタン名は大文字小文字を区別します

## トラブルシューティング

### オーバーライドが適用されない
- 機能名とボタン名のスペルを確認
- 現在の操作モードで利用可能な機能かチェック
- YAML構文が正しいか確認

### 警告メッセージが表示される
- ログメッセージを確認し、具体的な問題を特定
- 無効な設定を修正するか削除

### 設定が反映されない
- `key_mapping`セクションが正しく配置されているか確認
- ファイルの保存を確認
- 必要に応じてプログラムを再起動