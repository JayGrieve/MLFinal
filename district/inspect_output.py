#!/usr/bin/env python3
import numpy as np
import sys
import scipy.spatial as sp
import shapely.geometry as sg
from shapely.geometry.polygon import Polygon
import shapely.ops 
import shapely.wkt
from shapely.geometry import mapping, Point, LineString
import fiona
import geopandas as gpd
import pandas as pd

f = open('final.wkt', "r")
lines = f.readlines()




def wkt_to_shp(wkt_list, shp_file):
    '''Take output of build_graph_wkt() and render the list of linestrings
    into a shapefile
    # https://gis.stackexchange.com/questions/52705/how-to-write-shapely-geometries-to-shapefiles
    '''

    # Define a linestring feature geometry with one attribute
    schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'int'},
    }

    # Write a new shapefile
    with fiona.open(shp_file, 'w', 'ESRI Shapefile', schema) as c:
        for i, line in enumerate(wkt_list):
            shape = shapely.wkt.loads(line)
            c.write({
                    'geometry': mapping(shape),
                    'properties': {'id': i},
                    })

    return


wkt_to_shp(lines,'final')

regions = gpd.read_file('/Users/jay/Desktop/Sem6/Machine_Learning/Project/district/final/final.shp')
regions.plot()
tracts = gpd.read_file('/Users/jay/Desktop/Sem6/Machine_Learning/Project/district/tract_shape/cb_2019_us_tract_500k.shp')
tlist = tracts.to_dict('records')
rlist = regions.to_dict('records')

#Map each tract to its region
for tract in tlist:
    for geom in rlist:
        if geom['geometry'].contains(tract['geometry']):
            tract['region'] = geom['id']



tracts2 = gpd.GeoDataFrame(tlist)

pop_by_tract = pd.read_csv('pop_tract_df.csv')

tracts2['GEOID'] = tracts2['AFFGEOID']

merged = tracts2.merge(pop_by_tract,how = 'left',on = 'GEOID')


#Error Checking
import json
dropped = json.load(open('dropped_tracts.json','r'))

invalid = merged.loc[merged['region'].isna()]
invalid = invalid.loc[~merged['ALUBE001'].isna()] #set of tracts w/ valid population 
invalid = invalid.loc[merged['ALUBE001']>0] #set of tracts w/ population 

not_assigned = list(invalid['GEOID'])
incorrectly_not_assigned = [n for n in not_assigned if n not in dropped] #not dropped but missing pops
invalid = invalid.loc[invalid['GEOID'].isin(incorrectly_not_assigned)]

invalid_gdf = gpd.GeoDataFrame(invalid)
invalid_gdf.plot()         
invalid_gdf['center_x'] = invalid_gdf['geometry'].centroid.x
invalid_gdf['center_y'] = invalid_gdf['geometry'].centroid.y


def filter_fn(row):
    top = 49.3457868 # north lat
    left = -124.7844079 # west long
    right = -66.9513812 # east long
    bottom =  24.7433195 # south lat
    lng = row['center_x']
    lat = row['center_y']

    if bottom <= lat <= top and left <= lng <= right:
        return True
    return False

                
in_continental = invalid_gdf.apply(filter_fn, axis=1)                
invalid_gdf = invalid_gdf[in_continental]
igdf = invalid_gdf.to_dict('records')
multiregion_mapping = {}
for i in igdf:
    temp_mapping = {}
    for geom in rlist:
        inter = geom['geometry'].intersection(i['geometry']).area
        if inter > 0:
            temp_mapping[geom['id']] = inter / i['geometry'].area
    multiregion_mapping[i['GEOID']] = temp_mapping

#now we have a mapping for the partials... lets compute summary values
temp_merged = merged
votes_by_tract = pd.read_csv('votes_by_tract.csv')
votes_by_tract['voting_pop'] = votes_by_tract['votes_dem'] + votes_by_tract['votes_gop']
votes_by_tract['GEOID'] = votes_by_tract['GEOID'].str.replace('US','00US')
merged_vote = merged.merge(votes_by_tract,how = 'left',on = 'GEOID')
#now we have the voting stuff for each tract, next for each region first get voting from df
#then, use votes_by_tract and the multiregion mapping stuff to finish it

#first, tracts fitting perfectly into regions
for r in rlist:
    temp = merged_vote.loc[merged_vote['region'] == r['id']]
    if len(temp) > 0:
        r['voting_pop'] = float(temp['voting_pop'].sum())
        r['votes_gop'] = float(temp['votes_gop'].sum())
        r['votes_dem'] = float(temp['votes_dem'].sum())
        r['pct_dem'] = r['votes_dem'] / r['voting_pop']
        r['pct_gop'] = r['votes_gop'] / r['voting_pop']
        r['population'] = float(temp['ALUBE001'].sum())

#next, tracts that dont
r_wrapped = {}
for r in rlist:
    r_wrapped[r['id']] = r
vote_dict = merged_vote.set_index('GEOID').to_dict(orient = 'index')
for m in multiregion_mapping:
    vote = vote_dict[m] #vote info for this tract
    for v in multiregion_mapping[m]: #iterate through regions its in
        r_wrapped[v]['voting_pop'] += float(vote['voting_pop'] * multiregion_mapping[m][v])
        r_wrapped[v]['votes_gop'] += float(vote['votes_gop'] *  multiregion_mapping[m][v])
        r_wrapped[v]['votes_dem'] += float(vote['votes_dem'] *  multiregion_mapping[m][v])
        r_wrapped[v]['pct_dem'] = r_wrapped[v]['votes_dem'] / r_wrapped[v]['voting_pop']
        r_wrapped[v]['pct_gop'] = r_wrapped[v]['votes_gop'] / r_wrapped[v]['voting_pop']
        r_wrapped[v]['population'] += float(vote['ALUBE001'] *  multiregion_mapping[m][v])

    

final = pd.DataFrame(rlist)
final.to_csv('region_data_final.csv',index = None)

                