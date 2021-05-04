import pandas as pd
from shapely.geometry import Point
#import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
#import pysal as ps
import geopandas as gpd
from sklearn import cluster
from sklearn.preprocessing import scale
import json

x = pd.read_csv('pop_by_tract.csv',encoding = "ISO-8859-1")[['GEOID','ALUBE001']].set_index('GEOID').to_dict()['ALUBE001']
json.dump(x,open('tract_pop_map.json','w'))

votes_by_county = pd.read_csv('2020_US_County_Level_Presidential_Results.csv')
age_sex_pop_tract = pd.read_csv('age_sex_pop_tract.csv',encoding = "ISO-8859-1")[['GEOID','COUNTYA','STATEA','ALT0E001','ALT0E003','ALT0E004','ALT0E005','ALT0E006','ALT0E027','ALT0E028','ALT0E029','ALT0E030']]
age_sex_pop_tract['voting_pop'] = age_sex_pop_tract['ALT0E001']
to_subtract = ['ALT0E003','ALT0E004','ALT0E005','ALT0E006','ALT0E027','ALT0E028','ALT0E029','ALT0E030']
for key in to_subtract:
    age_sex_pop_tract['voting_pop'] -= age_sex_pop_tract[key]
    
to_fix = age_sex_pop_tract.to_dict('records')
for f in to_fix:
    def pad(x,county):
        x = str(x)
        if county:
            while len(x) != 3:
                x = '0' + x
        if not county:
            while len(x) != 2:
                x = '0' + x
        
        return x
            
            
    county_code = f['COUNTYA']
    state_code = f['STATEA']
    f['county_fips'] = int(pad(state_code,0) + pad(county_code,1))

votingpop_by_tract = pd.DataFrame(to_fix)[['GEOID','county_fips','voting_pop','STATEA']]
f = lambda x:  x / float(x.sum())
votingpop_by_tract['perc_total'] = (votingpop_by_tract.groupby(['county_fips'])['voting_pop'].transform(f))

to_merge = votes_by_county[['county_fips','votes_gop','votes_dem']]
merged = votingpop_by_tract.merge(to_merge,how = 'left',on = 'county_fips')

merged['votes_gop'] *= merged['perc_total']
merged['votes_dem'] *= merged['perc_total']

merged.to_csv('votes_by_tract.csv')



