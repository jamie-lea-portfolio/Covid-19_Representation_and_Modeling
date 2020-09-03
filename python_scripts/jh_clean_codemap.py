#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os


# In[ ]:


debug = False


# In[2]:


jh_timeseries_root = "../johns_hopkins_data/csse_covid_19_data/csse_covid_19_time_series"


# In[3]:


jh_cases_path = os.path.join(jh_timeseries_root, "time_series_covid19_confirmed_US.csv")
jh_deaths_path = os.path.join(jh_timeseries_root, "time_series_covid19_deaths_US.csv")

jh_cases_df = pd.read_csv(jh_cases_path)
jh_deaths_df = pd.read_csv(jh_deaths_path)
state_fips = pd.read_csv("../other_data/state_codes.tsv", sep='\t', index_col=["state"])


# In[4]:


jh_drop_col = jh_cases_df.columns[10:]


# In[5]:


jh_cases_df = jh_cases_df.drop(columns=jh_drop_col)
jh_deaths_df = jh_deaths_df.drop(columns=jh_drop_col)


# In[6]:


jh_cases_df[jh_cases_df["Province_State"] == "Diamond Princess"]


# In[7]:


jh_deaths_df[jh_deaths_df["FIPS"].duplicated()]


# In[8]:


jh_deaths_df.tail()


# In[9]:


jh_deaths_df


# In[11]:


jh_codemap_joined = jh_cases_df.join(jh_deaths_df.iloc[:,-1], how="outer")


# In[12]:


jh_codemap_joined = jh_codemap_joined.drop(columns=["Country_Region"])


# In[13]:


jh_codemap_joined = jh_codemap_joined.loc[~jh_codemap_joined["UID"].isna()]


# In[14]:


jh_codemap_joined["UID"] = jh_codemap_joined["UID"].astype(int)


# In[15]:


jh_codemap_joined = jh_codemap_joined.merge(state_fips, how="outer", left_on="Province_State", right_on="state")


# In[16]:


jh_codemap_joined = jh_codemap_joined.rename(
    {
        "FIPS": "subunit_fips", "fips": "unit_fips", 
        "Province_State": "unit_name", "Admin2": "subunit_name",
        "Population": "population"
    }, axis=1)


# In[17]:


jh_codemap_joined


# In[18]:


jh_codemap_joined = jh_codemap_joined.rename({"Long_": "lon", "Lat": "lat"}, axis=1)


# In[19]:


print(jh_codemap_joined.shape)
jh_codemap_joined.head()


# In[20]:


jh_codemap_joined["unit_fips"] = jh_codemap_joined.apply(
    lambda x: x["UID"] if (np.isnan(x["unit_fips"])) else x["unit_fips"]
                          ,axis=1)


# In[21]:


jh_codemap_joined["subunit_fips"] = jh_codemap_joined.apply(
    lambda x: x["UID"] if (np.isnan(x["subunit_fips"])) else x["subunit_fips"]
                          ,axis=1)


# In[22]:


jh_codemap_joined[jh_codemap_joined["unit_name"].isna()]


# In[23]:


jh_codemap_joined[jh_codemap_joined["subunit_name"].isna()]


# In[24]:


no_subunit_names = jh_codemap_joined[jh_codemap_joined["subunit_name"].isna()]["unit_name"].to_list()


# In[25]:


no_subunit_names


# In[26]:


jh_codemap_joined = jh_codemap_joined.set_index("unit_name")


# In[27]:


jh_codemap_joined


# In[28]:


for name in no_subunit_names:
    jh_codemap_joined.loc[name, "subunit_name"] = name


# In[29]:


jh_codemap_joined[jh_codemap_joined["unit_fips"].isna()]


# In[30]:


jh_codemap_joined[jh_codemap_joined["subunit_fips"].isna()]


# In[31]:


jh_codemap_joined["subunit_fips"] = jh_codemap_joined["subunit_fips"].astype(int)
jh_codemap_joined["unit_fips"] = jh_codemap_joined["unit_fips"].astype(int)


# In[32]:


jh_codemap_joined["subunit_fips_str"] = jh_codemap_joined["subunit_fips"].astype(str)
jh_codemap_joined["unit_fips_str"] = jh_codemap_joined["unit_fips"].astype(str)


# In[33]:


jh_codemap_joined["subunit_fips_str"] = jh_codemap_joined["subunit_fips_str"].apply(
    lambda x: "0" + x if (len(x) == 4 and int(x) > 0) else x
)

jh_codemap_joined["subunit_fips_str"] = jh_codemap_joined["subunit_fips_str"].apply(
    lambda x: "0" + x if (len(x) == 1) else x
)


# In[34]:


jh_codemap_joined.loc["District of Columbia", "post_code"] = "DC"


# In[35]:


jh_codemap_joined.loc["Diamond Princess", "post_code"] = "DP"
jh_codemap_joined.loc["Grand Princess", "post_code"] = "GP"


# In[36]:


jh_codemap_joined.head()


# In[37]:


jh_codemap_joined.loc[jh_codemap_joined["code3"].isna()]


# In[38]:


jh_codemap_joined = jh_codemap_joined.reset_index()


# In[39]:


jh_codemap_joined.head()


# In[40]:


type_dict = {
    "unit_name": str,
    "UID": int,
    "iso2": str,
    "iso3": str,
    "code3": int,
    "subunit_fips": int,
    "subunit_name": str,
    "lat": np.float64,
    "lon": np.float64,
    "post_code": str,
    "unit_fips": int,
    "subunit_fips_str": str,
    "unit_fips_str": str,
    "population": int,
}


# In[41]:


jh_codemap_joined = jh_codemap_joined.astype(type_dict)


# In[42]:


if debug:
    jh_codemap_joined.info()


# In[43]:


jh_codemap_joined.head(10)


# In[44]:


jh_codemap_joined.tail(10)


# In[45]:


jh_codemap_joined[jh_codemap_joined.isnull().any(axis=1)]


# In[46]:


jh_codemap_joined = jh_codemap_joined.set_index("UID")


# In[47]:


jh_codemap_joined = jh_codemap_joined[["iso2", "iso3", "code3", 
                                       "unit_fips", "unit_fips_str", "post_code", "unit_name",
                                       "subunit_fips", "subunit_fips_str", "subunit_name",
                                      "lat", "lon", "population"]
                                     ]


# In[48]:


jh_codemap_joined


# In[50]:


jh_codemap_joined.to_csv("../model_data/jh_codemap_clean.tsv", sep='\t')
jh_codemap_joined.to_pickle("../model_data/jh_codemap_clean.pkl")

