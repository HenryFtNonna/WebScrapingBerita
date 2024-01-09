from flask import Flask, render_template
import requests as req
from bs4 import BeautifulSoup as bs
import csv
import pandas as pd

app = Flask(__name__)

hades = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}

# Your scraping function here
def scrape_detik(hal):
    global hades
    results = []
    a = 1
    for page in range(1, hal):
        url = f'https://www.detik.com/search/searchnews?query=pemilu+2024&sortby=time&page={page}'
        ge = req.get(url, hades).text
        sop = bs(ge, 'lxml')
        li = sop.find('div', class_='list media_rows list-berita')
        lin = li.find_all('article')
        for x in lin:
            link = x.find('a')['href']
            date = x.find('a').find('span', class_='date').text.replace('WIB', '').replace('detikNews', '').split(',')[1]
            headline = x.find('a').find('h2').text
            ge_ = req.get(link, hades).text
            sop_ = bs(ge_, 'lxml')
            content = sop_.find_all('div', class_='detail__body-text itp_bodycontent')
            for x in content:
                x = x.find_all('p')
                y = [y.text for y in x]
                content_ = ''.join(y).replace('\n', '').replace('ADVERTISEMENT', '').replace('SCROLL TO RESUME CONTENT', '')
                result = {'headline': headline, 'date': date, 'link': link, 'content': content_}
                results.append(result)
                print(f'done[{a}] > {headline[0:10]}')
                a += 1
                with open('politik.csv', 'a') as file:
                    wr = csv.writer(file, delimiter=',')
                    wr.writerow([headline, date, link, content_])
    return results

# Route to trigger scraping
@app.route('/scrape')
def run_scraping():
    results = scrape_detik(3)
    return render_template('index.html', results=results)

# Route to display the data
@app.route('/')
def show_data():
    # Read the CSV file into a DataFrame
    df = pd.read_csv('politik.csv')
    # Convert DataFrame to HTML table
    table_html = df.to_html(classes='table table-striped', index=False)
    return render_template('index.html', table_html=table_html)

if __name__ == '__main__':
    app.run(debug=True)
 