"""
メモリベース処理のテストスクリプト
"""
import os
from career_document_parser import DocumentTextExtractor

def test_memory_processing():
    """メモリベース処理のテスト"""
    print("メモリベース処理テストを開始...")
    
    # テスト用のダミーPDFバイトデータ（実際のPDFファイルではない簡易テスト）
    try:
        # extract_textメソッドのテスト（エラーハンドリング）
        test_bytes = b"dummy test data"
        result = DocumentTextExtractor.extract_text(
            file_input=test_bytes,
            file_extension=".pdf",
            use_memory=True
        )
        print("メソッド呼び出し成功")
        print(f"結果: {result}")
        
        # サポートされていないファイル形式のテスト
        result2 = DocumentTextExtractor.extract_text(
            file_input=test_bytes,
            file_extension=".txt",
            use_memory=True
        )
        print(f"サポートされていないファイル形式のテスト: {result2}")
        
    except Exception as e:
        print(f"エラー: {e}")
    
    print("テスト完了")

if __name__ == "__main__":
    test_memory_processing()
