import requests
from bs4 import BeautifulSoup
import genanki
import os

MODEL_ID = 1325114336
DECK_ID = 2058260461

cocktail_model = genanki.Model(
    MODEL_ID,
    'Cocktail',
    fields=[
      {'name': 'Name'},
      {'name': 'Recipe'},
      {'name': 'MainImage'},
      ],
    templates=[
      {
        'name': 'Cocktail Card',
        'qfmt': '{{Name}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Recipe}}{{MainImage}}',
      },
    ]
  )

cocktail_deck = genanki.Deck(DECK_ID, 'IBA Cocktails')
# they block the requests user agent
headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0' }

# request index
index_req = requests.get('https://iba-world.com/category/iba-cocktails/', headers=headers)
index_html = index_req.text

# parse index
main_soup = BeautifulSoup(index_html, 'html.parser')
articles_html = main_soup.find_all('article')
articles_links = map(lambda a: a.find("a").get("href"), articles_html)

media_files = []

# request all articles
for l in articles_links:
  cocktail_req = requests.get(l, headers=headers)
  # parse
  cocktail_soup = BeautifulSoup(cocktail_req.text, 'html.parser')

  # get name
  cocktail_name = cocktail_soup.find("title").string.replace(" - iba-world.com", "")
  print(cocktail_name)

  # image
  image_link = cocktail_soup.find(lambda x: x.has_attr("property") and x.get("property") == "og:image").get("content")

  cocktail_img = image_link.split("/")[-1]
  # download if not exists
  if not os.path.exists(f"imgs/{cocktail_img}"):
    with open(f"imgs/{cocktail_img}", "wb") as i:
      image_req = requests.get(image_link, headers=headers)
      i.write(image_req.content)
      i.close()
  media_files.append(f"imgs/{cocktail_img}")

  tags_div = cocktail_soup.find("div", class_="et_pb_title_container")
  tags = map(lambda a: a.string.replace(" ", ""), tags_div.find_all("a"))

  content_div = cocktail_soup.find("div", class_="blog-post-content")
  # FIXME?
  cocktail_recipe = str(content_div)

  cocktail_note = genanki.Note(
      model=cocktail_model,
      fields=[cocktail_name, cocktail_recipe, f"<img src=\"{cocktail_img}\">"],
      tags=tags)

  cocktail_deck.add_note(cocktail_note)

# write out package
cocktail_package = genanki.Package(cocktail_deck)
cocktail_package.media_files = media_files

cocktail_package.write_to_file('iba-cocktails.apkg')
