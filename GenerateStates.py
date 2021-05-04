import pandas as pd
from shapely.geometry import Point
#import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import libpysal 
import pysal as ps
from libpysal.weights import Queen, Rook, KNN

import geopandas as gpd
from sklearn import cluster
from sklearn.cluster import KMeans, AgglomerativeClustering

from sklearn.preprocessing import scale
from sklearn_extra.cluster import KMedoids

import json
import statistics
import numpy as np
import random
NUM_COLORS = 48
cm = plt.get_cmap('gist_rainbow')
colors = [cm(random.random()*i/NUM_COLORS) for i in range(NUM_COLORS)]
color_map = []
for i in range(48):
    color_map.append({'num':i,'color':colors[i]})
    
color_join = pd.DataFrame(color_map)

ww = pd.read_csv('region_data_final.csv')
plt.boxplot(r = max(ww['population']) - min(ww['population']))

temp = pd.read_csv('region_data_final.csv').drop(labels ='geometry',axis = 1)
temp['voting_pop'] = temp['votes_gop'] + temp['votes_dem']
temp['pct_dem'] = temp['votes_dem']/temp['voting_pop']
temp['pct_gop'] = temp['votes_gop']/temp['voting_pop']

temp2 = gpd.read_file('/Users/jay/Desktop/Sem6/Machine_Learning/Project/district/final/final.shp')
temp2 = gpd.GeoDataFrame(temp2.merge(temp, how = 'left', on = 'id'))


km5 = KMedoids(n_clusters=48,metric = 'chebyshev')
f, ax = plt.subplots(1, figsize=(9, 9))

km5cls = km5.fit(temp2.drop(['geometry', 'pct_dem','pct_gop'], axis=1).values)
regions = temp2.assign(cl=km5cls.labels_)
c_spec = color_join.rename(columns = {'num':'cl'})

regions_c2 = regions.merge(c_spec,how = 'left', on = 'cl')

regions_c2.plot(column='cl', color = regions_c2['color'],categorical=True, legend=False, linewidth=0.1, edgecolor='white', ax=ax)

dissims = abs(regions.groupby('cl')['votes_gop'].sum() / regions.groupby('cl')['voting_pop'].sum() -
regions.groupby('cl')['votes_dem'].sum() / regions.groupby('cl')['voting_pop'].sum())
dissim_temp = dissims.to_frame().reset_index()

Q_w = Queen.from_dataframe(temp2)

model = AgglomerativeClustering(linkage='ward',connectivity=Q_w.sparse,n_clusters=48)
model.fit(temp2.drop(['population','geometry'], axis=1).values)
temp2 = temp2.assign(cl2=model.labels_)

c_spec = color_join.rename(columns = {'num':'cl2'})
temp2_c2 = temp2.merge(c_spec,how = 'left', on = 'cl2')

f2, ax2 = plt.subplots(1, figsize=(9, 9))
temp2_c2.plot(column='cl2',color = temp2_c2['color'],categorical = True, legend=True, linewidth=0.1, edgecolor='white', ax=ax2)

for_comp = pd.read_csv('votes_by_tract.csv')
for_comp['voting_pop'] = for_comp['votes_dem'] + for_comp['votes_gop']
for_comp = for_comp.loc[~for_comp['votes_dem'].isna()]
dissims0 = abs(for_comp.groupby('county_fips')['votes_gop'].sum() / for_comp.groupby('county_fips')['voting_pop'].sum() -
for_comp.groupby('county_fips')['votes_dem'].sum() / for_comp.groupby('county_fips')['voting_pop'].sum())
dissim_temp0 = dissims0.to_frame().reset_index().rename(columns = {0:'diff'})

dissims1 = abs(regions.groupby('cl')['votes_gop'].sum() / regions.groupby('cl')['voting_pop'].sum() -
regions.groupby('cl')['votes_dem'].sum() / regions.groupby('cl')['voting_pop'].sum())
dissim_temp = dissims.to_frame().reset_index().rename(columns = {0:'diff'})

dissims2 = abs(temp2.groupby('cl2')['votes_gop'].sum() / temp2.groupby('cl2')['voting_pop'].sum() -
temp2.groupby('cl2')['votes_dem'].sum() / temp2.groupby('cl2')['voting_pop'].sum())
dissim_temp2 = dissims2.to_frame().reset_index().rename(columns = {0:'diff'})

plot_dic = {'U.S. Counties':dissims0,'Noncontiguous':dissim_temp['diff'],'Contiguous':dissim_temp2['diff']}

fig3, ax3 = plt.subplots()
ax3.boxplot(plot_dic.values())
ax3.set_xticklabels(plot_dic.keys())