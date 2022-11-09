#!/usr/bin/env python
# coding: utf-8

# # Wrangling behavorial data generated by OpenSesame
# 

# ## Introduction
# You build the experiment and ran your first participant. Now, it is time to take a look at the data you have collected.
# 
# OpenSesame outputs a *comma-separated values (csv)* file. This is a very widely used format, and you can painlessly import this file type in Python using the datafile package **pandas**. Let's import a datafile from two participants and merge those in one file:
# 
# 

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# disable chained assignments
pd.options.mode.chained_assignment = None

subj1 = pd.read_csv("data/subject-3.csv", sep=",")
subj2 = pd.read_csv("data/subject-4.csv", sep=",")

df = pd.concat([subj1, subj2], ignore_index=True)


# That's a lot of columns. In your "logger" file in OpenSesame, the recommended thing to do is to check the box of "Log all variables". This is the safest option, because it's easy to remove columns and you would rather not have that you missed an essential variable after doing your experiment. Let's pick the columns that we need:
# 

# In[2]:


include_columns = ['subject_nr', 'block', 'session', 'congruency_transition_type', 'congruency_type',
                   'correct', 'response_time', 'task_transition_type', 'task_type', 'cue_color']

df_trim = df[include_columns]
df_trim


# Before we make any changes to the dataframe, we must first be sure that all the columns are in the right [type](https://pbpython.com/pandas_dtypes.html). If we print the data types of each column, we can see that subject_nr is an integer. However, we don't intend for the dataframe to interpret "3" and "4" as numbers, since it's simply a categorization. Let's change that:

# In[3]:


print(df_trim.dtypes)

df_trim['subject_nr'] = df_trim['subject_nr'].astype('category')
df_trim['correct'] = df_trim['correct'].astype('category')

print(df_trim.dtypes)


# Alright, it's getting a bit more uncluttered now. The task-design is so that the last two blocks are different kind of blocks. We don't have to go in details now, but for further analysis we will have to create a dataframe without block 11 and 12. There are [many ways to conditional selection of rows](https://www.geeksforgeeks.org/selecting-rows-in-pandas-dataframe-based-on-conditions/), but here we opt to use the information that we need all blocks with a value smaller than 11.

# In[4]:


# Here the last blocks should be 12
print(df_trim.tail(5))

# Conditionally select rows based on if the value in the "block" column is lower than 11
df_trim_blocks = df_trim[df_trim['block'] < 11]

# Check to see if the last block is now 10 instead of 12
print(df_trim_blocks.tail(5))


# Lastly, it's a bit confusing that we have only two subjects, but they are called number 3 and 4, instead of 1 and 2. Let's fix that by replacing subject 3 with subject 1, and subject 4 with subject 2. We can use the replace function of Pandas to achieve this. Then, with the pandas *unique* function we can verify that the subject numbers have been changed.

# In[5]:


df_trim_blocks['subject_nr'] = df_trim_blocks['subject_nr'].replace(3, 1)
df_trim_blocks['subject_nr'] = df_trim_blocks['subject_nr'].replace(4, 2)
df_trim_blocks['subject_nr'].unique()


# Let's see what kind of data we are dealing with. The "session" column says lowswitch for subject 1, and highswitch for subject 2. This means that we should see less task-switch trials for subject 1 than subject 2. To check this, we can use the [pivot table](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html) function from pandas. Let's check:

# In[6]:


piv_task_transition_exp = df_trim_blocks.pivot_table(
    index=['session'],
    columns='task_transition_type',
    aggfunc='size') # Function to aggregate columns on, here we specify "size"

piv_task_transition_exp


# It is always good practice to check if the trials count is what you expected. This experiment had a quite complex counterbalancing structure, since the researchers had to counterbalance:
# - Amount of congruent/incongruent trials
# - Amount of parity/magnitude trials
# - Amount of congruent-switch/congruent-repetition trials
# 
# All whilst keeping the task-repetition/task-switch rate to 25/75 or 75/25 (depending on the session).
# This all whilst keeping into account that the first trial of each block does not count as either repetition or switch trial. Let's see if we can use a bit more complex pivot table to get a clear picture if all of this worked out

# In[7]:


piv_cong = df_trim_blocks.pivot_table(
    index=['subject_nr', 'block'],
    columns=['congruency_type'],
    aggfunc='size') # Function to aggregate columns on, here we specify "size"

piv_cong_transition = df_trim_blocks.pivot_table(
    index=['subject_nr', 'block'],
    columns=['congruency_transition_type'],
    aggfunc='size') # Function to aggregate columns on, here we specify "size"

piv_task = df_trim_blocks.pivot_table(
    index=['subject_nr', 'block'],
    columns=['task_type'],
    aggfunc='size') # Function to aggregate columns on, here we specify "size"

piv_task_transition = df_trim_blocks.pivot_table(
    index=['subject_nr', 'block'],
    columns='task_transition_type',
    aggfunc='size') # Function to aggregate columns on, here we specify "size"

# Add all dataframes to a list
dfs = [piv_cong, piv_cong_transition, piv_task, piv_task_transition]

# Merge the dataframes
pd.concat(dfs, axis=1)


# We are repeating quite a lot of code. Whenever you notice that happen, you can probably shorten the code. Let's try it out:

# In[8]:


columns_to_check = ['task_type', 'congruency_type',
                    'task_transition_type', 'congruency_transition_type']

dfs = []
for column in columns_to_check:
    piv = df_trim_blocks.pivot_table(
        index=['subject_nr', 'block'],
        columns=[column],
        aggfunc='size') # Function to aggregate columns on, here we specify "size"

    dfs.append(piv)

# Merge the dataframes
pd.concat(dfs, axis=1)


# Nice. It's cleaner and also way easier to change this code if you want to check another column for example. The counterbalancing looks good on a block level. Let's do some first checks on whether the results are what we expect. Let's first remove all the incorrect trials, we aren't interested in those at the moment.

# In[9]:


df_correct = df_trim_blocks[df_trim_blocks['correct'] == 1]
df_correct


# A really convenient way to quickly get an idea of your numerical columns, you can use the describe function of pandas:

# In[10]:


df_correct['response_time'].describe()


#   We expect people to be slower when they have to switch from task, in comparison to when they can do the same task as on the previous trial. This is what we call **switch cost**. To show this in a table-format, we can again use the pivot_table function from pandas.

# In[11]:


#check switch costs
switch_table = pd.pivot_table(
    df_correct,
    values="response_time", # The value that will be summarized
    index=["subject_nr"], # The rows to summarize over
    columns=["task_transition_type"], # The columns to summarize over
    aggfunc=np.mean, # Calculate the mean response time per subject per task type
)

switch_table


# It is pretty clear that incongruent trials are slower than congruent trials, but we can make it even clearer by showing the difference between the two columns. We can make a new column, and input in that column the difference between the incongruent and congruent columns:

# In[12]:


switch_table['switch cost'] = switch_table['task-switch'] - switch_table['task-repetition']
switch_table


# Lastly, you can use the handy function *describe* to get a quick peek at the response times.

# In[13]:


df_correct['response_time'].describe()


# What we've done here is just a subset of the myriad of possibilities how you can change your dataframe in a way that is tidy and gives you a better overview of what you're dealing with. [This cheat sheet](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf) gives a nice overview of the things we discussed and more! Use the cheat sheet for the following exercises.
# 
# > **Note:** The developers of OpenSesame have also created a Python package for working with column-based and continuous data, called [DataMatrix](http://pydatamatrix.eu/0.15/index/). It's similar to the Pandas package we've been working with in this tutorial, but has some crucial differences in syntax. We have opted for the more versatile and widely used Pandas package, but be aware that the OpenSesame website and tutorials can sometimes refer to DataMatrixes instead of DataFrames.

# ### Exercise 1
# We've removed incorrect trials from our experiment, and looked at the switch cost effect after. However, we should be aware that there is a difference in how many incorrect trials there are per condition. Show the amount of correct/incorrect trials per congruency using a pivot table.

# In[14]:


# Pivot table


# ### Exercise 2
# Next to removing incorrect trials from a dataframe, an often done dataframe manipulation is to remove outliers from your dataframe. These can be trials where participants where unrealistically quick, or just too slow to test the effect you are interested in.
# 
# From the dataframe with correct trials only, remove all trials that have a reaction time below 400ms and above 1000ms. Use a conditional selection of rows, and use only one line of code.

# In[15]:


# df_correct


# ### Exercise 3
# What is a more objective way to do outlier detection? Name two outlier detection methods, one that is suited for normally distributed data, and one that is suited for non-normally distributed data.

# *Answer to exercise 3*

# During the next session we will dive deeper into outlier detection methods.
