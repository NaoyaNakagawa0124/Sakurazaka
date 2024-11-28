import os
import requests
from bs4 import BeautifulSoup
import time
import random
import argparse
from urllib.parse import urlparse, parse_qs
from transformers import pipeline
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からアクセストークンを取得（公開モデルを使用する場合は不要）
access_token = os.getenv('HF_ACCESS_TOKEN')

# 感情分析パイプラインの初期化
sentiment_analyzer = pipeline(
    'sentiment-analysis',
    model='koheiduck/bert-japanese-finetuned-sentiment',  # 使用するモデルを変更
    # モデルが公開されている場合、use_auth_tokenは不要です
    # 非公開モデルの場合は以下のコメントを外してください
    use_auth_token=access_token
)

# メンバー名とそのブログトップページのURLを取得する関数
def get_member_list(base_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    members = soup.select('ul.com-blog-circle li a')

    member_links = []
    for member in members:
        member_name = member.select_one('p.name').get_text().strip()
        member_url = f"https://sakurazaka46.com{member['href']}"
        member_links.append((member_name, member_url))

    return member_links

# 各ブログページをスクレイピングしてテキストを解析する関数
def scrape_blog_page(blog_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(blog_url, headers=headers)
        response.raise_for_status()

        bs4_blog = BeautifulSoup(response.text, 'html.parser')
        article = bs4_blog.select_one('article.post')

        if article:
            # ブログ本文のテキストを取得
            content_div = article.select_one('div.box-article')
            if content_div:
                content_text = content_div.get_text(strip=True)

                # 長いテキストの場合、モデルの最大入力長に合わせて分割
                max_length = 512  # モデルの最大入力長
                segments = [content_text[i:i+max_length] for i in range(0, len(content_text), max_length)]

                positive_score = 0
                negative_score = 0

                for segment in segments:
                    # 感情分析
                    result = sentiment_analyzer(segment)[0]
                    label = result['label']
                    score = result['score']
                    print(f"Segment: {segment[:30]}..., Label: {label}, Score: {score}")  # デバッグ用

                    # モデルのラベルに応じてスコアを累積
                    # ここでは一般的な例を示します。実際のラベル名はモデルのドキュメントを参照してください。
                    if label.lower() == 'positive':
                        positive_score += score
                    elif label.lower() == 'negative':
                        negative_score += score
                    # 他のラベルが存在する場合は追加の条件をここに記述

                return positive_score, negative_score
            else:
                print(f"本文が見つかりませんでした: {blog_url}")
                return 0, 0
        else:
            print(f"記事が見つかりませんでした: {blog_url}")
            return 0, 0

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 0, 0

# メンバーごとの全ブログをスクレイピングして解析
def scrape_all_blogs(member_url):
    # メンバーのct値を取得
    parsed_url = urlparse(member_url)
    query_params = parse_qs(parsed_url.query)
    ct_value = query_params.get('ct', [''])[0]
    ima_value = query_params.get('ima', ['0000'])[0]

    total_positive = 0
    total_negative = 0

    page_num = 0
    while True:
        # ページURLを構築
        page_url = f"https://sakurazaka46.com/s/s46/diary/blog/list?ima={ima_value}&page={page_num}&ct={ct_value}"
        print(f"ページをスクレイピング中: {page_url}")

        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(page_url, headers=headers)
        if response.status_code != 200:
            print(f"ページが存在しませんでした: {page_url}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # ブログ記事のURLを取得
        blog_links = []
        articles = soup.select('ul.com-blog-part li.box a')
        for article in articles:
            blog_link = f"https://sakurazaka46.com{article['href']}"
            blog_links.append(blog_link)

        if not blog_links:
            print(f"ブログ記事が見つかりませんでした: {page_url}")
            break

        # 各ブログ記事をスクレイピングして解析
        for blog_url in blog_links:
            print(f"ブログをスクレイピング中: {blog_url}")
            pos_score, neg_score = scrape_blog_page(blog_url)
            total_positive += pos_score
            total_negative += neg_score
            time.sleep(random.uniform(2, 5))

        # 次のページへ
        page_num += 1
        time.sleep(random.uniform(2, 5))

    return total_positive, total_negative

# メイン処理
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='指定されたメンバーのブログから感情分析を行います。')
    parser.add_argument('--member', type=str, help='メンバーの名前（漢字）を指定してください。')
    args = parser.parse_args()

    base_url = 'https://sakurazaka46.com/s/s46/diary/blog/list?ima=0000'
    member_list = get_member_list(base_url)

    # メンバーが指定されている場合
    if args.member:
        for member_name, member_url in member_list:
            if member_name == args.member:
                print(f"メンバーのブログを解析開始: {member_name}")
                total_positive, total_negative = scrape_all_blogs(member_url)

                # 結果の表示
                total_score = total_positive + total_negative
                print("\n感情分析結果：")
                print(f"ポジティブスコア合計: {total_positive:.2f}")
                print(f"ネガティブスコア合計: {total_negative:.2f}")

                if total_score > 0:
                    positive_ratio = (total_positive / total_score) * 100
                    negative_ratio = (total_negative / total_score) * 100
                    print(f"ポジティブ割合: {positive_ratio:.2f}%")
                    print(f"ネガティブ割合: {negative_ratio:.2f}%")
                else:
                    print("スコアの合計が0のため、割合を計算できません。")
                break
        else:
            print(f"指定されたメンバー名 '{args.member}' が見つかりませんでした。")
    else:
        print("メンバー名が指定されていません。--member 引数を使用してください。")
