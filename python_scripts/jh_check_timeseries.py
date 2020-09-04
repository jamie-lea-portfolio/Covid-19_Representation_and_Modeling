#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


jh_timeseries_df = pd.read_pickle("../model_data/jh_us_timeseries.pkl")

jh_empty_slice_df = pd.read_pickle("../model_data/jh_us_timeseries-empty_slice.pkl")


# In[3]:


jh_ts_single_index = jh_timeseries_df.loc[jh_timeseries_df.index.get_level_values(level=0)[-1]].index

jh_empty_single_index = jh_empty_slice_df.loc[jh_empty_slice_df.index.get_level_values(level=0)[-1]].index


# In[4]:


# if the existing empty slice isn't correct for the current timeslice, create a new one
if not (len(jh_empty_single_index) == len(jh_ts_single_index) and (jh_empty_single_index == jh_ts_single_index).all()):
    import numpy as np
    day_zero = jh_timeseries_df.loc[jh_timeseries_df.index.get_level_values(0)[0]].copy()
    day_zero_dt = np.datetime64("2020-01-21")
    day_zero["cum_cases"] = 0
    day_zero["new_cases"] = 0
    day_zero["cum_deaths"] = 0
    day_zero["new_deaths"] = 0
    day_zero = pd.concat([day_zero], keys=[day_zero_dt], names=['date'])
    day_zero.to_csv("../model_data/jh_us_timeseries-empty_slice.csv", sep='\t')
    day_zero.to_pickle("../model_data/jh_us_timeseries-empty_slice.pkl")

