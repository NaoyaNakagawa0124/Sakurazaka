import os
import requests
from bs4 import BeautifulSoup
from pykakasi import kakasi
from PIL import Image
from io import BytesIO
import time
import random
import argparse
from urllib.parse import urlparse, parse_qs

# pykakasiの設定
kks = kakasi()
conv = kks.getConverter()

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

# 各ブログページをスクレイピングして画像を保存する関数
def scrape_blog_page(blog_url, member_name_rome, save_dir):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(blog_url, headers=headers)
        response.raise_for_status()

        bs4_blog = BeautifulSoup(response.text, 'html.parser')
        articles = bs4_blog.select('article.post')

        for article in articles:
            # 日付の取得
            year_element = article.find('span', {'class': 'ym-year'})
            month_element = article.find('span', {'class': 'ym-month'})
            day_element = article.find('p', {'class': 'date wf-a'})

            if year_element and month_element and day_element:
                year = year_element.get_text().strip()
                month = month_element.get_text().strip().zfill(2)
                day = day_element.get_text().strip().zfill(2)
                date = f"{year}/{month}/{day}"
            else:
                date = "unknown_date"

            # 画像の取得
            img_elements = article.select('div.box-article img')
            if img_elements:
                img_counter = 1
                for img in img_elements:
                    src = img.get('src')
                    if not src:
                        continue
                    img_url = f'https://sakurazaka46.com{src}'
                    img_name = f"{member_name_rome}_{date.replace('/', '_')}_{img_counter}.png"
                    img_path = os.path.join(save_dir, img_name)

                    # ファイルが既に存在する場合はスキップ
                    if os.path.exists(img_path):
                        print(f"既に存在するためスキップ: {img_path}")
                    else:
                        img_response = requests.get(img_url)
                        if img_response.status_code == 200:
                            img_data = Image.open(BytesIO(img_response.content))
                            if img_data.mode == "RGBA":
                                img_data = img_data.convert("RGB")
                            new_size = (img_data.width * 2, img_data.height * 2)
                            img_resized = img_data.resize(new_size, Image.LANCZOS)
                            img_resized.save(img_path, format="PNG")
                            print(f"画像を保存: {img_path}")
                        else:
                            print(f"画像のダウンロードに失敗: {img_url}")

                    img_counter += 1
                    time.sleep(random.uniform(2, 5))
            else:
                print(f"画像が見つかりませんでした: {blog_url}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# メンバーごとの全ブログをスクレイピング
def scrape_all_blogs(member_url, member_name_rome, member_name_kanji):
    # メンバーのct値を取得
    parsed_url = urlparse(member_url)
    query_params = parse_qs(parsed_url.query)
    ct_value = query_params.get('ct', [''])[0]
    ima_value = query_params.get('ima', ['0000'])[0]

    save_dir = os.path.join('data', member_name_kanji)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

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

        # 各ブログ記事をスクレイピング
        for blog_url in blog_links:
            print(f"ブログをスクレイピング中: {blog_url}")
            scrape_blog_page(blog_url, member_name_rome, save_dir)
            time.sleep(random.uniform(2, 5))

        # 次のページへ
        page_num += 1
        time.sleep(random.uniform(2, 5))

# メイン処理
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='指定されたメンバーのブログから写真を収集します。')
    parser.add_argument('--member', type=str, help='メンバーの名前（漢字）を指定してください。')
    args = parser.parse_args()

    base_url = 'https://sakurazaka46.com/s/s46/diary/blog/list?ima=0000'
    member_list = get_member_list(base_url)

    # メンバーが指定されている場合
    if args.member:
        for member_name, member_url in member_list:
            if member_name == args.member:
                member_name_rome = conv.do(member_name)  # ローマ字に変換
                scrape_all_blogs(member_url, member_name_rome, member_name)
                break
        else:
            print(f"指定されたメンバー名 '{args.member}' が見つかりませんでした。")
    else:
        print("メンバー名が指定されていません。--member 引数を使用してください。")
