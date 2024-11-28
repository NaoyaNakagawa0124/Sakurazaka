import requests
import bs4
import os
from pykakasi import kakasi

url = 'https://sakurazaka46.com/s/s46/diary/detail/57068?ima=0000&cd=blog'

responce = requests.get(url)

responce.raise_for_status()

bs4_blog = bs4.BeautifulSoup(responce.text, 'html.parser')

article = bs4_blog.select('.p-blog-article')

last_day = 0
No = 0

for j in range(len(article)):
    date = article[j].find('div', {'class': 'c-blog-article__date'}).get_text().strip()
    date = date.split()[0]

    year = date.split('.')[0]
    month = date.split('.')[1]
    day = date.split('.')[2]

    label = name_rome[9] + '_' + year + '_' + month.zfill(2) + '_' + day.zfill(2) + '_'

    img = article[j].select('img')

    if day == last_day:
        pass
    else:
        No = 0

    last_day = day

    for i in range(len(img)):
        src = img[i].get('src')

        file_name = label + str(No).zfill(2)

        No = No + 1

        fg = True
        if '.jpg' in src or '.jpeg' in src:
            file_name = file_name + '.jpeg'
        elif '.png' in src:
            file_name = file_name + '.png'
        else:
            print(src)
            fg = False

        path = os.path.join('data', name_kanji[9], file_name)

        if not os.path.isfile(path) and fg:
            responce = requests.get(src)
            time.sleep(1)

            if responce.status_code == 200:
                print(file_name)
                with open(path, "wb") as f:
                    f.write(responce.content)
            else:
                print('False', responce.status_code, src)