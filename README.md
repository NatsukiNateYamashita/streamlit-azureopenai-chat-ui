"# Azure OpenAI Chat UI with Career Document Analysis

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

## 🎯 概要

Azure OpenAIを活用した求職者インタビュー支援ツールです。HR担当者が効率的に求職者とのインタビューを行い、履歴書や職務経歴書を自動解析して構造化されたデータとして活用できます。

### 対象ユーザー
- **人事・採用担当者**: 求職者との効率的なインタビュー実施
- **キャリアコンサルタント**: 体系的なキャリア相談の実施
- **人材紹介会社の担当者**: 候補者情報の構造化と管理

### 主な価値提案
- **効率化**: 手動での履歴書確認時間を最大80%短縮
- **標準化**: 一貫したインタビュープロセスの実現
- **データ化**: 求職者情報の構造化と一元管理
- **品質向上**: AIによる網羅的な情報収集

## ✨ 主な機能

### 💬 AIチャット機能
- **Azure OpenAI GPT-4o**: 最新のGPTモデルを使用した自然な対話
- **専門特化プロンプト**: 求職者インタビューに最適化されたシステムプロンプト
- **リアルタイム応答**: ストリーミングなしの高速応答生成
- **会話継続**: コンテキストを保持した長期対話

#### 利用可能なモデル
- **GPT-4.1**: 最新の推論能力を持つモデル
- **GPT-4o**: 高性能な汎用モデル
- **GPT-4o-mini**: 高速・コスト効率モデル
- **o3-mini**: 最新の推論特化モデル

### 📄 ファイル解析機能
- **対応形式**: PDF, DOCX（Word文書）
- **高精度抽出**: テキスト、表、レイアウト情報を保持
- **AI構造化**: 職歴、スキル、学歴等の自動分類
- **即座に活用**: 解析結果を対話に自動反映

#### 抽出される情報
```json
{
  "skills": {
    "adc_skillnametext_c": "取得資格、技術スキル、語学スキル等"
  },
  "career_history": [
    {
      "adc_jobcontent_c": "詳細な職務内容・経歴情報",
      "adc_enrolledstartyear_c": "就業開始年",
      "adc_enrolledstartmonth_c": "就業開始月",
      "adc_enrolledendyear_c": "就業終了年",
      "adc_enrolledendmonth_c": "就業終了月"
    }
  ],
  "extraction_confidence": "high/medium/low",
  "processing_notes": "抽出処理の詳細情報"
}
```

### ⚙️ プロンプト管理機能
- **外部ファイル管理**: `prompts/system_prompt.txt`でプロンプトを管理
- **構造化インタビュー**: CSVデータを基にした体系的な質問フロー
- **リアルタイム再読み込み**: アプリ再起動なしでプロンプト更新
- **UI内編集**: ブラウザ上での直接編集も可能
- **バージョン管理**: プロンプトのダウンロード・バックアップ

#### インタビュー用AIエージェント機能
- **事前データ解析**: CSVからJSON形式への情報変換
- **優先度ベース質問**: 必須項目から優先的に質問
- **条件分岐質問**: 回答に応じた適応的なインタビュー
- **自然な会話形式**: 1回に1つの質問で負担軽減
- **選択肢提示**: 回答しやすい具体例の提供

### 📊 データ管理機能
- **チャット履歴**: 全会話の構造化保存とダウンロード
- **System Prompt**: 設定内容のバックアップ
- **セッション管理**: 複数チャットセッションの並行管理
- **データ形式**: テキスト、JSON形式での出力

### 🔄 ワークフロー自動化
- **ワンクリック開始**: 「開始」ボタンで即座にインタビュー開始
- **ファイル自動処理**: アップロード後の自動解析と対話への反映
- **構造化インタビュー**: CSVデータベースの質問管理システム
- **優先度制御**: 必須項目から順次質問する自動フロー
- **条件分岐**: 回答に応じた適応的な質問展開
- **エラーハンドリング**: 詳細なエラー情報と対処法の提示

## 🚀 クイックスタート

### 前提条件

```bash
# 必要なソフトウェア
Python 3.8以上
Azure OpenAI APIアクセス権
インターネット接続環境
```

### インストール手順

1. **リポジトリのクローン**
```bash
git clone https://github.com/NatsukiNateYamashita/streamlit-azureopenai-chat-ui.git
cd streamlit-azureopenai-chat-ui
```

2. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

3. **環境変数の設定**

`.env`ファイルを作成し、以下の内容を設定：

```bash
# Azure OpenAI Chat API（必須）
AZURE_OPENAI_CHAT_API_KEY=your_api_key_here
AZURE_OPENAI_CHAT_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_CHAT_API_VERSION=2025-01-01-preview

# モデル設定（複数モデル対応）
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_4_1=gpt-4.1
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_4O=gpt-4o
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_4O_MINI=gpt-4o-mini
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_O3_MINI=o3-mini

# デプロイメント名設定
AZURE_OPENAI_CHAT_API_DEPLOYMENT_NAME_GPT_4O=gpt-4o
```

4. **アプリケーションの起動**
```bash
streamlit run app.py
```

5. **ブラウザでアクセス**
```
http://localhost:8501
```

### 基本的な使用方法

1. **インタビュー開始**: 「開始」ボタンをクリック
2. **ファイルアップロード**: 必要に応じてPDF/DOCXをアップロード
3. **対話継続**: チャット形式でインタビューを進行
4. **結果保存**: 履歴やプロンプトをダウンロード

## 📖 詳細な使用方法

### チャット機能の使い方

#### 🔄 インタビューの開始
- **新規チャット**: サイドバーの「新しいチャット」で新しいセッション開始
- **開始ボタン**: メッセージ履歴が空の場合、「開始」ボタンが表示
- **自動開始**: 開始ボタンクリックで「始めてください」メッセージを自動送信

#### 💬 対話の進行
```
CSVデータ読み込み → 優先度分析 → 必須項目質問 → 条件分岐 → 任意項目 → 終了
```

#### インタビューフローの例
```
👩‍💼 AI: 「本日はご協力ありがとうございます。まず、お持ちのOAスキルの
            カテゴリーを教えてください。（例：業務系、RPA、CAD、
            PowerPoint、Office365など）」

🙋‍♂️ 求職者: 「PowerPointです。」

👩‍💼 AI: 「ありがとうございます。PowerPointでは、どのようなスキルを
            お持ちですか？（例：既存スライドの修正、資料作成、図解作成など）」

🙋‍♂️ 求職者: 「資料作成です。」

👩‍💼 AI: 「承知しました。次に、ITエンジニアスキルのカテゴリーについて
            伺います...」
```

#### 🎛️ モデル選択
- サイドバーでAzure OpenAIのモデルを選択
- 利用可能なモデルは`.env`ファイルから自動取得
- リアルタイムでモデル変更可能

### ファイルアップロード・解析

#### 📁 対応ファイル形式
| 形式 | 抽出内容 | 特徴 |
|------|----------|------|
| **PDF** | テキスト、表、レイアウト | 高精度なテキスト抽出 |
| **DOCX** | 段落、表、メタデータ | 構造化データの保持 |

#### 🔄 解析プロセス
1. **ファイル選択**: 「📎 ファイル添付」エリアからファイルをアップロード
2. **自動抽出**: テキストと表構造を自動的に抽出
3. **AI解析**: Azure OpenAI GPT-4oで内容を構造化
4. **自動送信**: 解析結果を事前データとしてチャットに送信
5. **継続対話**: AIが解析結果を基にインタビューを継続

#### 📊 解析結果の活用

解析されたファイル内容は以下の形式でチャットに送信されます：

```
以下事前収集済みのデータを踏まえ、インタビューを続行してください。
【事前収集済みデータ】
{
  "skills": {"adc_skillnametext_c": "Python, Java, AWS認定..."},
  "career_history": [
    {
      "adc_jobcontent_c": "【基本情報】\n会社名: ABC株式会社\n...",
      "adc_enrolledstartyear_c": "2020",
      "adc_enrolledstartmonth_c": "04"
    }
  ]
}
```

### System Prompt設定

#### 📁 ファイルベースの管理

**主要プロンプトファイル:**
- `prompts/system_prompt.txt`: 構造化インタビュー用AIエージェント設定
- `prompts/system_prompt_career_document_parser.txt`: ファイル解析用プロンプト
- `prompts/user_prompt_career_document_parser.txt`: ユーザープロンプトテンプレート（更新版）

**新機能:**
- **CSVベース質問管理**: 外部CSVファイルから質問項目を動的読み込み
- **優先度制御**: 必須/任意、優先度高/中/低での質問順序制御
- **条件分岐**: 回答内容に応じた次の質問の自動選択
- **自然な会話フロー**: 1回1質問の負担軽減設計

#### ✏️ 編集方法

**方法1: ファイル直接編集**
```bash
# プロンプトファイルを直接編集
notepad prompts/system_prompt.txt

# UI上で再読み込み
「📁 ファイルから再読み込み」ボタンをクリック
```

**方法2: UI編集**
1. System Prompt設定エリアを展開
2. 「編集」ボタンをクリック
3. テキストエリアで直接編集
4. 「保存」ボタンで確定

#### 🔄 プロンプトのカスタマイズ例

```text
あなたは、人財紹介における「求職者インタビュー担当AIエージェント」です。
あなたの目的は、事前に与えられる以下CSVをJSON形式に転換したファイルをもとに、
求職者から必要な情報を自然な会話形式で収集することです。

【行動ルール】
1. ファイルを読み取る
   - この情報を解析し、質問の順序・条件・内容を決定
2. 質問の進め方
   - 「優先度」が高いものから順に、かつ「必須」の項目を優先
   - 「質問条件」に従い、条件が満たされた場合のみ質問
   - 「AIの質問例」をベースに、求職者が答えやすい文章で提示
3. 会話スタイル
   - 1度に質問するのは1つだけ
   - すでに回答を得た情報は再度聞かない
   - 求職者が答えやすいように「選択肢」や「例」を必ず提示

【実行フロー】
1. ファイルを読み込み、全項目を「優先度・必須/任意」で整理
2. 優先度「高」かつ必須 → それ以外の必須 → 任意 の順で質問
3. 各質問の前に「質問条件」をチェック
4. すべて完了したらインタビューを終了
```

### データのダウンロード

#### 💾 サイドバーのダウンロード機能

**1. System Promptダウンロード**
- 現在の設定をテキストファイルで保存
- ファイル名: `system_prompt_YYYYMMDD_HHMMSS.txt`

**2. チャット履歴ダウンロード**
- 全メッセージ履歴を整形してテキストファイルで保存
- ファイル名: `chat_messages_YYYYMMDD_HHMMSS.txt`

#### 📄 ダウンロードファイルの形式

**チャット履歴の例:**
```
=== メッセージ 1 (USER) ===
こんにちは、転職を検討しています。

=== メッセージ 2 (ASSISTANT) ===
こんにちは！転職のご相談ですね。
まず、お名前と現在のご状況を教えていただけますか？

=== メッセージ 3 (USER) ===
田中太郎です。現在、IT企業でエンジニアをしています。
```

## 🔧 設定・カスタマイズ

### 環境変数設定

#### 必須設定

```bash
# Azure OpenAI API接続情報
AZURE_OPENAI_CHAT_API_KEY=3acad7a85d04465498db3ac29f0d7630
AZURE_OPENAI_CHAT_ENDPOINT=https://oai-eur-ww-prd-jpnaimpub.openai.azure.com
AZURE_OPENAI_CHAT_API_VERSION=2025-01-01-preview
```

#### モデル設定

```bash
# 利用可能なモデルの定義
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_4_1=gpt-4.1
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_4O=gpt-4o
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_4O_MINI=gpt-4o-mini
AZURE_OPENAI_CHAT_MODEL_NAME_GPT_O3_MINI=o3-mini

# デプロイメント名（Azure OpenAI Studioで設定した名前）
AZURE_OPENAI_CHAT_API_DEPLOYMENT_NAME_GPT_4O=gpt-4o
```

#### オプション設定

```bash
# アプリケーション設定
LOG_LEVEL=INFO
DEBUG_MODE=False

# Azure AI Search（将来の拡張用）
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your_search_api_key
```

### プロンプトファイルの詳細設定

#### `system_prompt.txt`
```text
あなたは、人財紹介における「求職者インタビュー担当AIエージェント」です。
事前に与えられるCSVをJSON形式に転換したファイルをもとに、
求職者から必要な情報を自然な会話形式で収集します。

【行動ルール】
- 「優先度」が高いものから順に、かつ「必須」の項目を優先して質問
- 1度に質問するのは1つだけ
- 求職者が答えやすいように「選択肢」や「例」を必ず提示
- すべての必須項目が収集できたら感謝を述べて終了
```

#### `system_prompt_career_document_parser.txt`
```text
あなたは履歴書・職務経歴書から職歴情報を正確に抽出するAIアシスタントです。
表構造を含む文書を理解し、構造化されたJSONデータを生成してください。
職務内容は具体的かつ網羅的に含めてください。必ずJSON形式で回答してください。
```

#### `user_prompt_career_document_parser.txt`
```text
履歴書または職務経歴書を分析し、system_promptで指定された
収集情報定義書に基づいて情報を抽出し、JSON形式で整理して回答する。

【出力仕様】
- 回答は必ずJSON形式
- JSONのキーはCSVの「項目」列に対応
- 値は抽出した内容を文字列またはリストで格納
```

### モデル選択ガイド

| モデル | 特徴 | 推奨用途 | コスト |
|--------|------|----------|--------|
| **GPT-4.1** | 最新の推論能力 | 複雑な分析 | 高 |
| **GPT-4o** | 高性能バランス型 | 一般的なインタビュー | 中 |
| **GPT-4o-mini** | 高速・軽量 | 簡単な対話 | 低 |
| **o3-mini** | 推論特化 | 論理的分析 | 中 |

## 📁 プロジェクト構造

```
streamlit-azureopenai-chat-ui/
├── app.py                              # メインアプリケーション
├── career_document_parser.py           # ファイル解析モジュール
├── .env                                # 環境変数設定（作成要）
├── requirements.txt                    # 依存関係
├── README.md                           # このファイル
├── prompts/                            # プロンプト管理ディレクトリ
│   ├── system_prompt.txt              # メインシステムプロンプト（構造化インタビュー）
│   ├── system_prompt_career_document_parser.txt  # ファイル解析用
│   └── user_prompt_career_document_parser.txt    # ユーザープロンプト（更新版）
└── temp/                              # 一時ファイル（自動生成）
```

### 各ファイルの役割

#### `app.py` - メインアプリケーション（433行）
**主要機能:**
- Streamlit UIの制御
- セッション状態管理
- Azure OpenAI API連携
- ファイルアップロード処理
- チャット履歴表示

**重要な関数:**
```python
# Azure OpenAI API呼び出し
def get_openai_response(messages, api_key, endpoint, model, api_version)

# System Prompt読み込み
def load_system_prompt(file_path='./prompts/system_prompt.txt')

# ファイル変換
def convert_file_to_json(uploaded_file)
```

#### `career_document_parser.py` - ファイル解析エンジン
**主要クラス:**

**1. `DocumentTextExtractor`**
- PDF/DOCX/DOCファイルからテキスト抽出
- 表構造の保持
- メタデータ管理

**2. `CareerDataParser`**
- Azure OpenAI APIによる構造化解析
- プロンプトファイルの動的読み込み
- JSON形式での結果出力

**3. `CareerDocumentProcessor`**
- 全体の処理フローを統括
- エラーハンドリング
- 結果の統合
- ログ出力の最適化（v2.0で改善）

#### `prompts/` ディレクトリ
- **外部管理**: アプリ再起動なしでプロンプト変更
- **バージョン管理**: 複数バージョンの保持
- **カスタマイズ**: 用途に応じた細かい調整
- **構造化設計**: CSVベースの質問データベース対応
- **条件分岐対応**: 複雑なインタビューフローの管理

## 🛠️ 開発者向け情報

### アーキテクチャ

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Azure OpenAI    │───▶│ Career Document │
│   (Frontend)    │    │  API Integration │    │ Parser Module   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Session State   │    │ Prompt Manager   │    │ File Processor  │
│ Management      │    │ (External Files) │    │ (PDF/DOCX)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 主要クラス・関数の詳細

#### Azure OpenAI API統合
```python
def get_openai_response(messages, api_key, endpoint, model, api_version):
    """
    非ストリーミングでAzure OpenAI APIからレスポンスを取得
    
    Features:
    - ログ出力機能
    - エラーハンドリング
    - レスポンス検証
    """
```

#### ファイル処理パイプライン
```python
class CareerDocumentProcessor:
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        統合ファイル処理フロー:
        1. ファイル形式判定
        2. テキスト・表抽出
        3. AI構造化解析
        4. 結果統合・検証
        """
```

#### セッション管理
```python
# 主要なセッション状態
st.session_state['system_prompt']      # システムプロンプト
st.session_state['messages']           # チャット履歴
st.session_state['file_text']          # ファイル抽出テキスト
st.session_state['model']              # 選択モデル
```

### API仕様

#### Azure OpenAI Chat Completions API
```http
POST https://{endpoint}/openai/deployments/{model}/chat/completions?api-version={version}

Headers:
- Content-Type: application/json
- api-key: {your-api-key}

Body:
{
  "messages": [
    {"role": "system", "content": "システムプロンプト"},
    {"role": "user", "content": "ユーザーメッセージ"}
  ],
  "model": "gpt-4o",
  "stream": false
}
```

### 拡張方法

#### 1. 新しいファイル形式の追加

```python
# DocumentTextExtractorクラスに新しいメソッドを追加
@staticmethod
def extract_from_xlsx(xlsx_path: str) -> Dict[str, Any]:
    """Excelファイルからテキストを抽出"""
    # 実装内容
    pass

# CareerDocumentProcessorでサポート形式を拡張
def process_document(self, file_path: str) -> Dict[str, Any]:
    if file_path.endswith('.xlsx'):
        return self.extractor.extract_from_xlsx(file_path)
```

#### 2. カスタムプロンプトの追加

```python
# prompts/ディレクトリに新しいファイルを作成
touch prompts/system_prompt_technical_interview.txt

# CareerDataParserで新しいプロンプトを読み込み
def load_technical_interview_prompt(self):
    return self._load_prompt_file("system_prompt_technical_interview.txt")
```

#### 3. UI機能の追加

```python
# app.pyに新しいStreamlitコンポーネントを追加
with st.expander("🎯 インタビュー設定"):
    interview_type = st.selectbox(
        "インタビュータイプ", 
        ["一般面接", "技術面接", "役員面接"]
    )
    
    # セッション状態管理
    st.session_state['interview_type'] = interview_type
```

### パフォーマンス最適化

#### ファイル処理の最適化
```python
# 推奨ファイルサイズ制限
MAX_FILE_SIZE = {
    'pdf': 10 * 1024 * 1024,   # 10MB
    'docx': 5 * 1024 * 1024,   # 5MB
}

# メモリ使用量の監視
import psutil
memory_usage = psutil.virtual_memory().percent
```

#### API使用量の最適化
```python
# プロンプト長の制限
def validate_prompt_length(prompt: str, max_tokens: int = 4000):
    # おおよそのトークン数を計算（英語: 4文字/token, 日本語: 2文字/token）
    estimated_tokens = len(prompt) / 3
    return estimated_tokens <= max_tokens
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 🔑 API接続エラー

**症状:**
```
AuthenticationError: Invalid API key provided
```

**解決方法:**
1. `.env`ファイルの`AZURE_OPENAI_CHAT_API_KEY`を確認
2. Azure OpenAI Studioでキーが有効か確認
3. エンドポイントURLが正しいか確認

```bash
# デバッグ用: 環境変数の確認
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'API_KEY: {os.getenv(\"AZURE_OPENAI_CHAT_API_KEY\", \"未設定\")[:10]}...')"
```

#### 📄 ファイル解析エラー

**症状:**
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**原因と対処:**
1. **ファイルサイズ過大**: 10MB以下に圧縮
2. **複雑な表構造**: シンプルな形式に変換
3. **画像多用**: テキスト主体のファイルに変更
4. **API制限**: トークン数を削減

```python
# デバッグ: 抽出テキストの確認
extracted_text = processor.extract_text(file_path)
print(f"抽出テキスト長: {len(extracted_text)} 文字")
print(f"先頭500文字: {extracted_text[:500]}")
```

#### 🔄 プロンプト読み込みエラー

**症状:**
```
FileNotFoundError: [Errno 2] No such file or directory: './prompts/system_prompt.txt'
```

**解決方法:**
```bash
# プロンプトファイルの存在確認
ls -la prompts/

# ファイルが存在しない場合は作成
echo "あなたは人財企業の求職者インタビューのプロです。" > prompts/system_prompt.txt
```

#### 💾 セッション状態エラー

**症状:**
- チャット履歴が消える
- 設定が保存されない

**対処法:**
```python
# セッション状態のリセット
if st.button("セッション状態をリセット"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

### ログの確認方法

#### アプリケーションログ
```bash
# 詳細ログでStreamlitを起動
streamlit run app.py --logger.level=debug

# ログファイルの確認（Windows）
type %USERPROFILE%\.streamlit\logs\*.log

# ログファイルの確認（Linux/Mac）
tail -f ~/.streamlit/logs/*.log
```

#### Azure OpenAI APIログ
```python
# app.py内でAPI呼び出しログを有効化
logger.info(f"POSTリクエスト: URL={url}")
logger.info(f"ペイロード: {json.dumps(payload, indent=2, ensure_ascii=False)}")
```

### パフォーマンス診断

#### システムリソース監視
```python
import psutil
import time

def monitor_performance():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"CPU使用率: {cpu_percent}%")
    print(f"メモリ使用率: {memory.percent}%")
    print(f"ディスク使用率: {disk.percent}%")
```

#### API応答時間の測定
```python
import time

start_time = time.time()
response = get_openai_response(messages, ...)
end_time = time.time()

print(f"API応答時間: {end_time - start_time:.2f}秒")
```

## 🤝 コントリビューション

### 開発環境のセットアップ

```bash
# リポジトリのフォーク後、クローン
git clone https://github.com/your-username/streamlit-azureopenai-chat-ui.git
cd streamlit-azureopenai-chat-ui

# 開発用ブランチの作成
git checkout -b feature/your-feature-name

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 開発用の追加パッケージ
pip install black flake8 pytest
```

### コード品質管理

#### フォーマット
```bash
# Blackでコードフォーマット
black app.py career_document_parser.py

# インポート順序の整理
isort app.py career_document_parser.py
```

#### リンター
```bash
# Flake8でコード品質チェック
flake8 . --max-line-length=88 --extend-ignore=E203,W503
```

#### テスト
```bash
# 単体テストの実行
pytest tests/ -v

# カバレッジレポート
pytest --cov=. tests/
```

### プルリクエストのガイドライン

1. **機能追加**
   - 新機能は`feature/`ブランチで開発
   - 詳細な説明とスクリーンショットを添付
   - 既存機能への影響を確認

2. **バグ修正**
   - `bugfix/`ブランチで修正
   - 再現手順と修正内容を明記
   - テストケースの追加

3. **ドキュメント更新**
   - `docs/`ブランチで更新
   - 変更内容の詳細説明
   - スクリーンショットの更新

### 報告すべき問題

#### バグレポート
- **環境情報**: OS、Python版、依存関係版
- **再現手順**: 詳細なステップ
- **期待結果**: 本来の動作
- **実際の結果**: 実際の動作とエラーメッセージ

#### 機能要求
- **背景**: なぜその機能が必要か
- **提案**: 具体的な実装案
- **代替案**: 他の解決方法
- **影響**: 既存機能への影響

## 📄 ライセンス

MIT License

Copyright (c) 2025 NatsukiNateYamashita

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 📞 サポート

### 技術サポート
- **GitHub Issues**: [問題報告・機能要求](https://github.com/NatsukiNateYamashita/streamlit-azureopenai-chat-ui/issues)
- **GitHub Discussions**: [質問・相談](https://github.com/NatsukiNateYamashita/streamlit-azureopenai-chat-ui/discussions)

### ドキュメント
- **API仕様**: Azure OpenAI Service公式ドキュメント
- **Streamlit**: [公式ガイド](https://docs.streamlit.io/)
- **Python-docx**: [ライブラリドキュメント](https://python-docx.readthedocs.io/)

### コミュニティ
- **開発者**: [@NatsukiNateYamashita](https://github.com/NatsukiNateYamashita)
- **プロジェクト**: [streamlit-azureopenai-chat-ui](https://github.com/NatsukiNateYamashita/streamlit-azureopenai-chat-ui)

---

**Created with ❤️ for HR professionals and career consultants**

*このツールは、人材業界のデジタル変革を支援し、より効率的で質の高いキャリア支援を実現することを目的として開発されました。*" 
