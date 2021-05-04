import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame

survey = pd.read_csv("CCES20_Common_OUTPUT.csv")
latlong = pd.read_csv('zip_lat_lon.csv')
f = survey.columns


z = survey[[
            "inputstate",
            "votereg",
            "votereg_f",
            'countyname',
            'countyfips',
            "regzip",
            "region",
            'lookupzip',
            'votereg',
            'CC20_433a',
            'CC20_433b'
            ]]

states = gpd.read_file('/Users/jay/Desktop/Sem6/Machine Learning/Project/cb_2018_us_state_500k/cb_2018_us_state_500k.shp')
states = states[~states.NAME.str.contains("Alaska")]
states = states[~states.NAME.str.contains("Hawaii")]
states = states[~states.NAME.str.contains("Guam")]
states = states[~states.NAME.str.contains("Rico")]
states = states[~states.NAME.str.contains("Virgin Is")]
states = states[~states.NAME.str.contains("Samoa")]
states = states[~states.NAME.str.contains("Commonweal")]

states.boundary.plot()


z[['lookupzip']].nunique()
z = z.rename(columns = {'lookupzip':'zip'})
r = z.groupby('zip').size().mean()

s1 = set(list(latlong['zip']))
s2 = set(list(z['zip']))
s3 = s1.difference(s2)
3586 in s2


merged = z.merge(latlong,how = 'left',on = 'zip')
merged = merged.loc[merged['lon']>-130]

geometry = [Point(xy) for xy in zip(merged['lon'], merged['lat'])]
gdf = GeoDataFrame(merged, geometry=geometry)   



gdf.plot(ax=states.plot(figsize=(10, 6)),column='votereg', marker='o', color='red', markersize=15)
