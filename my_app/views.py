from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from requests.compat import quote_plus
from . import models
import io
import json

BASE_URL = 'https://sg.carousell.com/search/products/?query={}'

def home(request):
    return render(request, 'base.html')

def new_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search)
    response = requests.get(BASE_URL.format(quote_plus(search)))
    full_html = response.text
    soup = BeautifulSoup(full_html,"lxml")

    ### Finding the images ###
    data = soup.select('script', type='application/ld+json')[4]
    new_data = str(data)
    new_data_2 = new_data[28:-9]
    test_json = json.loads(new_data_2)
    test_json_1 = test_json["SearchListing"]["listingCards"]

    # list of thumbnail URLS
    write_json= []
    for each in test_json_1:
        write_json.append(each["thumbnailURL"])

    # dict of listing id with URLs
    thumbnailURL_dict = {}
    for each in write_json:
        each2 = each.split("_")[1]
        thumbnailURL_dict[each2] = each
    
    ### start post-parsing
    final_postings = []
    post_listings = soup.find_all("div", {"class":"styles__cardContent___TpQXu"})
    for i in post_listings:
        post_title = i.find('p', {'class':'styles__text___1gJzw styles__colorUrbanGrey60___2rwkI styles__overflowNormal___mT74G styles__singleline___nCFol styles__textAlignLeft___lqg5e styles__weightSemibold___uxIDP desktop__sizeS___30RAN'}).text
        for each in i.find_all('a',{'class':'styles__link___9msaS'}):
            if len(each['class']) != 1:
                continue
            else:
                post_url = 'https://sg.carousell.com' + each.get('href')
                pass
        post_price = i.find('p', {'class':'styles__text___1gJzw styles__colorUrbanGrey60___2rwkI styles__overflowNormal___mT74G styles__singleline___nCFol styles__textAlignLeft___lqg5e styles__weightRegular___19l6i desktop__sizeM___3k5LI'}).text
        post_image_url = thumbnailURL_dict[post_url.split('?')[0][-9:]]
        final_postings.append((post_title, post_price, post_url, post_image_url))

    # # list of listing ID according to the tiles
    # results = []
    # for each in soup.find_all('div', attrs={'class': 'styles__cardContent___TpQXu'}):
    #     for item in each.find_all('a', attrs = {'class': 'styles__link___9msaS'}):
    #         if len(item["class"]) != 1:
    #             continue
    #         else:
    #             results.append(item.get('href'))

    # results2 = []
    # for each in results:
    #     each = each.split('?')
    #     each = each[0]
    #     each = each[-9:]
    #     results2.append(each)

    # # matching them together
    # master_dict = {}
    # for each in results2:
    #     master_dict[each] = thumbnailURL_dict[each]
        

    stuff_for_frontend = {'search': search, 'final_postings': final_postings}
    return render(request, 'my_app/new_search.html', stuff_for_frontend)
