
# Sakura Blog Scraper

このスクリプトは、櫻坂46の公式ブログから指定されたメンバーの画像を収集するものです。以下の手順に従って環境をセットアップし、スクリプトを実行してください。

---

## 必要条件

- Python 3.10.5
- `pyenv`（Python バージョン管理）
- `poetry`（Python パッケージ管理ツール）
- 仮想環境（venv）での実行

---

## セットアップ手順

### 1. `pyenv` と Python のインストール

`pyenv` を使用して指定のバージョンの Python をインストールします。

#### **`pyenv` のインストール**

Linux または macOS の場合:

```bash
curl https://pyenv.run | bash
```

#### **`pyenv` のパスを設定**

以下を `~/.bashrc` または `~/.zshrc` に追加してください。

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

設定を反映させるには、次のコマンドを実行します。

```bash
source ~/.bashrc  # または source ~/.zshrc
```

#### **Python 3.10.5 のインストール**

指定されたバージョンの Python をインストールして有効化します。

```bash
pyenv install 3.10.5
pyenv global 3.10.5
```

インストールされた Python バージョンを確認します。

```bash
python --version
```

---

### 2. `poetry` のインストール

`poetry` をインストールします。

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

インストール後、`poetry` コマンドをシステムのパスに追加する必要があります。以下を `~/.bashrc` または `~/.zshrc` に追加してください。

```bash
export PATH="$HOME/.local/bin:$PATH"
```

設定を反映します。

```bash
source ~/.bashrc  # または source ~/.zshrc
```

`poetry` のバージョンを確認します。

```bash
poetry --version
```

---

### 3. スクリプトのセットアップ

#### **リポジトリのクローン**

リポジトリをクローンして、ディレクトリに移動します。

```bash
git clone <repository-url>
cd <repository-directory>
```

#### **依存関係のインストール**

`poetry` を使用して依存関係をインストールします。

```bash
poetry install
```

仮想環境を有効化します。

```bash
poetry shell
```

#### **Python とライブラリの確認**

Python とライブラリが正しくインストールされていることを確認します。

```bash
python --version
poetry show
```

---

## 実行手順

1. **スクリプトの実行**

   スクリプトを実行するには、次のようにメンバー名を指定してください。

   ```bash
   python script.py --member "田村保乃"
   ```

   `--member` オプションには、指定するメンバーの名前（漢字）を入力してください。

2. **出力**

   画像は、`data/<メンバー名>` ディレクトリに保存されます。

---

## 注意事項

- スクレイピング対象のウェブサイトの利用規約を遵守してください。
- サーバーへの負荷を減らすために、適切な時間間隔（`time.sleep`）を確保していますが、必要に応じて調整してください。

---

## トラブルシューティング

### 依存ライブラリが見つからない場合

1. Poetry 環境が正しく有効化されているか確認してください。

   ```bash
   poetry shell
   ```

2. 必要なライブラリがインストールされているか確認します。

   ```bash
   poetry install
   ```

### エラーが発生した場合

- `requests.exceptions.RequestException`: ウェブサイトに接続できない場合に発生します。インターネット接続と URL を確認してください。
- `PIL.UnidentifiedImageError`: 画像の保存中にエラーが発生した場合、画像 URL が正しいか確認してください。

---

## 使用ライブラリ

- `requests`: ウェブページの取得
- `BeautifulSoup`: HTML解析
- `pykakasi`: 漢字からローマ字への変換
- `Pillow`: 画像操作
- `argparse`: コマンドライン引数の処理
