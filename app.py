import streamlit as st
import os
import sys
from pathlib import Path
from career_document_parser import CareerDocumentProcessor
import requests
import json
from dotenv import load_dotenv
import logging
from streamlit_chat import message
import pandas as pd
import csv
from datetime import datetime
import traceback
import google.protobuf


# Azure Web App Service環境の判定
def is_azure_environment():
    """Azure Web App Service環境かどうかを判定"""
    return 'WEBSITE_SITE_NAME' in os.environ

# 環境に応じたログ設定
def setup_logging():
    """環境に応じたログ設定を行う"""
    
    # ログレベルとフォーマット
    log_level = logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    
    # ログハンドラーのリスト
    handlers = []
    
    if is_azure_environment():
        # Azure環境: 標準出力に強制出力（Log Streamで確認可能）
        site_name = os.environ.get('WEBSITE_SITE_NAME', 'unknown')
        
        # Azure Log Streamに出力（stdout）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(f'[{site_name}] ' + log_format))
        handlers.append(console_handler)
        
        # ファイルログ（Azure Log Files）
        try:
            log_dir = '/home/LogFiles'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(f'{log_dir}/application.log')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(log_format))
            handlers.append(file_handler)
        except Exception as e:
            # ファイルログに失敗してもコンソールログは継続
            print(f"Warning: Could not create file handler: {e}")
    else:
        # ローカル環境: コンソールのみ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter('[LOCAL] ' + log_format))
        handlers.append(console_handler)
    
    # 既存のログ設定をクリア
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # 新しいログ設定
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True  # 既存のログ設定を上書き
    )
    
    return logging.getLogger(__name__)

# ログ設定を実行
logger = setup_logging()

# 起動時の環境情報をログに記録
logger.info("=" * 50)
logger.info("Streamlit App Starting")
logger.info(f"Environment: {'Azure Web App' if is_azure_environment() else 'Local'}")
logger.info(f"Python Version: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")

# ライブラリバージョン情報の記録
logger.info(f"STREAMLIT = {st.__version__}")
logger.info(f"PROTOBUF  = {getattr(google.protobuf, '__version__', 'unknown')}")

if is_azure_environment():
    logger.info(f"Site Name: {os.environ.get('WEBSITE_SITE_NAME')}")
    logger.info(f"Resource Group: {os.environ.get('WEBSITE_RESOURCE_GROUP', 'N/A')}")
logger.info("=" * 50)

def convert_file_to_json(uploaded_file):
    """
    アップロードされたCSV/TXTファイルをJSON形式に変換する関数
    
    Args:
        uploaded_file: Streamlitのアップロードファイルオブジェクト
        
    Returns:
        tuple: (JSON文字列, エラーメッセージ)
    """
    file_info = {
        'name': uploaded_file.name,
        'size': len(uploaded_file.getvalue()),
        'type': uploaded_file.type
    }
    
    logger.info(f"📄 System Prompt file conversion started: {file_info}")
    
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        logger.info(f"📄 File extension: {file_extension}")
        
        if file_extension == 'csv':
            # CSVファイルの処理
            logger.info("📄 Processing as CSV format")
            df = pd.read_csv(uploaded_file)
            logger.info(f"📄 CSV read successfully: {len(df)} rows, {len(df.columns)} columns")
            
            # pandasでJSONに変換（ensure_asciiパラメータなし）
            json_raw = df.to_json(orient='records')
            # 標準のjsonモジュールで整形
            json_data = json.dumps(json.loads(json_raw), indent=2, ensure_ascii=False)
            
            logger.info(f"✅ CSV to JSON conversion successful: {len(json_data)} characters")
            return json_data, None
            
        elif file_extension == 'txt':
            # TXTファイルの処理（JSON形式として解析を試行）
            logger.info("📄 Processing as TXT format")
            content = uploaded_file.read().decode('utf-8')
            logger.info(f"📄 TXT read successfully: {len(content)} characters")
            
            # JSON形式かどうかを確認
            try:
                parsed_json = json.loads(content)
                json_data = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                logger.info("✅ TXT to JSON conversion successful (parsed as JSON)")
                return json_data, None
            except json.JSONDecodeError:
                # JSON形式でない場合は、テキストをそのまま返す
                logger.info("✅ TXT processing successful (processed as plain text)")
                return content, None
                
        else:
            error_msg = f"Unsupported file format: {file_extension}"
            logger.error(f"❌ {error_msg}")
            return None, error_msg
            
    except Exception as e:
        error_msg = f"File conversion error: {str(e)}"
        logger.error(f"❌ System Prompt file conversion failed: {error_msg}")
        logger.error(f"❌ Error details: {traceback.format_exc()}")
        return None, error_msg

def get_openai_response(messages, api_key, endpoint, model, api_version):
    """
    Azure OpenAI APIから一括でレスポンスを取得する関数（非ストリーミング）
    
    Args:
        messages (list): チャット履歴（システムプロンプト含む）
        api_key (str): Azure OpenAI APIキー
        endpoint (str): Azure OpenAIエンドポイント
        model (str): 使用するモデル名
        api_version (str): APIバージョン

    Returns:
        str: AIの応答テキスト
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key
    }
    payload = {
        'messages': messages,
        'model': model,
        'stream': False  # ストリーミングを無効化
    }

    url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"
    
    # リクエスト情報をログに記録（APIキーは伏せる）
    safe_headers = {k: v[:8] + "***" if k == 'api-key' else v for k, v in headers.items()}
    logger.info(f"🤖 API Request [{request_id}]: URL={url}")
    logger.info(f"🤖 API Request [{request_id}]: Headers={safe_headers}")
    logger.info(f"🤖 API Request [{request_id}]: Model={model}")
    logger.info(f"🤖 API Request [{request_id}]: Messages count={len(messages)}")
    
    # メッセージの詳細（デバッグ用）
    total_chars = sum(len(msg.get('content', '')) for msg in messages)
    logger.info(f"🤖 API Request [{request_id}]: Total characters={total_chars}")

    try:
        start_time = datetime.now()
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        logger.info(f"🤖 API Response [{request_id}]: Status={response.status_code}, Duration={duration:.2f}s")

        if response.status_code != 200:
            error_detail = {
                'status_code': response.status_code,
                'response_text': response.text[:500],  # 最初の500文字のみ
                'request_id': request_id
            }
            logger.error(f"❌ API Error [{request_id}]: {error_detail}")
            raise Exception(f"API Error [{request_id}]: {response.status_code}, {response.text}")

        response_data = response.json()
        
        # 応答の詳細をログに記録
        if 'choices' in response_data and response_data['choices']:
            response_content = response_data['choices'][0]['message']['content']
            logger.info(f"✅ API Success [{request_id}]: Response length={len(response_content)}")
            
            # 使用量情報（あれば）
            if 'usage' in response_data:
                usage = response_data['usage']
                logger.info(f"📊 API Usage [{request_id}]: {usage}")
            
            return response_content
        else:
            logger.error(f"❌ API Invalid Response [{request_id}]: No choices in response")
            raise Exception(f"Invalid API response [{request_id}]: No choices")
            
    except requests.exceptions.Timeout:
        logger.error(f"❌ API Timeout [{request_id}]: Request timeout after 120s")
        raise Exception(f"API request timeout [{request_id}]")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API Request Error [{request_id}]: {str(e)}")
        raise Exception(f"API request error [{request_id}]: {str(e)}")
        
    except Exception as e:
        logger.error(f"❌ API Unexpected Error [{request_id}]: {str(e)}")
        logger.error(f"❌ Traceback [{request_id}]: {traceback.format_exc()}")
        raise

# .envからモデル名を取得する関数
def get_models_from_env(env_path):
    models = []
    if not Path(env_path).exists():
        return models
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('AZURE_OPENAI_CHAT_MODEL_NAME_'):
                key, value = line.strip().split('=', 1)
                models.append(value)
    return models

# System Promptをファイルから読み込む関数
def load_system_prompt(file_path='./prompts/system_prompt.txt'):
    """System Promptをファイルから読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # シングルクォートやダブルクォートで囲まれている場合は除去
            if (content.startswith("'") and content.endswith("'")) or \
                (content.startswith('"') and content.endswith('"')):
                content = content[1:-1]
            return content

    except Exception as e:
        raise Exception(f"Error loading system prompt: {str(e)}")

# .envのパス
ENV_PATH = './.env'
MODELS = get_models_from_env(ENV_PATH)

# .envファイルを読み込む
load_dotenv()

# APIキー・エンドポイント取得
API_KEY = os.getenv('AZURE_OPENAI_CHAT_API_KEY')
ENDPOINT = os.getenv('AZURE_OPENAI_CHAT_ENDPOINT')
API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')

if not API_KEY or not ENDPOINT:
    st.error("APIキーまたはエンドポイントが設定されていません。")

st.set_page_config(page_title='Azure OpenAI Chat', layout='wide')
st.title('Azure OpenAI Chat App')

# セッションステートの初期化
if 'system_prompt' not in st.session_state:
    st.session_state['system_prompt'] = load_system_prompt()
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ''
if 'file_text' not in st.session_state:
    st.session_state['file_text'] = ''
if 'system_prompt_files' not in st.session_state:
    st.session_state['system_prompt_files'] = []
if 'is_editing_system_prompt' not in st.session_state:
    st.session_state['is_editing_system_prompt'] = False
if 'file_expander_expanded' not in st.session_state:
    st.session_state['file_expander_expanded'] = False

# 左サイドバー
with st.sidebar:
    st.header('チャット設定')
    if st.button('新しいチャット'):
        st.session_state['messages'] = []
        st.session_state['system_prompt'] = load_system_prompt()
        st.session_state['system_prompt_files'] = []
        st.session_state['user_input'] = ''
        st.session_state['file_text'] = ''
        st.session_state['is_editing_system_prompt'] = False
        st.session_state['file_expander_expanded'] = False
        if 'uploaded_file_name' in st.session_state:
            del st.session_state['uploaded_file_name']
        st.rerun()  # ページを再実行して変更を反映
    model = st.selectbox('モデル選択', MODELS)
    st.session_state['model'] = model
    
    # ダウンロードセクション
    st.header('ダウンロード')
    
    # System Promptダウンロード
    if st.session_state.get('system_prompt') and len(st.session_state['system_prompt']) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📄 System Promptをダウンロード",
            data=st.session_state['system_prompt'],
            file_name=f"system_prompt_{timestamp}.txt",
            mime="text/plain",
            key="download_system_prompt_sidebar"
        )
    
    # メッセージ履歴ダウンロード
    if st.session_state.get('messages') and len(st.session_state['messages']) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # メッセージをテキスト形式で整形
        messages_text = ""
        for i, msg in enumerate(st.session_state['messages']):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            messages_text += f"=== メッセージ {i+1} ({role.upper()}) ===\n"
            messages_text += f"{content}\n\n"
        
        st.download_button(
            label="💬 チャット履歴をダウンロード",
            data=messages_text,
            file_name=f"chat_messages_{timestamp}.txt",
            mime="text/plain",
            key="download_messages_sidebar"
        )
    

# System Prompt設定（折りたたみ可能）
with st.expander("⚙️ System Prompt設定", expanded=False):
    # 編集ボタン（編集モードでない場合のみ表示）
    if not st.session_state.get('is_editing_system_prompt', False):
        if st.button("編集", key="edit_system_prompt"):
            st.session_state['is_editing_system_prompt'] = True

    # System Prompt表示/編集
    if st.session_state.get('is_editing_system_prompt', False):
        # 編集モード
        edited_prompt = st.text_area(
            "System Promptを編集", 
            value=st.session_state['system_prompt'],
            height=200
        )
        if st.button("保存", key="save_system_prompt"):
            st.session_state['system_prompt'] = edited_prompt
            st.session_state['is_editing_system_prompt'] = False
            st.success("System Promptを更新しました！")
            st.rerun()
        if st.button("キャンセル", key="cancel_edit"):
            st.session_state['is_editing_system_prompt'] = False
            st.rerun()
    else:
        # 表示モード
        st.text_area(
            "現在のSystem Prompt", 
            value=st.session_state['system_prompt'], 
            height=200, 
            disabled=True
        )
    # CSV/TXTファイルアップロード
    uploaded_system_files = st.file_uploader(
        'System Prompt用ファイル（CSV, TXT）', 
        type=['csv', 'txt'], 
        accept_multiple_files=True,
        key='system_files'
    )
    ### DEBUG ###
    st.write("DEBUG: uploaded_system_files =", uploaded_system_files)

    if uploaded_system_files is not None:
        for uploaded_file in uploaded_system_files:
            st.write("✅ Uploaded:", uploaded_file.name, uploaded_file.size)
            st.download_button("確認ダウンロード", uploaded_file.getvalue(), file_name=uploaded_file.name)
    ### DEBUG ###   
    # アップロードされたファイルの処理
    if uploaded_system_files:
        for uploaded_file in uploaded_system_files:
            # 新しいファイルかどうかをチェック
            file_names = [f['name'] for f in st.session_state['system_prompt_files']]
            if uploaded_file.name not in file_names:
                with st.spinner(f'ファイル "{uploaded_file.name}" を変換中...'):
                    json_data, error = convert_file_to_json(uploaded_file)
                    
                    if error:
                        logger.error(f"❌ System Prompt file conversion error: {uploaded_file.name} - {error}")
                        st.error(f"ファイル変換エラー: {error}")
                    else:
                        logger.info(f"✅ System Prompt file conversion successful: {uploaded_file.name}")
                        # ファイル情報をセッションに保存
                        st.session_state['system_prompt_files'].append({
                            'name': uploaded_file.name,
                            'content': json_data
                        })
                        st.success(f'ファイル "{uploaded_file.name}" を変換しました！')

    # アップロードされたファイルの管理
    if st.session_state['system_prompt_files']:
        st.write("📁 **添付されたファイル:**")
        for i, file_info in enumerate(st.session_state['system_prompt_files']):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"• {file_info['name']}")
            with col2:
                if st.button("プレビュー", key=f"preview_{i}"):
                    st.session_state[f'show_preview_{i}'] = not st.session_state.get(f'show_preview_{i}', False)
            with col3:
                if st.button("削除", key=f"delete_{i}"):
                    st.session_state['system_prompt_files'].pop(i)
                    st.rerun()
            
            # プレビュー表示
            if st.session_state.get(f'show_preview_{i}', False):
                preview_content = file_info['content'][:500] + "..." if len(file_info['content']) > 500 else file_info['content']
                st.code(preview_content, language='json')

    # System Promptの構築（ファイル内容を含む）
    def build_complete_system_prompt():
        # 現在のsystem_promptから既に追加されたファイル内容を削除（基本部分のみ抽出）
        base_prompt = st.session_state['system_prompt']
        
        # 既存のファイル内容があれば削除して基本部分のみを取得
        for file_info in st.session_state['system_prompt_files']:
            file_section = f"\n\n### {file_info['name']}\n{file_info['content']}"
            if file_section in base_prompt:
                base_prompt = base_prompt.replace(file_section, "")
        
        # 新しくファイル内容を追加
        complete_prompt = base_prompt
        for file_info in st.session_state['system_prompt_files']:
            complete_prompt += f"\n\n### {file_info['name']}\n{file_info['content']}"
        
        return complete_prompt

    # ファイル追加時のSystem Prompt更新
    if st.button('ファイルをSystem Promptに追加'):
        if st.session_state['system_prompt_files']:
            st.session_state['system_prompt'] = build_complete_system_prompt()
            st.success("ファイル内容をSystem Promptに追加しました！")
            st.rerun()
        else:
            st.warning("追加するファイルがありません。")

# ファイル添付（折りたたみ可能）
with st.expander("📎 ファイル添付（PDF, DOCXのみ）",  expanded=st.session_state.get('file_expander_expanded', False)):
    uploaded_file = st.file_uploader('ファイルを選択してください', type=['pdf', 'docx'])
    
    ### DEBUG ###
    st.write("DEBUG: uploaded_file =", uploaded_file)

    if uploaded_file is not None:
        st.write("✅ Uploaded:", uploaded_file.name, uploaded_file.size)
        st.download_button("確認ダウンロード", uploaded_file.getvalue(), file_name=uploaded_file.name)
    ### DEBUG ###    
        
    # ファイルが添付された場合の自動解析処理
    if uploaded_file:
        if 'uploaded_file_name' not in st.session_state or st.session_state['uploaded_file_name'] != uploaded_file.name:
            # 新しいファイルがアップロードされた場合
            st.session_state['uploaded_file_name'] = uploaded_file.name
            
            # ファイル情報をログに記録
            file_info = {
                'name': uploaded_file.name,
                'size': len(uploaded_file.getvalue()),
                'type': uploaded_file.type,
                'user_session': id(st.session_state)  # セッションID（簡易版）
            }
            logger.info(f"📎 PDF/DOCX processing started: {file_info}")
            
            with st.spinner(f'ファイル "{uploaded_file.name}" を解析中...'):
                try:
                    # メモリベース処理（一時ファイル不要）
                    logger.info("📎 Binary data retrieval started")
                    file_bytes = uploaded_file.getvalue()  # バイナリデータを取得
                    logger.info(f"📎 Binary data retrieval completed: {len(file_bytes)} bytes")
                    
                    # ファイル解析（メモリベース）
                    logger.info("📎 CareerDocumentProcessor initialization")
                    processor = CareerDocumentProcessor(API_KEY)
                    
                    logger.info("📎 Document analysis started")
                    result = processor.process_document_memory(file_bytes, uploaded_file.name)
                    logger.info(f"📎 Document analysis completed: Text length={len(result.get('raw_text', ''))}")
                    
                    st.session_state['file_text'] = result['raw_text']
                    
                    st.success(f'ファイル "{uploaded_file.name}" の解析が完了しました！')
                    logger.info(f"✅ PDF/DOCX processing successful: {uploaded_file.name}")
                    
                    # # 解析結果のプレビューを表示
                    # with st.expander("📄 解析されたファイル内容のプレビュー"):
                    #     preview_text = st.session_state['file_text'][:500] + "..." if len(st.session_state['file_text']) > 500 else st.session_state['file_text']
                    #     st.text_area("抽出されたテキスト", value=preview_text, height=200, disabled=True)
                    
                    # メッセージ履歴に追加
                    content = f"以下事前収集済みのデータを踏まえ、インタビューを続行してください。\n【事前収集済みデータ】\n{result['output']}"
                    st.session_state['messages'].append({'role': 'user', 'content': content})
                   
                    # API送信用メッセージ構築
                    messages = []
                    if st.session_state['system_prompt']:
                        messages.append({'role': 'system', 'content': st.session_state['system_prompt']})
                    for msg in st.session_state['messages']:
                        messages.append(msg)
                    # Azure OpenAI API呼び出し（最適化版）
                    try:
                        logger.info("🤖 Azure OpenAI API call started")
                        st.info('応答を取得中...')
                        # 一括でレスポンスを取得
                        assistant_response = get_openai_response(messages, API_KEY, ENDPOINT, model, API_VERSION)
                        # 完全な応答をセッションに保存
                        if assistant_response:
                            st.session_state['messages'].append({'role': 'assistant', 'content': assistant_response})
                            # ✅ ここでexpanderを閉じる
                            st.session_state['file_expander_expanded'] = False
                            # デバッグ用ログ
                            logger.info(f"✅ Azure OpenAI API successful: Response length {len(assistant_response)}")
                            logger.info(f"File processing completed - expander state: {st.session_state['file_expander_expanded']}")
                            # ページを再実行してチャット履歴を更新
                            st.rerun()
                        else:
                            logger.warning("⚠️ Azure OpenAI API response is empty")
                    except Exception as api_error:
                        error_msg = str(api_error)
                        logger.error(f"❌ Azure OpenAI API call failed: {error_msg}")
                        logger.error(f"❌ API error details: {traceback.format_exc()}")
                        st.error(f"API呼び出しエラー: {error_msg}")
                except Exception as e:
                    error_msg = str(e)
                    error_type = type(e).__name__
                    
                    # 詳細なエラーログ
                    logger.error(f"❌ PDF/DOCX processing failed: {uploaded_file.name}")
                    logger.error(f"❌ Error type: {error_type}")
                    logger.error(f"❌ Error message: {error_msg}")
                    logger.error(f"❌ Stack trace: {traceback.format_exc()}")
                    logger.error(f"❌ File information: {file_info}")
                    
                    st.error(f"ファイル解析中にエラーが発生しました: {error_msg}")
                    
                    # エラーの詳細をexpanderで表示
                    with st.expander("🔍 エラーの詳細情報"):
                        st.text(f"エラータイプ: {error_type}")
                        st.text(f"エラーメッセージ: {error_msg}")
                        st.text(f"ファイル名: {uploaded_file.name}")
                        st.text(f"ファイルサイズ: {len(uploaded_file.getvalue())} bytes")
                        st.text(f"ファイルタイプ: {uploaded_file.type}")
                        st.text(f"環境: {'Azure' if is_azure_environment() else 'Local'}")
                        
                        if "JSONパース" in error_msg:
                            st.warning("💡 **対処法**: このエラーは通常、以下の原因で発生します：")
                            st.write("1. ファイル内容が複雑すぎてAIが処理できない")
                            st.write("2. Azure OpenAI APIの応答が不正")
                            st.write("3. プロンプトのトークン数制限を超過")
                            st.info("**推奨**: より簡潔なファイルで試すか、しばらく待ってから再度試してください。")
                    
                    st.session_state['file_text'] = ''
    else:
        # ファイルが削除された場合
        if 'uploaded_file_name' in st.session_state:
            del st.session_state['uploaded_file_name']
            st.session_state['file_text'] = ''

    # # 現在添付されているファイルの表示
    # if st.session_state.get('file_text', ''):
    #     st.info(f"📎 添付ファイル: {st.session_state.get('uploaded_file_name', '不明なファイル')}")
    #     if st.button("添付ファイルを削除", key="remove_attached_file"):
    #         st.session_state['file_text'] = ''
    #         if 'uploaded_file_name' in st.session_state:
    #             del st.session_state['uploaded_file_name']
    #         st.success("添付ファイルを削除しました！")
    #         st.rerun()

# チャット履歴をChatGPT風に表示
st.subheader('チャット')
chat_container = st.container()
with chat_container:
    if st.session_state['messages']:
        for i, msg in enumerate(st.session_state['messages']):
            if msg['role'] == 'user':
                message(msg['content'], is_user=True, key=f"user_{i}")
            else:
                message(msg['content'], is_user=False, key=f"assistant_{i}")

# 開始ボタン（メッセージが空の場合のみ表示）
if len(st.session_state['messages']) == 0:
    if st.button("開始", use_container_width=True, type="primary"):
        user_input = "始めてください"
        
        # メッセージ履歴に追加
        st.session_state['messages'].append({'role': 'user', 'content': user_input})
        
        # API送信用メッセージ構築
        messages = []
        if st.session_state['system_prompt']:
            messages.append({'role': 'system', 'content': st.session_state['system_prompt']})
        for msg in st.session_state['messages']:
            messages.append(msg)
        
        # Azure OpenAI API呼び出し
        try:
            with st.spinner('応答を取得中...'):
                # 一括でレスポンスを取得
                assistant_response = get_openai_response(messages, API_KEY, ENDPOINT, model, API_VERSION)
                
                # 完全な応答をセッションに保存
                if assistant_response:
                    st.session_state['messages'].append({'role': 'assistant', 'content': assistant_response})
                    # ページを再実行してチャット履歴を更新
                    st.rerun()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# チャット入力（エンターキーで送信可能）
user_input = st.chat_input("メッセージを入力してください...")

# メッセージが入力された場合の処理
if user_input:
    # # ファイルのテキストがある場合は取得
    # file_text = st.session_state.get('file_text', '')
    
    # メッセージ履歴に追加
    st.session_state['messages'].append({'role': 'user', 'content': user_input})
    # API送信用メッセージ構築
    messages = []
    if st.session_state['system_prompt']:
        messages.append({'role': 'system', 'content': st.session_state['system_prompt']})
    for msg in st.session_state['messages']:
        messages.append(msg)
    # if file_text:
    #     messages.append({'role': 'user', 'content': f'添付ファイル内容: {file_text}'})

    # Azure OpenAI API呼び出し（最適化版）
    try:
        st.info('応答を取得中...')
        
        # 一括でレスポンスを取得
        assistant_response = get_openai_response(messages, API_KEY, ENDPOINT, model, API_VERSION)
        
        # 完全な応答をセッションに保存
        if assistant_response:
            st.session_state['messages'].append({'role': 'assistant', 'content': assistant_response})
            # ページを再実行してチャット履歴を更新
            st.rerun()
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
