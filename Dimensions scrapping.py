# -*- coding: utf-8 -*-
"""
@author: Juan Andrés Cabral
You can reach me at: juan.drs.c@gmail.com
"""

# Packages
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import pandas as pd
import requests 
import time



save_path="" # Path where csv will be saved
driver = webdriver.Chrome(" ") # Chrome driver path
url_list=[''] # All urls lists 
# Example of URL:  https://app.dimensions.ai/discover/publication?or_facet_source_title=jour.1018957


# Main code:
for searchurls in url_list:  
    url = searchurls
    
    # Number of results
    driver.get(url)
    page = requests.get(url)
    html = driver.page_source 
    soup = BeautifulSoup(html)
    
    resultsnumber=int(soup.find('div',{'class':'sc-6lq5t8-13 jjoHIn'}).text.replace(',',''))
    no_of_pagedowns = resultsnumber/2 # This one depends on the speed of browser to load all the page
    # Load all the results via scrolling down
    
    soup = BeautifulSoup(page.content, 'html.parser')
    elem = driver.find_element_by_tag_name("html")
    
    while (no_of_pagedowns>0):
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(.7)
        no_of_pagedowns-=1
        print('Scroll down left:',no_of_pagedowns)

    # Extract urls from papers
    
    html = driver.page_source 
    soup = BeautifulSoup(html)
    
    url_abstracts = []
    data = soup.findAll('article',attrs={'class':'n0bn8v-6 cBNkjo resultList__item','data-bt':'publication_result_item'})
    for elm in data:
        link = elm.find('a',{'class':'w3owpf-0 einqZr w3owpf-1 z0mrsy-0 hRtMMp resultList__item__title__primary'}).get("href")
        link = "https://app.dimensions.ai"+link
        url_abstracts.append(link)
        
    print("Urls found:", len(url_abstracts))
    # Sometimes dimensions list the same article multiple times
    # Check duplications and delete them
    
    # Duplicate values
    duplicates=len(url_abstracts)==len(set(url_abstracts))
    duplicatesnumber=len(url_abstracts)-len(set(url_abstracts))
    if duplicates == False:
        print(duplicatesnumber, "Duplicates values found")
    else:
        print("No duplicates values found")
    # Show duplicates
    import collections 
    print([item for item, count in collections.Counter(url_abstracts).items() if count > 1])
    
    # Drop duplicates
    d_url_abstracts=url_abstracts
    url_abstracts = list(dict.fromkeys(url_abstracts))
    # Extract titles, abstracts, journal
    abstracts=[]
    titles=[]
    journal=[]
    citations=[]
    authors=[]
    institution=[]
    nauthors=[]
    counter=0
    for paper in url_abstracts:
        # Iterate for each paper/url
        counter+=1
        url = paper
        driver.get(url)
        html = driver.page_source 
        soup = BeautifulSoup(html) 
        
        # Abstracts
        data1 = soup.findAll('div',attrs={'class':'sc-1vq0mqb-0 jiOUXH'})
        for elm in data1:
            abs_text = elm.find('p',{'class':'sgay21-1 FqKVk'}).text
        abstracts.append(abs_text)
        abs_text='none' # Some articles don't have abstracts
        # Title and journal
        data2 = soup.findAll('div',attrs={'class':'details_title'})
        for elm in data2:
            tit_text = elm.find('h1',{'data-bt':'details-title', 'class':'sc-10se207-0 hfRwDd'}).text
            jour_text=elm.find('a',{'class':'w3owpf-0 einqZr w3owpf-1 z0mrsy-0 hRtMMp'}).text 
            
        titles.append(tit_text)
        journal.append(jour_text)
       
        # Citations
        cit = soup.find('span',{'class':'__dimensions_Badge_stat_count'})
        if cit is None:
            cit='none'
        else:
            cit=str(cit) # Transform to str to slice for numbers of citations
            cit=cit[44:] # Keep only number of citations
            cit=cit[:-7] # Keep only number of citations
        citations.append(cit)
        # Authors and institutions
        auth_text=soup.find_all('div',{'class':'s46ce1-0 bGKWPk'}) # Authors and institution are in the same class
        if len(auth_text)==0: # Sometimes the html is different  # THIS SECTION NEEDS WORK
            allauthors='none'
            alluniv='none'
        else: 
            alluniv=''
            allauthors=''
            for i in range(len(auth_text)): # Iterate and separate authors from institutions
                authorn=auth_text[i].text.split(' - ')[0]
                try: # Some articles doesn't have information about authors' institution
                    univn=auth_text[i].text.split(' - ')[1] 
                except:
                    univn='none'
                if i ==0:
                    allauthors=allauthors+authorn
                    alluniv=alluniv+univn
                else:
                    allauthors=allauthors+' - '+authorn
                    alluniv=alluniv+' - '+univn
        nauthors.append(len(auth_text)) # Number of authors
        authors.append(allauthors)
        institution.append(alluniv)
    
        time.sleep(1) # Wait to avoid being blocked by many requests
        if counter==len(url_abstracts):
            print("Finished")
        else:
            continue
        # Save data in csv
    papers = {'title':titles,'abstract':abstracts,'journal':journal,'authors':authors,
              'nauthors':nauthors,'institution':institution,'citation':citations}
    
    df = pd.DataFrame(data=papers)
    path=save_path+journal[0]+".csv"
    df.to_csv(path_or_buf=path,sep=',', na_rep='', float_format=None, 
              columns=None, header=True, index=False, index_label=None)
    time.sleep(10) # Wait to avoid being blocked by many requests
    

