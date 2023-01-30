# IMPORTS
import requests
import re
import sqlite3
import pandas as pd
import seaborn as sns
import logging
import os
import numpy as np

from sqlalchemy   import create_engine
from datetime     import datetime
from bs4          import BeautifulSoup


# Data extract - first Showcase

def get_showcase(url, header):
    
    # API Request - GET
    page = requests.get(url, headers = header)
    
    # Beautiful Soup object
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # Product Data
    products = soup.find('ul', class_ = 'products-listing small')
    product_list = products.find_all('article', class_ = "hm-product-item") 

    # product_id
    product_id = [p.get('data-articlecode') for p in product_list]

    # product_category
    product_category = [p.get('data-category') for p in product_list]

    # product_name
    products_list_aux = products.find_all('a', class_ = 'link')
    product_name = [p.get_text('title') for p in products_list_aux]

    # product_price
    product_list = products.find_all('span', class_ = 'price regular')
    product_price = [p.get_text()for p in product_list]


    # Product Data to dataframe
    df_showcase = pd.DataFrame([product_id, product_category, product_name, product_price]).T
    df_showcase.columns = ['product_id','product_category','product_name','product_price']

    ## scrapy_datetime
    df_showcase['scrapy_datetime'] = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )
    
    return df_showcase



# Data extract by product - Each product of this showcase

def get_all_product_details(data, header):
        
    # empty DataFrame to receive all items 
    df_all_product_details = pd.DataFrame()

    # aux dataframe to assert the correct scrap
    df_pattern = pd.DataFrame(columns=['Art. No.','Composition','Fit','Size', 'product_name','product_price'])

    # aux list to assert no different 
    aux = []

    for i in range(len(data)): 
    # for each item of showcase, enter at item and collect the details!
        url = 'https://www2.hm.com/en_us/productpage.'+ data.loc[i,'product_id']+'.html'
        logger.debug ('Product: %s',url)

        # API Request
        page = requests.get(url,headers=header)

        # page.text #doctypeHTML

        
        # Beautiful Soup object
        soup = BeautifulSoup(page.text, 'html.parser')


        # --Product List
        product_list = soup.find_all('a', class_ = "filter-option miniature active") + soup.find_all('a', class_ = "filter-option miniature") 
        # each miniature of color pants contains the tag with respective values, being one for active item and others tags for inactivate 

        # color_name
        color_name = [p.get('data-color') for p in product_list]

        # product_id    
        product_id = [p.get('data-articlecode') for p in product_list]

        # --Concat color_name and product_id to Dataframe
        df_color = pd.DataFrame([product_id, color_name]).T
        df_color.columns = ['product_id','color_name']


        for j in range(len(df_color)):

            # API Request
            url = 'https://www2.hm.com/en_us/productpage.'+ df_color.loc[j,'product_id']+'.html'
            logger.debug('Color: %s',url)

            page = requests.get(url, headers = header)

            # Beautiful Soup object
            soup = BeautifulSoup(page.text,'html.parser')

            # --product_name
            product_name = soup.find_all('h1')[0]
            product_name = product_name.get_text()

            # --product_price
            product_price = soup.find_all('div', class_= "primary-row product-item-price")[0].get_text()
            product_price = re.findall(r'\d+\.?\d+', product_price)[0]

            # --product_details (size_model, fit, composition, art.no)
            product_details_list = soup.find_all('div', class_ = "content pdp-text pdp-content")[0].find('dl').find_all('div')
            product_details = [list(filter(None,p.get_text().split('\n'))) for p in product_details_list]

            # product_details to DataFrame
            df_details = pd.DataFrame(product_details).T
            df_details.columns = df_details.iloc[0]

            # delete first row of df_details
            df_details = df_details.iloc[1:]

            # fillna in Size, Fit and Art.No with the same value,
            df_details = df_details.fillna(method='ffill')

            # remove Shell:, Pocket Lining:, Lining:, Pocket:
            df_details['Composition'] = df_details['Composition'].str.replace('Shell:', '', regex=True)
            df_details['Composition'] = df_details['Composition'].str.replace('Pocket lining:', '', regex=True)
            df_details['Composition'] = df_details['Composition'].str.replace('Lining:', '', regex=True)
            df_details['Composition'] = df_details['Composition'].str.replace('Pocket:', '', regex=True)
            # //the percentage of components was abstracted. To find the components apply df_details['Composition'].unique on df done

            # add product_price and product_name to df_details
            df_details['product_price'] = product_price
            df_details['product_name'] = product_name


            # garantee the same columns between product_details and a pattern, and sort the labels
            df_details = pd.concat([df_pattern,df_details], axis=0)
            # //if it has some difference, a new column will appear with some Nan

            # rename the columns to lower case
            df_details.columns = df_details.columns.map(str.lower)
            df_details = df_details.rename(columns={'art. no.':'product_id'})
    #         df_details.columns = ['']


            # if some strange column appear, keep it and shows
            aux = aux + df_details.columns.to_list()
            if len(set(aux)) != len(df_pattern.columns):
                print('Some column does not fit with pattern!')
                pass

            # merge df_color and df_details of one item (single product_id)
            df_details = pd.merge(df_details, df_color, how='left', on='product_id')

            # add to list of all items
            df_all_product_details = pd.concat([df_all_product_details, df_details])


    # generate style_ID + color_ID
    df_all_product_details ['style_ID'] = df_all_product_details['product_id'].apply(lambda x: x[:-3])
    df_all_product_details ['color_ID'] = df_all_product_details['product_id'].apply(lambda x: x[-3:])

    ## scrapy_datetime
    df_all_product_details['scrapy_datetime'] = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )

    return df_all_product_details



# Data transform - cleaning the data

def data_cleaning (data):

    # product_id

    # product_name
    data['product_name'] = data.loc[:,'product_name'].apply(lambda x: x.replace(' ','_').lower())

    #product_fit
    data['fit'] = data.loc[:,'fit'].apply(lambda x: x.replace(' ','_').lower())

    #color_name
    data['color_name'] = data.loc[:,'color_name'].apply(lambda x: x.replace(' ','_').lower())

    #size_number
    data['size_number'] = data['size'].apply(lambda x: re.search('\d{3}cm', x).group(0) if pd.notnull(x) else x)
    data['size_number'] = data['size_number'].apply(lambda x: re.search('\d+', x).group(0) if pd.notnull(x) else x)

    #size_model 
    data['size_model'] = data['size'].str.extract('(\d+/\d+)')



    # df1_composition outuput of break in columns of each item of 'composition' separated by a comma
    df_composition = data['composition'].str.split(',', expand = True).reset_index(drop=True)

    # df_aux to storage each kind of composition in a separated column 
    df_aux = pd.DataFrame(index = np.arange(len(data)), columns = ['cotton','spandex','polyester','elastomultiester'])



    # --composition: cotton
    df_cotton_0 = df_composition.loc[df_composition[0].str.contains('Cotton', na=True), 0]
    df_cotton_0.name = 'cotton'
    df_cotton_1 = df_composition.loc[df_composition[1].str.contains('Cotton', na=True),1]
    df_cotton_1.name = 'cotton'

    df_cotton = df_cotton_0.combine_first(df_cotton_1)

    df_aux = pd.concat ([df_aux, df_cotton],axis=1)
    df_aux = df_aux.iloc[:, ~df_aux.columns.duplicated(keep='last')]

    # --composition: spandex

    df_spandex_0 = df_composition.loc[df_composition[1].str.contains('Spandex', na=True),1]
    df_spandex_0.name = 'spandex'
    df_spandex_1 = df_composition.loc[df_composition[2].str.contains('Spandex', na=True),2]
    df_spandex_1.name = 'spandex'

    df_spandex = df_spandex_0.combine_first(df_spandex_1)

    df_aux = pd.concat([df_aux, df_spandex], axis=1)
    df_aux = df_aux.iloc[:, ~df_aux.columns.duplicated(keep='last')]

    # --composition: polyester

    df_polyester = df_composition.loc[df_composition[0].str.contains('Polyester', na=True),0]
    df_polyester.name = 'polyester'

    df_aux = pd.concat([df_aux, df_polyester], axis=1)
    df_aux = df_aux.iloc[:, ~df_aux.columns.duplicated(keep='last')]


    # --composition: elastomultiester

    df_elastomultiester = df_composition.loc[df_composition[1].str.contains('Elastomultiester', na=True),1]
    df_elastomultiester.name = 'elastomultiester'

    df_aux = pd.concat([df_aux, df_elastomultiester], axis=1)
    df_aux = df_aux.iloc[:, ~df_aux.columns.duplicated(keep='last')]

    # add product_id to df_aux
    df_aux = pd.concat([data.loc[:,'product_id'].reset_index(drop=True),df_aux], axis=1)


    #format composition 
    df_aux['cotton'] = df_aux['cotton'].apply(lambda x: int(re.search('\d+',x).group(0)) /100 if pd.notnull(x) else x)
    df_aux['polyester'] = df_aux['polyester'].apply(lambda x: int(re.search('\d+',x).group(0))/100 if pd.notnull(x) else x)
    df_aux['spandex'] = df_aux['spandex'].apply(lambda x: int(re.search('\d+',x).group(0))/100 if pd.notnull(x) else x)
    df_aux['elastomultiester'] = df_aux['elastomultiester'].apply(lambda x: int(re.search('\d+',x).group(0))/100 if pd.notnull(x) else x)

    #final join
    df_aux = df_aux.groupby('product_id').max().reset_index().fillna(0)
    data = pd.merge(data, df_aux, on = 'product_id', how = 'left')


    # drop columns 
    data = data.drop(columns = ['size', 'composition'])

    # drop duplicates
    data = data.drop_duplicates()
    
    # df_raw receives the clean data
    df_raw = data
    
    return df_raw


# Data load - load to a sqlite3 database

def data_load (data, path):
    
    # Create data_insert from df with adjusts at orders of columns
    data_insert = data[[
        'product_id',
        'style_ID', 
        'color_ID', 
        'product_name',
        'color_name',
        'fit',
        'product_price', 
        'size_number', 
        'size_model',
        'cotton', 
        'spandex', 
        'polyester', 
        'elastomultiester',
        'scrapy_datetime' 
    ]]

    # Create database connection
    conn = create_engine('sqlite:///'+ path + '/data/raw/db_hm.sqlite')

    # Data Insert
    data_insert.to_sql('vitrine', con = conn, if_exists = 'append', index=False)
    
    return None




if __name__ == "__main__":
    
    path = '../../'
    
    if not os.path.exists (path + 'Logs'):
        os.mkdir(path+'Logs')
        
    logging.basicConfig(
        filename = path + 'Logs/webscrapping_hm.log',
        level = logging.DEBUG, 
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger ('webscrapping_hm')

    # parameters
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'

    header = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    
    # Data extract
    df_showcase = get_showcase (url, header)
    logger.info ('data extract done')

    
    # Data extract by product
    df_all_product_details = get_all_product_details (df_showcase, header)
    logger.info ('data extract by product done')
    
    # Data tranform
    df_raw = data_cleaning (df_all_product_details)
    logger.info ('data transform done')
    
    # Data load
    data_load(df_raw, path)
    logger.info ('data load done')
