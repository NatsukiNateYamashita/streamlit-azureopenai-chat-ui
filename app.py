import streamlit as st
import os
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


# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_file_to_json(uploaded_file):
    """
    アップロードされたCSV/TXTファイルをJSON形式に変換する関数
    
    Args:
        uploaded_file: Streamlitのアップロードファイルオブジェクト
        
    Returns:
        tuple: (JSON文字列, エラーメッセージ)
    """
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            # CSVファイルの処理
            df = pd.read_csv(uploaded_file)
            # pandasでJSONに変換（ensure_asciiパラメータなし）
            json_raw = df.to_json(orient='records')
            # 標準のjsonモジュールで整形
            json_data = json.dumps(json.loads(json_raw), indent=2, ensure_ascii=False)
            return json_data, None
            
        elif file_extension == 'txt':
            # TXTファイルの処理（JSON形式として解析を試行）
            content = uploaded_file.read().decode('utf-8')
            
            # JSON形式かどうかを確認
            try:
                parsed_json = json.loads(content)
                json_data = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                return json_data, None
            except json.JSONDecodeError:
                # JSON形式でない場合は、テキストをそのまま返す
                return content, None
                
        else:
            return None, f"サポートされていないファイル形式: {file_extension}"
            
    except Exception as e:
        return None, f"ファイル変換エラー: {str(e)}"

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
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key
    }
    payload = {
        'messages': messages,
        'model': model,
        'stream': False  # ストリーミングを無効化
    }

    # POST内容をログに出力
    url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"
    logger.info(f"POSTリクエスト: URL={url}")
    logger.info(f"ヘッダー: {headers}")
    logger.info(f"ペイロード: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    response = requests.post(url, 
                             headers=headers, 
                             data=json.dumps(payload))

    if response.status_code != 200:
        logger.error(f"APIエラー: {response.status_code}, {response.text}")
        raise Exception(f"APIエラー: {response.status_code}, {response.text}")

    response_data = response.json()
    return response_data['choices'][0]['message']['content']

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
    # アップロードされたファイルの処理
    if uploaded_system_files:
        for uploaded_file in uploaded_system_files:
            # 新しいファイルかどうかをチェック
            file_names = [f['name'] for f in st.session_state['system_prompt_files']]
            if uploaded_file.name not in file_names:
                with st.spinner(f'ファイル "{uploaded_file.name}" を変換中...'):
                    json_data, error = convert_file_to_json(uploaded_file)
                    
                    if error:
                        st.error(f"ファイル変換エラー: {error}")
                    else:
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
    # ダウンロードボタン       
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="📥 system promptをダウンロード",
        data=json.dumps(st.session_state['system_prompt'], indent=2, ensure_ascii=False).encode('utf-8'),
        file_name= f"system_prompt_{timestamp}.json",
        mime="application/json",
        key="download_system_prompt"
    )

# ファイル添付（折りたたみ可能）
with st.expander("📎 ファイル添付（PDF, DOCXのみ）",  expanded=st.session_state.get('file_expander_expanded', False)):
    uploaded_file = st.file_uploader('ファイルを選択してください', type=['pdf', 'docx'])

    # ファイルが添付された場合の自動解析処理
    if uploaded_file:
        if 'uploaded_file_name' not in st.session_state or st.session_state['uploaded_file_name'] != uploaded_file.name:
            # 新しいファイルがアップロードされた場合
            st.session_state['uploaded_file_name'] = uploaded_file.name
            
            with st.spinner(f'ファイル "{uploaded_file.name}" を解析中...'):
                try:
                    # 一時ファイル保存
                    temp_path = f"./temp_{uploaded_file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # ファイル解析
                    processor = CareerDocumentProcessor(API_KEY)
                    result = processor.process_document(temp_path)
                    st.session_state['file_text'] = result['raw_text']
                    
                    # 一時ファイルを削除
                    os.remove(temp_path)
                    
                    st.success(f'ファイル "{uploaded_file.name}" の解析が完了しました！')
                    
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
                        st.info('応答を取得中...')
                        # 一括でレスポンスを取得
                        assistant_response = get_openai_response(messages, API_KEY, ENDPOINT, model, API_VERSION)
                        # 完全な応答をセッションに保存
                        if assistant_response:
                            st.session_state['messages'].append({'role': 'assistant', 'content': assistant_response})
                            # ✅ ここでexpanderを閉じる
                            st.session_state['file_expander_expanded'] = False
                            # デバッグ用ログ
                            logger.info(f"ファイル処理完了後のexpander状態: {st.session_state['file_expander_expanded']}")
                            # ページを再実行してチャット履歴を更新
                            st.rerun()
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"ファイル解析中にエラーが発生しました: {error_msg}")
                    
                    # エラーの詳細をexpanderで表示
                    with st.expander("🔍 エラーの詳細情報"):
                        st.text(f"エラータイプ: {type(e).__name__}")
                        st.text(f"エラーメッセージ: {error_msg}")
                        
                        if "JSONパース" in error_msg:
                            st.warning("💡 **対処法**: このエラーは通常、以下の原因で発生します：")
                            st.write("1. ファイル内容が複雑すぎてAIが処理できない")
                            st.write("2. Azure OpenAI APIの応答が不正")
                            st.write("3. プロンプトのトークン数制限を超過")
                            st.info("**推奨**: より簡潔なファイルで試すか、しばらく待ってから再度試してください。")
                        
                        # ファイル情報も表示
                        if uploaded_file:
                            st.text(f"ファイル名: {uploaded_file.name}")
                            st.text(f"ファイルサイズ: {len(uploaded_file.getbuffer())} bytes")
                    
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
