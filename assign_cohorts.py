import time
import csv
import re

import pandas as pd
import numpy as np

# Import and cleaning
## subset columns to get email, first and last name, and cohort preferences
df = pd.read_csv('./data/form_sheet.csv')
df = df[[col for col in df.columns if (("Preferences" in col) | ("Email" in col) | ("Name" in col) | ("Year" in col))]]
df.columns = list(df.columns[0:4]) + [re.split('\[|\]',name)[1] for name in df.columns[4:]]

## converting rankings into numbers
cohort_names = list(df.columns[4:])
for col in cohort_names:
    df[col] = pd.to_numeric(df[col].str.extract('(\d)', expand=False).str.strip())
df.fillna(0,inplace=True)


# Assigning applicants to cohorts
## assignments
cohorts = {name:[] for name in cohort_names}
temp = df.copy()
for rank in range(1,len(cohort_names)+1):
    for name in cohort_names:
        for row in range(0,temp.shape[0]):
            if ((pd.notna(temp.loc[row,'Email Address'])) and (len(cohorts[name]) < 20) and (temp[name][row] == rank)):
                cohorts[name].append(temp['Email Address'][row])
                temp.loc[row,'Email Address'] = np.nan

# checking if people did not get assigned and outputting them to separate csv
assigned = sum(cohorts.values(), [])
leftovers = list(set(assigned).symmetric_difference(set(df['Email Address'].tolist())))

if len(leftovers) != 0:
    df[df['Email Address'].isin(leftovers)].to_csv(path_or_buf='./assignments/leftovers.csv',index=False)

# output assignments as csv
## all cohort assignments and emails
cohort_assignments = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in cohorts.items()]))
cohort_assignments.fillna('',inplace=True)
cohort_assignments.to_csv(path_or_buf='./assignments/all_emails.csv',index=False)

## each individual cohort spreadsheet with first name, last name, email, year
for cohort, emails in cohorts.items():
    temp = df[df['Email Address'].isin(emails)]
    indiv_assign = temp[[col for col in temp.columns if (("Email" in col) or ("Name" in col) or ("Year" in col))]]
    
    path = './assignments/' + '_'.join(cohort.lower().split(' ')) + '.csv'
    indiv_assign.to_csv(path_or_buf=path,index=False)