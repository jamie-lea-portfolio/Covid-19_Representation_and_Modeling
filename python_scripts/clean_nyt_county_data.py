#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
# note: we need fips as str with prepended 0 for mapping to geojson in plotly
df_nyt_counties = pd.read_csv("../nyt_repo/us-counties.csv", 
                              index_col="date", 
                              parse_dates=True
                             )
df_state_fips_codes = pd.read_csv("../other_data/state_fips.tsv", 
                                  index_col=None, sep='\t'
                                 )

df_nyt_counties = df_nyt_counties.rename(columns={"fips": "county_fips_idx"})
df_state_fips_codes = df_state_fips_codes.rename(columns={"fips": "state_fips_idx"})


# In[ ]:


# merge data
df_merged = df_nyt_counties.copy()
df_merged = df_merged.reset_index().merge(df_state_fips_codes, on="state")


# In[ ]:


# remap "unknown" counties and NYC, KC to eliminate nan's
def remap_county_fips(row):
    if row["county"] == "Unknown":
        if row["state_fips_idx"] > 56:
            # map territories (e.g. virgin islands) state and county fips code to their code
            return row["state_fips_idx"]
        else:
            # map us states with unknown locations to the state fips
            return row["state_fips_idx"] * -1000
        
    elif row["county"] == "New York City":
        return -100
    elif row["county"] == "Kansas City":
        return -200
    
    else:
        return row["county_fips_idx"]

df_merged["county_fips_idx"] = df_merged.apply(remap_county_fips, axis=1)
df_merged = df_merged.astype({"county_fips_idx": int, "state_fips_idx": int})


# In[ ]:


# make string version of fips for plotly to map to geo json
df_merged["county_fips_str"] = df_merged["county_fips_idx"].apply(lambda x: str(x))
df_merged["state_fips_str"] = df_merged["state_fips_idx"].apply(lambda x: str(x))


# In[ ]:


df_merged["county_fips_str"] = df_merged["county_fips_str"].apply(
    lambda x: "0" + x if (len(x) < 5 and int(x) > 0) else x
)

df_merged["state_fips_str"] = df_merged["state_fips_str"].apply(
    lambda x: "0" + x if (len(x) < 2) else x
)

# set index
df_merged = df_merged.set_index(["date", "state_fips_idx", "county_fips_idx"], drop=True)


# In[ ]:


# calculate new cases and deaths
df_merged[["new_cases", "new_deaths"]] = df_merged.groupby(level=2)[["cases", "deaths"]].diff()

def remap_first_cases(row):
    case_val = row["new_cases"] 
    if pd.isnull(case_val):
        return row["cases"]
    else:
        return case_val
    
def remap_first_deaths(row):
    case_val = row["new_deaths"] 
    if pd.isnull(case_val):
        return row["deaths"]
    else:
        return case_val
    
df_merged["new_cases"] = df_merged.apply(remap_first_cases, axis=1)
df_merged["new_deaths"] = df_merged.apply(remap_first_deaths, axis=1)

df_merged = df_merged.astype({"cases": int, "new_cases": int, "deaths": int, "new_deaths": int})

# reorder columns
df_merged = df_merged[["post_code", "state", "county",
                       "county_fips_str", "state_fips_str",
                       "cases", "new_cases", 
                       "deaths", "new_deaths"]]

# sort index by date
df_merged = df_merged.sort_index(level=["date"], sort_remaining=True)

df_merged.to_csv("../model_data/nyt_county_data_cleaned.tsv", sep="\t", na_rep="NA")
df_merged.to_pickle("../model_data/nyt_county_data_cleaned.pkl")
# ## Create a dataframe for each unique county with "empty" data

# In[ ]:


df_fips_unique = df_merged.copy().reset_index()


# In[ ]:


fake_date = pd.Timestamp("2000-01-01 00:00:00")


# In[ ]:


df_fips_unique["cases"] = 0
df_fips_unique["deaths"] = 0
df_fips_unique["new_cases"] = 0
df_fips_unique["new_deaths"] = 0
df_fips_unique["date"] = fake_date
df_fips_unique = df_fips_unique.drop_duplicates().copy()


# ### Bring in counties from adj list not in nyt data

# In[ ]:


adj_code_map = pd.read_pickle("../model_data/county_adj_codes_map.pkl")
adj_code_map = adj_code_map.rename(columns={"county_fips": "county_fips_str"})
adj_code_map = adj_code_map.merge(df_state_fips_codes, on="post_code")


# In[ ]:


adj_code_map["county_fips_idx"] = adj_code_map["county_fips_str"].apply(lambda x: int(x))
adj_code_map["state_fips_str"] = adj_code_map["state_fips_idx"].apply(lambda x: str(x))
adj_code_map["state_fips_str"] = adj_code_map["state_fips_str"].apply(
    lambda x: "0" + x if (len(x) < 2) else x
)


# In[ ]:


adj_code_map["cases"] = 0
adj_code_map["deaths"] = 0
adj_code_map["new_cases"] = 0
adj_code_map["new_deaths"] = 0
adj_code_map["date"] = fake_date
adj_code_map = adj_code_map.drop_duplicates().copy()


# In[ ]:


nyt_fips_list = df_fips_unique.county_fips_idx.to_list()
new_counties = adj_code_map[~adj_code_map["county_fips_idx"].isin(nyt_fips_list)].reset_index(drop=True)


# ### Concatenate

# In[ ]:


df_fips_unique = pd.concat([df_fips_unique, new_counties])


# In[ ]:


df_fips_unique = df_fips_unique.set_index(["date", "state_fips_idx", "county_fips_idx"])
df_fips_unique = df_fips_unique.sort_index(level=0)


# In[ ]:


df_fips_unique.head()


# In[ ]:


assert (df_fips_unique.isna().all() == False).all() == True, "ERROR: nan in unique empty, did data format change?"


# In[ ]:


assert df_fips_unique.duplicated().sum() == 0, "ERROR: some rows in final unique empty are duplicated, what happened?"


# In[ ]:


df_fips_unique.to_csv("../model_data/nyt_empty_counties_frame_slice.tsv", sep='\t', na_rep="NA")
df_fips_unique.to_pickle("../model_data/nyt_empty_counties_frame_slice.pkl")


# ## Create a dataframe for mapping identifiers

# In[ ]:


df_fips_list_frame = df_fips_unique.copy().reset_index(drop=True)


# In[ ]:


df_fips_list_frame = df_fips_list_frame.drop(columns=["cases", "new_cases", "deaths", "new_deaths"])


# In[ ]:


df_fips_list_frame.to_csv("../model_data/nyt_counties_list_slice.tsv", sep='\t', na_rep="NA", index=False)
df_fips_list_frame.to_pickle("../model_data/nyt_counties_list_slice.pkl")


# ## Create a dataframe for a simple list of fips, as str (to include pre-fixed 0)

# In[ ]:


df_fips_list = df_fips_list_frame["county_fips_str"]


# In[ ]:


df_fips_list.to_csv("../model_data/model_counties_list.lst", sep='\t', index=False)

