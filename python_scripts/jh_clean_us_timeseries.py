#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime


# In[2]:


jh_us_cases_path = "../johns_hopkins_data/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
jh_us_deaths_path = "../johns_hopkins_data/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
jh_us_cases_df = pd.read_csv(jh_us_cases_path, parse_dates=True)
jh_us_deaths_df = pd.read_csv(jh_us_deaths_path, parse_dates=True)
jh_us_codemap_df = pd.read_pickle("../model_data/jh_codemap_clean.pkl")


# In[3]:


jh_us_cases_df = jh_us_cases_df.loc[~jh_us_cases_df["UID"].isna()]
jh_us_deaths_df = jh_us_deaths_df.loc[~jh_us_deaths_df["UID"].isna()]


# In[4]:


jh_us_cases_df["UID"] = jh_us_cases_df["UID"].astype(int)
jh_us_deaths_df["UID"] = jh_us_deaths_df["UID"].astype(int)


# In[5]:


jh_us_cases_df = jh_us_cases_df.set_index("UID")
jh_us_deaths_df = jh_us_deaths_df.set_index("UID")


# In[6]:


jh_col_drop_list = [
    "iso2",
    "iso3",
    "code3",
    "FIPS",
    "Admin2",
    "Province_State",
    "Country_Region",
    "Lat",
    "Long_",
    "Combined_Key"
]


# In[7]:


jh_codemap_drop_list = [
    'iso2', 'iso3', 'code3','unit_name','subunit_name',
    'lat', 'lon', 'population', "post_code"
]


# In[8]:


jh_us_codemap_df = jh_us_codemap_df.drop(columns=jh_codemap_drop_list)

jh_us_cases_df = jh_us_cases_df.drop(columns=jh_col_drop_list)
jh_us_deaths_df = jh_us_deaths_df.drop(columns=jh_col_drop_list)
jh_us_deaths_df = jh_us_deaths_df.drop(columns=["Population"])


# In[9]:


jh_us_cases_df = jh_us_cases_df.join(jh_us_codemap_df)
jh_us_deaths_df = jh_us_deaths_df.join(jh_us_codemap_df)


# In[10]:


jh_us_cases_df = jh_us_cases_df.reset_index()
jh_us_deaths_df = jh_us_deaths_df.reset_index()


# In[11]:


idx_list = [
    "unit_fips",
    "unit_fips_str",
    "subunit_fips",
    "subunit_fips_str",
    "UID",
]


jh_us_cases_df = jh_us_cases_df.melt(idx_list, var_name='date',value_name='cum_cases')
jh_us_deaths_df = jh_us_deaths_df.melt(idx_list, var_name='date',value_name='cum_deaths')


# In[15]:


jh_us_cases_df["date"] = jh_us_cases_df["date"].astype(np.datetime64)
jh_us_deaths_df["date"] = jh_us_deaths_df["date"].astype(np.datetime64)


# In[16]:


jh_us_cases_df = jh_us_cases_df.astype({"unit_fips": int, "subunit_fips": int})
jh_us_deaths_df = jh_us_deaths_df.astype({"subunit_fips": int, "subunit_fips": int})


# In[17]:


idx_list.insert(0, "date")


# In[19]:


jh_us_cases_df = jh_us_cases_df.set_index(idx_list)
jh_us_deaths_df = jh_us_deaths_df.set_index(idx_list)


# In[20]:


jh_us_cases_df = jh_us_cases_df.sort_index(level=0, sort_remaining=True)
jh_us_deaths_df = jh_us_deaths_df.sort_index(level=0, sort_remaining=True)


# In[21]:


jh_us_data_df = jh_us_cases_df.join(jh_us_deaths_df)


# In[22]:


jh_us_data_df = jh_us_data_df[["cum_cases", "cum_deaths"]]
jh_us_data_df = jh_us_data_df.astype({"cum_cases": int, "cum_deaths": int})

# ## Save the time series

# In[25]:


jh_us_data_df.to_csv("../model_data/jh_us_timeseries.csv", sep='\t')
jh_us_data_df.to_pickle("../model_data/jh_us_timeseries.pkl")
