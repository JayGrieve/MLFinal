#!/usr/bin/env python3
import shapefile
from shapely.geometry import shape
from shapely.geometry import Polygon

'''
Call with first argument being the two-letter state abbreviation
and second argument being a filename of a shape record file,
 e.g. "/Users/klein/Downloads/cb_2016_us_state_500k/cb_2016_us_state_500k"
'''
# http://en.wikipedia.org/wiki/Extreme_points_of_the_United_States#Westernmost
top = 49.3457868 # north lat
left = -124.7844079 # west long
right = -66.9513812 # east long
bottom =  24.7433195 # south lat


def cull(latlngs):
    """ Accepts a list of lat/lng tuples. 
        returns the list of tuples that are within the bounding box for the US.
        NB. THESE ARE NOT NECESSARILY WITHIN THE US BORDERS!
    """
    inside_box = []
    for (lat, lng) in latlngs:
        if bottom <= lat <= top and left <= lng <= right:
            inside_box.append((lat, lng))
    return inside_box


sf = shapefile.Reader('/Users/jay/Desktop/Sem6/Machine_Learning/Project/cb_2018_us_nation_5m/cb_2018_us_nation_5m.shp')
for state in sf.iterShapeRecords():
    pass
j = []
x = []
y = []
for i in range(1,len(state.shape.points)):
    if i in state.shape.parts:
        print()
    pt = state.shape.points[i]
    #print(pt[0], pt[1])
    x.append((pt[1],pt[0]))
trimmed = cull(x)
for t in trimmed:
    print(t[1],t[0])




