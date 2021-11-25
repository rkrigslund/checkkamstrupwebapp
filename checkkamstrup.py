#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 22:45:16 2021

@author: rkr
"""
import pandas as pd
import requests
import streamlit as st

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

kamstrup_man_ids = pd.Series(['KAM','KAW','KAH','KAS'])

serial = st.number_input('Type a serial to test on check.kamstrup.com:', min_value=0, max_value=99999999)
man_ids = st.multiselect('Select applicable Manufacturer IDs', options=['KAM','KAW','KAH','KAS'], default=kamstrup_man_ids.to_list())


url=f'https://rs-app.kamstrup.com/product_centric/connection_overview/v1/{serial}?listOfManufacturerIDs={",".join(man_ids)}'

#71256409

req = requests.get(url)
json_obj = req.json()

if 'message' in json_obj:
    st.write(json_obj['message'])
else:
    #PRODUCT
    st.markdown(f"{json_obj['productClass'].capitalize()} product: **{json_obj['serialNumber']}{json_obj['manufacturerID']}**")
    st.markdown(f"Last contact: **{str(pd.to_datetime(json_obj['informationTimestamp'], unit='s', utc=True))}**")
    
    #LINKS
    full_links = pd.DataFrame(json_obj['links'])
    links = full_links.loc[full_links.manufacturerID.isin(kamstrup_man_ids)]
    
    links.informationTimestamp = pd.to_datetime(links.informationTimestamp, unit='s', utc=True)
    st.markdown(f"Links: **{links.shape[0]}**")
    # Show the table
    links_to_web = links[['serialNumber', 'manufacturerID', 'productClass', 'informationTimestamp', 'rssi']]
    links_to_web.rename(columns={'serialNumber': 'Serial',
                                 'manufacturerID': 'Manufacturer ID',
                                 'productClass': 'Product class',
                                 'informationTimestamp': 'Timestamp',
                                 'rssi': 'RSSI'}, inplace=True)
    st.dataframe(links_to_web, 1024, 800)
    csv = convert_df(links_to_web)
    st.download_button(label="Download data as CSV",
                       data=csv,
                       file_name=f'links_for_{serial}.csv',
                       mime='text/csv')