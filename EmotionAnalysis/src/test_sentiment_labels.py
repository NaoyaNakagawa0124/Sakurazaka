# test_sentiment_labels.py

import os
import traceback
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from dotenv import load_dotenv
import torch

# TensorFlow のログを抑制
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# .envファイルを読み込む
load_dotenv()

# 環境変数からアクセストークンを取得（必要な場合）
access_token = os.getenv('HF_ACCESS_TOKEN')

# 使用する感情分析モデル
model_name = "koshin2001/Japanese-to-emotions"

# モデルとトークナイザーをロード
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()  # 評価モードに設定
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
except Exception as e:
    print("感情分析モデルのロードに失敗しました。環境・ネットワーク状態を確認してください。")
    traceback.print_exc()
    exit(1)

# モデルのラベル一覧を表示
labels = model.config.id2label
print("モデルのラベル一覧:")
for idx, label in labels.items():
    print(f"{idx}: {label}")

def classify_emotion(sentence):
    try:
        # トークナイズ（token_type_ids を生成しない）
        inputs = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=512, padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items() if k != 'token_type_ids'}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            scores, predicted = torch.max(probabilities, dim=1)
            label = labels[predicted.item()]
            score = scores.item()
            return {'label': label, 'score': score}
    except Exception as e:
        print(f"感情分析中にエラーが発生しました: 文: {sentence}")
        traceback.print_exc()
        return None

# テスト文の定義
test_sentences = [
    "今日はとても楽しかったです。",            # 喜び
    "とても悲しい気持ちになりました。",        # 悲しみ
    "少し驚きました。",                        # 驚き
    "怒りを感じます。",                        # 怒り
    "普通の日でした。",                        # 中立
    "怖い夢を見ました。",                      # 恐れ
    "うれしいニュースを聞きました。",          # 喜び
    "少し疲れました。",                        # 疲労
]

# 感情分析の実行と結果の表示
for sentence in test_sentences:
    res = classify_emotion(sentence)
    if res:
        print(f"文: {sentence}")
        print(f"感情: {res}\n")
    else:
        print(f"文: {sentence}")
        print("感情分析に失敗しました。\n")
