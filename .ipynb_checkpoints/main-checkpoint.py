import requests
from bs4 import BeautifulSoup
import csv
import re


def scrape_books(base_url, maxDepth=3):
    base_url = base_url.replace('/index.html', '')
    books = []
    for page in range(1, maxDepth+1):
        if re.match(r'https://books\.toscrape\.com/catalogue', base_url):
            url = f"{base_url}/page-{page}.html"
        else:
            url = f"{base_url}/catalogue/page-{page}.html"
        print(f"Scraping page {page}...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            soup.prettify()
            product_pods = soup.find_all('article', class_='product_pod')
            for book in product_pods:
                title = book.h3.a['title']
                rating = book.find('p', class_='star-rating')['class'][1]
                price = book.find('p', class_='price_color').text
                availability = book.find('p', class_='instock availability').text.strip()
                book_url = f"{base_url}/catalogue/{book.h3.a['href']}"

                books.append({
                    'title': title,
                    'rating': rating,
                    'price': price,
                    'availability': availability,
                    'url': book_url
                })
        except requests.exceptions.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            continue
    print(f"Total Books Scraped: {len(books)}\n")
    return books


def save_to_csv(books, file='books.csv'):
    if not books:
        print("No books to save!")
        return
    else:
        with open(file, 'w', newline='', encoding='utf-8',) as f:
            writer = csv.DictWriter(f, fieldnames=books[0].keys())
            writer.writeheader()
            writer.writerows(books)

    print(f"Saved {len(books)} books to {file}")


def main():
    pageToScrape = input("Welcome to the (books.toscrape.com) catalouge WebScraper\nPlease enter a link:")
    if not re.match(r'https://books\.toscrape\.com', pageToScrape):
        raise ValueError('''Not a valid page for the purposes of this scraper
        make sure it\'s a catalogue page from https://books.toscrape.com''')

    depth = int(input("Please enter the number of pages to scrape:"))
    if not isinstance(depth, int) or depth % 1 != 0 or depth <= 0:
        raise ValueError('Not a valid positive integer')

    print("Valid url recieved proceeding to scrape the page" + '.' * 16 + '\n' + '=' * 32 + '\n')
    scraped = scrape_books(pageToScrape, depth)
    while 1:
        switch = input(
            "(s,S):save to csv    (d,D):display content    (q,Q)Quit program:")
        match switch:
            case 's' | 'S':
                file = input('Enter file name(or full path): ')
                save_to_csv(scraped, file)
            case 'd' | 'D': print(scraped)
            case 'q' | 'Q': return
            case _: pass

main()