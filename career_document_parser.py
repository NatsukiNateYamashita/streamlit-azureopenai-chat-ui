"""
Career Document Parser
PDFとDocxファイルから職歴情報を抽出し、構造化データに変換するモジュール
"""

import pdfplumber
import docx
import json
from openai import AzureOpenAI
import os
import ssl
import io
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# SSL証明書問題対応（企業環境用）
try:
    ssl._create_default_https_context = ssl._create_unverified_context
    print("SSL証明書検証を無効化しました（企業環境対応）")
except Exception as e:
    print(f"SSL設定変更失敗: {e}")

# 環境変数でSSL検証を無効化
os.environ["PYTHONHTTPSVERIFY"] = "0"


class DocumentTextExtractor:
    """PDF/Docxファイルからテキストと表を抽出するクラス"""
    
    @staticmethod
    def extract_from_pdf_memory(pdf_bytes: bytes) -> Dict[str, Any]:
        """
        PDFのバイナリデータからテキストと表を抽出（メモリベース）
        
        Args:
            pdf_bytes: PDFファイルのバイナリデータ
            
        Returns:
            Dict: 抽出されたテキストと表データ
        """
        extracted_data = {
            "text": "",
            "tables": [],
            "combined_text": "",
            "metadata": {
                "pages": 0,
                "tables_found": 0,
                "extraction_method": "pdfplumber-memory"
            }
        }
        
        try:
            # バイトデータをメモリストリームに変換
            pdf_stream = io.BytesIO(pdf_bytes)
            
            with pdfplumber.open(pdf_stream) as pdf:
                extracted_data["metadata"]["pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # ページテキストを抽出
                    page_text = page.extract_text()
                    if page_text:
                        extracted_data["text"] += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    
                    # 表を抽出
                    tables = page.extract_tables()
                    for table_num, table in enumerate(tables):
                        if table and any(any(cell for cell in row if cell) for row in table):
                            formatted_table = DocumentTextExtractor._format_table_as_text(table, page_num + 1, table_num + 1)
                            extracted_data["tables"].append({
                                "page": page_num + 1,
                                "table_num": table_num + 1,
                                "data": table,
                                "formatted_text": formatted_table
                            })
                            extracted_data["metadata"]["tables_found"] += 1
                
                # テキストと表を統合
                extracted_data["combined_text"] = DocumentTextExtractor._combine_text_and_tables(
                    extracted_data["text"], extracted_data["tables"]
                )
                
        except Exception as e:
            extracted_data["error"] = str(e)
            
        return extracted_data

    @staticmethod
    def extract_from_pdf(pdf_path: str) -> Dict[str, Any]:
        """
        PDFからテキストと表を抽出
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            Dict: 抽出されたテキストと表データ
        """
        extracted_data = {
            "text": "",
            "tables": [],
            "combined_text": "",
            "metadata": {
                "pages": 0,
                "tables_found": 0,
                "extraction_method": "pdfplumber"
            }
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                extracted_data["metadata"]["pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # ページテキストを抽出
                    page_text = page.extract_text()
                    if page_text:
                        extracted_data["text"] += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    
                    # 表を抽出
                    tables = page.extract_tables()
                    for table_num, table in enumerate(tables):
                        if table and any(any(cell for cell in row if cell) for row in table):
                            formatted_table = DocumentTextExtractor._format_table_as_text(table, page_num + 1, table_num + 1)
                            extracted_data["tables"].append({
                                "page": page_num + 1,
                                "table_num": table_num + 1,
                                "data": table,
                                "formatted_text": formatted_table
                            })
                            extracted_data["metadata"]["tables_found"] += 1
                
                # テキストと表を統合
                extracted_data["combined_text"] = DocumentTextExtractor._combine_text_and_tables(
                    extracted_data["text"], extracted_data["tables"]
                )
                
        except Exception as e:
            extracted_data["error"] = str(e)
            
        return extracted_data
    
    @staticmethod
    def extract_from_docx_memory(docx_bytes: bytes) -> Dict[str, Any]:
        """
        DOCXのバイナリデータからテキストと表を抽出（メモリベース）
        
        Args:
            docx_bytes: DOCXファイルのバイナリデータ
            
        Returns:
            Dict: 抽出されたテキストと表データ
        """
        extracted_data = {
            "text": "",
            "tables": [],
            "combined_text": "",
            "metadata": {
                "paragraphs": 0,
                "tables_found": 0,
                "extraction_method": "python-docx-memory"
            }
        }
        
        try:
            # バイトデータをメモリストリームに変換
            docx_stream = io.BytesIO(docx_bytes)
            doc = docx.Document(docx_stream)
            
            # 段落テキストを抽出
            paragraph_texts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraph_texts.append(paragraph.text)
            
            extracted_data["text"] = "\n".join(paragraph_texts)
            extracted_data["metadata"]["paragraphs"] = len(paragraph_texts)
            
            # 表を抽出
            for table_num, table in enumerate(doc.tables):
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        row_data.append(cell.text.strip())
                    table_data.append(row_data)
                
                if table_data and any(any(cell for cell in row if cell) for row in table_data):
                    formatted_table = DocumentTextExtractor._format_table_as_text(table_data, 1, table_num + 1)
                    extracted_data["tables"].append({
                        "page": 1,
                        "table_num": table_num + 1,
                        "data": table_data,
                        "formatted_text": formatted_table
                    })
                    extracted_data["metadata"]["tables_found"] += 1
            
            # テキストと表を統合
            extracted_data["combined_text"] = DocumentTextExtractor._combine_text_and_tables(
                extracted_data["text"], extracted_data["tables"]
            )
            
        except Exception as e:
            extracted_data["error"] = str(e)
            
        return extracted_data

    @staticmethod
    def extract_from_docx(docx_path: str) -> Dict[str, Any]:
        """
        Docxからテキストと表を抽出
        
        Args:
            docx_path: Docxファイルのパス
            
        Returns:
            Dict: 抽出されたテキストと表データ
        """
        extracted_data = {
            "text": "",
            "tables": [],
            "combined_text": "",
            "metadata": {
                "paragraphs": 0,
                "tables_found": 0,
                "extraction_method": "python-docx"
            }
        }
        
        try:
            doc = docx.Document(docx_path)
            
            # 段落テキストを抽出
            paragraph_texts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraph_texts.append(paragraph.text)
            
            extracted_data["text"] = "\n".join(paragraph_texts)
            extracted_data["metadata"]["paragraphs"] = len(paragraph_texts)
            
            # 表を抽出
            for table_num, table in enumerate(doc.tables):
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        row_data.append(cell.text.strip())
                    table_data.append(row_data)
                
                if table_data and any(any(cell for cell in row if cell) for row in table_data):
                    formatted_table = DocumentTextExtractor._format_table_as_text(table_data, 1, table_num + 1)
                    extracted_data["tables"].append({
                        "page": 1,
                        "table_num": table_num + 1,
                        "data": table_data,
                        "formatted_text": formatted_table
                    })
                    extracted_data["metadata"]["tables_found"] += 1
            
            # テキストと表を統合
            extracted_data["combined_text"] = DocumentTextExtractor._combine_text_and_tables(
                extracted_data["text"], extracted_data["tables"]
            )
            
        except Exception as e:
            extracted_data["error"] = str(e)
            
        return extracted_data
    
    def extract_from_doc(self, doc_path: str) -> Dict[str, Any]:
        """
        .docファイルからテキストを抽出（古いWord形式）
        
        Args:
            doc_path: .docファイルのパス
            
        Returns:
            Dict: 抽出されたテキストデータ
        """
        extracted_data = {
            "text": "",
            "tables": [],
            "combined_text": "",
            "metadata": {
                "paragraphs": 0,
                "tables_found": 0,
                "extraction_method": "python-docx-fallback"
            }
        }
        
        try:
            # まず、ファイルが実際に.docx形式として読めるかどうかを確認
            # （一部の.docファイルは実際には.docx形式の場合がある）
            try:
                doc = docx.Document(doc_path)
                paragraph_texts = []
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        paragraph_texts.append(paragraph.text)
                text = "\n".join(paragraph_texts)
                extracted_data["metadata"]["extraction_method"] = "python-docx (compatible format)"
            except Exception as docx_error:
                # python-docxで読めない場合は、.docファイルは現在サポートされていない
                raise ValueError(f".docファイルは現在サポートされていません。.docxファイルに変換してください。元のエラー: {str(docx_error)}")
            
            if text:
                extracted_data["text"] = text
                extracted_data["combined_text"] = text
                # 段落数を推定（改行で区切られたテキスト）
                paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
                extracted_data["metadata"]["paragraphs"] = len(paragraphs)
            else:
                extracted_data["text"] = ""
                extracted_data["combined_text"] = ""
                
        except Exception as e:
            extracted_data["error"] = str(e)
            
        return extracted_data
    
    @staticmethod
    def _format_table_as_text(table_data: List[List[str]], page_num: int, table_num: int) -> str:
        """
        表データを構造化テキストに変換
        
        Args:
            table_data: 表データ
            page_num: ページ番号
            table_num: 表番号
            
        Returns:
            str: フォーマットされた表テキスト
        """
        if not table_data:
            return ""
        
        formatted = f"\n【表データ - Page {page_num}, Table {table_num}】\n"
        
        for row in table_data:
            if row and any(cell for cell in row if cell):
                formatted += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
        
        formatted += "【表データ終了】\n\n"
        return formatted
    
    @staticmethod
    def _combine_text_and_tables(text: str, tables: List[Dict]) -> str:
        """
        テキストと表を統合
        
        Args:
            text: 抽出されたテキスト
            tables: 表データのリスト
            
        Returns:
            str: 統合されたテキスト
        """
        combined = text
        for table in tables:
            combined += table["formatted_text"]
        return combined
    
    @staticmethod
    def extract_text(file_input: Union[str, bytes], file_extension: str, use_memory: bool = False) -> Dict[str, Any]:
        """
        ファイルからテキストを抽出する統合メソッド
        
        Args:
            file_input: ファイルパス（str）またはバイナリデータ（bytes）
            file_extension: ファイル拡張子（.pdf, .docx, .doc）
            use_memory: メモリベース処理を使用するかどうか
            
        Returns:
            Dict: 抽出されたテキストと表データ
        """
        file_extension = file_extension.lower()
        
        if use_memory:
            # メモリベース処理
            if not isinstance(file_input, bytes):
                raise ValueError("メモリベース処理にはbytes型のデータが必要です")
                
            if file_extension == '.pdf':
                return DocumentTextExtractor.extract_from_pdf_memory(file_input)
            elif file_extension in ['.docx', '.doc']:
                return DocumentTextExtractor.extract_from_docx_memory(file_input)
            else:
                return {
                    "text": "",
                    "tables": [],
                    "combined_text": "",
                    "metadata": {"extraction_method": "unsupported"},
                    "error": f"サポートされていないファイル形式: {file_extension}"
                }
        else:
            # ファイルパスベース処理（後方互換性）
            if not isinstance(file_input, str):
                raise ValueError("ファイルパスベース処理にはstr型のパスが必要です")
                
            if file_extension == '.pdf':
                return DocumentTextExtractor.extract_from_pdf(file_input)
            elif file_extension == '.docx':
                return DocumentTextExtractor.extract_from_docx(file_input)
            elif file_extension == '.doc':
                extractor = DocumentTextExtractor()
                return extractor.extract_from_doc(file_input)
            else:
                return {
                    "text": "",
                    "tables": [],
                    "combined_text": "",
                    "metadata": {"extraction_method": "unsupported"},
                    "error": f"サポートされていないファイル形式: {file_extension}"
                }


class CareerDataParser:
    """職歴データを解析してJSONに変換するクラス"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Args:
            openai_api_key: Azure OpenAI APIキー
        """
        self.openai_client = None
        
        # Azure OpenAI の設定 - 環境変数から取得
        self.azure_endpoint = os.getenv('AZURE_OPENAI_CHAT_ENDPOINT')
        self.api_version = os.getenv('AZURE_OPENAI_CHAT_API_VERSION')
        self.deployment_name = os.getenv('AZURE_OPENAI_CHAT_API_DEPLOYMENT_NAME_GPT_4O')
        self.model_name = os.getenv('AZURE_OPENAI_CHAT_MODEL_NAME_GPT_4O')
        
        # プロンプトファイルのパス
        self.prompts_dir = Path(__file__).parent / "prompts"
        
        if openai_api_key:
            try:
                # Azure OpenAI クライアントを初期化
                self.openai_client = AzureOpenAI(
                    api_version=self.api_version,
                    azure_endpoint=self.azure_endpoint,
                    api_key=openai_api_key,
                )
                print("Azure OpenAI接続が正常に初期化されました。")
                    
            except Exception as e:
                raise Exception(f"Azure OpenAI初期化エラー: {e}")
    
    def _load_prompt_file(self, filename: str) -> str:
        """
        プロンプトファイルを読み込む
        
        Args:
            filename: プロンプトファイル名
            
        Returns:
            str: プロンプト内容
        """
        prompt_path = self.prompts_dir / filename
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {prompt_path}")
        except Exception as e:
            raise Exception(f"プロンプトファイル読み込みエラー: {e}")
    
    def parse_career_with_ai(self, extracted_text: str) -> Dict[str, Any]:
        """
        OpenAI APIを使用して職歴情報を解析
        
        Args:
            extracted_text: 抽出されたテキスト
            
        Returns:
            Dict: 解析された職歴データ
        """
        if not self.openai_client:
            raise ValueError("OpenAI APIキーが設定されていません")
        
        # プロンプトファイルから読み込み
        system_prompt = self._load_prompt_file("system_prompt_career_document_parser.txt")
        user_prompt = self._build_parsing_prompt(extracted_text)
        
        # print('-' * 50) 
        # print('extracted_text:')
        # print(extracted_text)
        # print('-' * 50)
        # print('-' * 50) 
        # print('prompt:')
        # print(user_prompt)
        # print('-' * 50)
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                # max_tokens=4000,  # 明示的にmax_tokensを設定
                # temperature=0.1,
                # top_p=0.9,
                # frequency_penalty=0.0,
                # presence_penalty=0.0,
                model=self.model_name
            )
            
            # レスポンスの基本情報をログ出力
            if hasattr(response, 'choices') and len(response.choices) > 0:
                print("DEBUG: Number of choices:", len(response.choices))
                choice = response.choices[0]
                if hasattr(choice, 'message'):
                    print("DEBUG: Message object exists")
                else:
                    print("DEBUG: No message object in choice")
            else:
                print("DEBUG: No choices in response")
                raise ValueError("OpenAIからの応答にchoicesが含まれていません")

            # レスポンス内容を取得
            response_content = response.choices[0].message.content
            
            if not response_content or response_content.strip() == "":
                print("DEBUG: Empty response from OpenAI")
                raise ValueError("OpenAIからの応答が空でした")
            
            # JSONパースを試行
            try:
                # JSONパース前に応答内容をクリーンアップ
                clean_content = response_content.strip()
                
                # Markdown形式のコードブロックが含まれている場合は除去（より堅牢な処理）
                if "```json" in clean_content:
                    # ```json から ``` までの間の内容を抽出
                    start_marker = "```json"
                    end_marker = "```"
                    start_idx = clean_content.find(start_marker)
                    if start_idx != -1:
                        start_idx += len(start_marker)
                        end_idx = clean_content.find(end_marker, start_idx)
                        if end_idx != -1:
                            clean_content = clean_content[start_idx:end_idx].strip()
                elif clean_content.startswith("```") and clean_content.endswith("```"):
                    # 一般的なコードブロック除去
                    clean_content = clean_content[3:-3].strip()
                
                print("DEBUG: Cleaned content:", clean_content[:200] + "..." if len(clean_content) > 200 else clean_content)
                
                parsed_data = json.loads(clean_content)
                # return self._validate_and_format_career_data(parsed_data)
                return parsed_data
            except json.JSONDecodeError as json_error:
                print(f"Response content was: {response_content}")
                raise ValueError(f"JSON Parse Error: {json_error}")
        except Exception as e:
            raise Exception(f"AI解析エラー: {str(e)}")
    
    def _build_parsing_prompt(self, text: str) -> str:
        """AI解析用のプロンプトを構築"""
        # テキストを短縮（プロンプトが長すぎる問題を回避）
        # より保守的な長さ制限を設定
        max_text_length = 10000
        limited_text = text[:max_text_length] + "..." if len(text) > max_text_length else text
        
        print(f"DEBUG: Original text length: {len(text)}")
        print(f"DEBUG: Limited text length: {len(limited_text)}")
        
        # プロンプトテンプレートファイルから読み込み
        template = self._load_prompt_file("user_prompt_career_document_parser.txt")
        
        # テンプレートに抽出テキストを挿入
        final_prompt = template.format(extracted_text=limited_text)
        print(f"DEBUG: Final prompt length: {len(final_prompt)}")
        
        return final_prompt
    
    # def _validate_and_format_career_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """解析されたデータを検証・フォーマット"""
    #     formatted_data = {
    #         "skills": data.get("skills", {}),
    #         "career_history": data.get("career_history", []),
    #         "metadata": {
    #             "extraction_method": "ai_assisted",
    #             "extraction_time": datetime.now().isoformat(),
    #             "confidence": data.get("extraction_confidence", "medium"),
    #             "notes": data.get("processing_notes", "")
    #         }
    #     }
        
    #     # データ検証
    #     if not isinstance(formatted_data["career_history"], list):
    #         formatted_data["career_history"] = []
        
    #     # 必須フィールドの確認
    #     for record in formatted_data["career_history"]:
    #         if "adc_jobcontent_c" not in record:
    #             record["adc_jobcontent_c"] = "職務内容情報が不足しています"
        
    #     return formatted_data


class CareerDocumentProcessor:
    """メインの職歴文書処理クラス"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Args:
            openai_api_key: Azure OpenAI APIキー
        """
        self.text_extractor = DocumentTextExtractor()
        self.career_parser = CareerDataParser(openai_api_key)
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        文書ファイルを処理して職歴データを抽出
        
        Args:
            file_path: 処理するファイルのパス
            
        Returns:
            Dict: 解析結果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # ファイル形式に応じてテキスト抽出
        if file_path.suffix.lower() == '.pdf':
            extracted_data = self.text_extractor.extract_from_pdf(str(file_path))
        elif file_path.suffix.lower() == '.docx':
            extracted_data = self.text_extractor.extract_from_docx(str(file_path))
        elif file_path.suffix.lower() == '.doc':
            extracted_data = self.text_extractor.extract_from_doc(str(file_path))
        else:
            raise ValueError(f"サポートされていないファイル形式: {file_path.suffix}")
        
        if "error" in extracted_data:
            raise Exception(f"テキスト抽出エラー: {extracted_data['error']}")
        
        # AI解析で職歴データを解析
        output = self.career_parser.parse_career_with_ai(extracted_data["combined_text"])
        
        # 結果をまとめて返す
        result = {
            "file_info": {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "file_type": file_path.suffix.lower()
            },
            "extraction_info": extracted_data["metadata"],
            "output": output,
            "raw_text": extracted_data["combined_text"][:1000] + "..." if len(extracted_data["combined_text"]) > 1000 else extracted_data["combined_text"]
        }
        
        return result
    
    def process_document_memory(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        メモリ上のファイルデータを処理して職歴データを抽出
        
        Args:
            file_bytes: ファイルのバイナリデータ
            filename: ファイル名（拡張子判定用）
            
        Returns:
            Dict: 解析結果
        """
        # ファイル拡張子を取得
        file_extension = Path(filename).suffix.lower()
        
        # メモリベースでテキスト抽出
        extracted_data = DocumentTextExtractor.extract_text(
            file_input=file_bytes,
            file_extension=file_extension,
            use_memory=True
        )
        
        if "error" in extracted_data:
            raise Exception(f"テキスト抽出エラー: {extracted_data['error']}")
        
        # AI解析で職歴データを解析
        output = self.career_parser.parse_career_with_ai(extracted_data["combined_text"])
        
        # 結果をまとめて返す
        result = {
            "file_info": {
                "filename": filename,
                "file_size": len(file_bytes),
                "file_type": file_extension,
                "processing_method": "memory-based"
            },
            "extraction_info": extracted_data["metadata"],
            "output": output,
            "raw_text": extracted_data["combined_text"][:1000] + "..." if len(extracted_data["combined_text"]) > 1000 else extracted_data["combined_text"]
        }
        
        return result


if __name__ == "__main__":
    pass
