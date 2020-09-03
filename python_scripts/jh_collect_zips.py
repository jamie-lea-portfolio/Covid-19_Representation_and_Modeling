#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("Collect zips script starting...")


# In[2]:


import glob
import os
from datetime import datetime
from zipfile import ZipFile


# In[3]:


date = datetime.now()
date_stamp = date.strftime("%d-%m-%y")
print("The date is: {}".format(date_stamp))


# In[4]:


zip_dir = "/home/happy/deep_learning/covid_graph_model/zips"
print("The zip dir is: {}".format(zip_dir))
try:
    os.makedirs(zip_dir, exist_ok=True)
except OSError as e:
    if e.errno != errno.EEXIST:
    	print("Zip dir did not exist but could not be made!")
        raise # not a directroy exist error.  
        # the directory should have diaappeared in previous step, so we should only get BAD errors
        # but if it still exists, we'll just use it and any remaining images will get overwritten

# In[5]:


jh_dirs = "/home/happy/deep_learning/covid_graph_model/images/spread_anim/jh/jh-*"
jh_zips_old = os.path.join(zip_dir, "jh*.zip")


# In[6]:


img_dir_list = [d for d in sorted(glob.glob(jh_dirs)) if os.path.isdir(d)]
old_zip_list = [z for z in sorted(glob.glob(jh_zips_old))]


# In[7]:


print("Found {} zips to remove:\n".format(len(old_zip_list)), "\n".join(old_zip_list))


# In[8]:


for z in old_zip_list:
    if os.path.exists(z):
        os.remove(z)


# In[9]:


print("Found {} image directories to zip:\n".format(len(img_dir_list)), "\n".join(img_dir_list))


# In[10]:


for d in img_dir_list:
    os.chdir(d)
    base_name = os.path.split(d)[-1]
    zip_name = os.path.join(zip_dir, base_name + ".zip")
    
    print("Creating zip: {}".format(zip_name))
    with ZipFile(zip_name, 'w') as zf:
        for f in glob.glob("*/*png"):
            zf.write(f)


# In[11]:


print("Collect zips script ending...")

