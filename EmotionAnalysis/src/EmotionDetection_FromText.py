# EmotionDetection_FromText.py

import os
import requests
from bs4 import BeautifulSoup
import time
import random
import argparse
from urllib.parse import urlparse, parse_qs
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from dotenv import load_dotenv
import re
import traceback
from fugashi import Tagger  # fugashiをインポート
import torch  # torchをインポート
import matplotlib.pyplot as plt  # matplotlib をインポート

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
    print("モデルとトークナイザーをロード中...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()  # 評価モードに設定
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print("モデルとトークナイザーのロードに成功しました。")
except Exception as e:
    print("感情分析モデルのロードに失敗しました。環境・ネットワーク状態を確認してください。")
    traceback.print_exc()
    exit(1)

# モデルのラベル一覧を表示
labels = model.config.id2label
print("\nモデルのラベル一覧:")
for idx, label in labels.items():
    print(f"{idx}: {label}")

# 感情ラベルの意味を定義
label_meanings = {
    'LABEL_0': '喜び',
    'LABEL_1': '怒り',
    'LABEL_2': '悲しみ',
    'LABEL_3': '驚き',
    'LABEL_4': '中立',
    'LABEL_5': '恐れ',
    'LABEL_6': '疲労',
    'LABEL_7': 'その他'
}

# 感情分析関数の定義
def classify_emotion(sentence):
    try:
        # トークナイズ（token_type_ids を生成しない）
        inputs = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=512, padding=True)
        # 'token_type_ids' を除外
        inputs = {k: v.to(device) for k, v in inputs.items() if k != 'token_type_ids'}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            scores, predicted = torch.max(probabilities, dim=1)
            label = labels[predicted.item()]
            meaning = label_meanings.get(label, 'その他')
            score = scores.item()
            return {'label': meaning, 'score': score}
    except Exception as e:
        print(f"感情分析中にエラーが発生しました: 文: {sentence}")
        traceback.print_exc()
        return None

# 文分割関数の定義（fugashiを使用）
def split_sentences(text):
    tagger = Tagger()
    sentences = []
    current_sentence = ""
    for word in tagger(text):
        current_sentence += word.surface
        if word.surface in '。！？':  # 句点、感嘆符、疑問符で文を分割
            sentences.append(current_sentence)
            current_sentence = ""
    if current_sentence:
        sentences.append(current_sentence)
    return sentences

def clean_text(text):
    text = text.replace('\u3000', ' ')
    text = re.sub(r'[^\w\sぁ-んァ-ン一-龥。、！？.!?]', '', text)
    text = text.strip()
    return text

def get_member_list(base_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        print(f"\nメンバー一覧ページを取得中: {base_url}")
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        members = soup.select('ul.com-blog-circle li a')

        if not members:
            print("メンバーリストが取得できませんでした。サイト構造が変わった可能性があります。")
            return []

        member_links = []
        for member in members:
            name_tag = member.select_one('p.name')
            if not name_tag:
                continue
            member_name = name_tag.get_text().strip()
            member_url = f"https://sakurazaka46.com{member['href']}"
            member_links.append((member_name, member_url))

        if not member_links:
            print("メンバー名とURLが取得できませんでした。サイト構造が変わった可能性があります。")

        # デバッグ用: 取得したメンバーを表示
        print(f"取得したメンバー数: {len(member_links)}")
        for name, url in member_links:
            print(f"メンバー名: {name}, URL: {url}")

        return member_links

    except requests.RequestException as e:
        print("メンバー一覧ページの取得中にネットワークエラーが発生しました。")
        traceback.print_exc()
        return []
    except Exception as e:
        print("メンバー一覧取得中に予期せぬエラーが発生しました。")
        traceback.print_exc()
        return []

def scrape_blog_page(blog_url, output_file):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        print(f"\nブログページを取得中: {blog_url}")
        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()

        bs4_blog = BeautifulSoup(response.text, 'html.parser')
        article = bs4_blog.select_one('article.post')

        if not article:
            print(f"記事が見つかりませんでした: {blog_url}")
            return []

        content_div = article.select_one('div.box-article')
        if not content_div:
            print(f"本文が見つかりませんでした: {blog_url}")
            return []

        content_text = content_div.get_text(separator="\n", strip=True)
        content_text = clean_text(content_text)

        try:
            sentences = split_sentences(content_text)
        except Exception as e:
            print(f"文分割中にエラーが発生しました: {blog_url}")
            traceback.print_exc()
            return []

        if not sentences:
            print(f"この記事は本文が空か分割できませんでした: {blog_url}")
            return []

        # 各文について感情分析を実行
        results = []
        for sentence in sentences:
            if not sentence.strip():
                continue
            try:
                res = classify_emotion(sentence)
                if res:
                    results.append(res)
                    # ファイルに書き込む
                    output_file.write(f"文: {sentence}\n")
                    output_file.write(f"感情: {res['label']}, スコア: {res['score']}\n\n")
            except Exception as e:
                print(f"感情分析中にエラーが発生しました: {blog_url}, 文: {sentence}")
                traceback.print_exc()
                continue

        return results

    except requests.RequestException as e:
        print(f"記事ページの取得中にネットワークエラーが発生しました: {blog_url}")
        traceback.print_exc()
        return []
    except Exception as e:
        print(f"記事解析中に予期せぬエラーが発生しました: {blog_url}")
        traceback.print_exc()
        return []

def scrape_all_blogs(member_url, output_file):
    parsed_url = urlparse(member_url)
    query_params = parse_qs(parsed_url.query)
    ct_value = query_params.get('ct', [''])[0]
    ima_value = query_params.get('ima', ['0000'])[0]

    # 感情ラベル -> ポジ・ネガ・中立マッピング
    # 使用するモデルに応じてラベルを確認し、マッピングを調整してください
    # 以下はテスト結果に基づく仮のマッピングです。実際のラベルに基づいて調整してください。
    positive_labels = {'LABEL_0'}    # 喜び、幸福
    negative_labels = {'LABEL_1', 'LABEL_2'}    # 怒り、悲しみ
    neutral_labels = {'LABEL_3', 'LABEL_4', 'LABEL_5', 'LABEL_6', 'LABEL_7'}  # 驚き、中立、恐れ、疲労、その他

    # 集計用
    total_positive = 0.0
    total_negative = 0.0
    total_neutral = 0.0

    # 全ての結果を保存（オプション）
    all_results = []

    page_num = 0
    while True:
        page_url = f"https://sakurazaka46.com/s/s46/diary/blog/list?ima={ima_value}&page={page_num}&ct={ct_value}"
        print(f"\nページをスクレイピング中: {page_url}")

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(page_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"ページが存在しませんでした（ステータスコード:{response.status_code}）: {page_url}")
                break
        except requests.RequestException as e:
            print(f"ブログ一覧ページ取得中にネットワークエラーが発生しました: {page_url}")
            traceback.print_exc()
            break
        except Exception as e:
            print(f"ブログ一覧ページ取得中に予期せぬエラーが発生しました: {page_url}")
            traceback.print_exc()
            break

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('ul.com-blog-part li.box a')
            if not articles:
                print(f"ブログ記事が見つかりませんでした: {page_url}")
                break

            blog_links = []
            for article in articles:
                href = article.get('href', '')
                if href:
                    blog_link = f"https://sakurazaka46.com{href}"
                    blog_links.append(blog_link)

            if not blog_links:
                print(f"このページにはブログ記事がありません: {page_url}")
                break

            # 各ブログ記事を解析
            for blog_url in blog_links:
                print(f"\nブログをスクレイピング中: {blog_url}")
                results = scrape_blog_page(blog_url, output_file)
                # results: [{'label': emotion_label, 'score': score}, ...]
                all_results.extend(results)

                for res in results:
                    label = res['label'].upper()  # ラベルを大文字に統一
                    score = res['score']
                    if label in positive_labels:
                        total_positive += score
                    elif label in negative_labels:
                        total_negative += score
                    elif label in neutral_labels:
                        total_neutral += score
                    else:
                        # 不明なラベルは中立として扱う
                        total_neutral += score

                # 過剰なアクセス防止のためのスリープ
                time.sleep(random.uniform(2, 5))

            page_num += 1
            # 次のページへ行く前にスリープ
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"ブログ一覧解析中に予期せぬエラーが発生しました: {page_url}")
            traceback.print_exc()
            break

    return total_positive, total_negative, total_neutral

# Plotting the sentiment scores
def plot_sentiment(positive, negative, neutral):
    try:
        labels_plot = ['ポジティブ', 'ネガティブ', 'ニュートラル']
        scores = [positive, negative, neutral]
        colors = ['green', 'red', 'gray']

        plt.figure(figsize=(8, 6))
        bars = plt.bar(labels_plot, scores, color=colors)

        # 各バーの上にスコアを表示
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}', ha='center', va='bottom')

        plt.title('感情分析結果')
        plt.xlabel('感情')
        plt.ylabel('スコア合計')
        plt.ylim(0, max(scores) * 1.1)  # 上に少し余裕を持たせる

        plt.savefig('sentiment_analysis_results.png')  # グラフを画像として保存
        print("\n感情分析結果のグラフを 'sentiment_analysis_results.png' に保存しました。")
        plt.show()
    except Exception as e:
        print("感情分析結果のグラフ描画中にエラーが発生しました。")
        traceback.print_exc()

# メイン処理
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='指定されたメンバーのブログから感情分析を行います。')
    parser.add_argument('--member', type=str, help='メンバーの名前（漢字）を指定してください。')
    args = parser.parse_args()

    base_url = 'https://sakurazaka46.com/s/s46/diary/blog/list?ima=0000'
    member_list = get_member_list(base_url)

    if not member_list:
        print("メンバー一覧が取得できず、処理を中断します。")
        exit(1)

    print("\n取得したメンバー一覧:", member_list)

    if args.member:
        member_found = False
        for member_name, member_url in member_list:
            if member_name == args.member:
                member_found = True
                print(f"\nメンバーのブログを解析開始: {member_name}")

                # 出力ファイル名を生成
                output_filename = f"{member_name.replace(' ', '')}_EmotionAnalysis.txt"
                try:
                    with open(output_filename, 'w', encoding='utf-8') as output_file:
                        # scrape_all_blogsにoutput_fileを渡す
                        total_positive, total_negative, total_neutral = scrape_all_blogs(member_url, output_file)
                except Exception as e:
                    print(f"出力ファイルの作成中にエラーが発生しました: {output_filename}")
                    traceback.print_exc()
                    exit(1)

                total = total_positive + total_negative + total_neutral
                print("\n感情分析結果：")
                print(f"ポジティブスコア合計: {total_positive:.2f}")
                print(f"ネガティブスコア合計: {total_negative:.2f}")
                print(f"ニュートラルスコア合計: {total_neutral:.2f}")

                if total > 0:
                    positive_ratio = (total_positive / total) * 100
                    negative_ratio = (total_negative / total) * 100
                    neutral_ratio = (total_neutral / total) * 100
                    print(f"ポジティブ割合: {positive_ratio:.2f}%")
                    print(f"ネガティブ割合: {negative_ratio:.2f}%")
                    print(f"ニュートラル割合: {neutral_ratio:.2f}%")
                else:
                    print("スコアの合計が0のため、割合を計算できません。")

                # グラフを描画
                plot_sentiment(total_positive, total_negative, total_neutral)
                break
        if not member_found:
            print(f"指定されたメンバー名 '{args.member}' が見つかりませんでした。")
    else:
        print("メンバー名が指定されていません。--member 引数を使用してください。")
