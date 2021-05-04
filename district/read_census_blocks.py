import shapefile
from shapely.geometry import shape
import json
'''Provides a procedure to read a shape file specifying census blocks,
   and write a file giving the clients.  For each census block, the client
   is located at the centroid of the block shape, and its weight is the
   population of the census block.
   Each line of the output consists of:
      the x coordinate,
      the y coordinate, and
      the population.
   Only census blocks with positive population are represented in the output.
'''

# http://en.wikipedia.org/wiki/Extreme_points_of_the_United_States#Westernmost
top = 49.3457868 # north lat
left = -124.7844079 # west long
right = -66.9513812 # east long
bottom =  24.7433195 # south lat


def valid(lat,lng):
    """ Accepts a list of lat/lng tuples. 
        returns the list of tuples that are within the bounding box for the US.
        NB. THESE ARE NOT NECESSARILY WITHIN THE US BORDERS!
    """
    if bottom <= lat <= top and left <= lng <= right:
        return True
    return False

def write_client_file(input_filename, output_filename):
    bad_fips = [2,15,60,69,72,78]
    dropped = []
    pop_mapping = json.load(open('tract_pop_map.json','r'))
    of = open(output_filename, 'w')
    sf = shapefile.Reader('/Users/jay/Desktop/Sem6/Machine_Learning/Project/tract_shape/cb_2019_us_tract_500k.shp')
    for shape_rec in sf.iterShapeRecords():
        if int(shape_rec.record[0]) not in bad_fips: #only continental US
            try:
                pop = pop_mapping[shape_rec.record[3]]
            except:
                dropped.append(shape_rec.record[3])
                continue
            if pop>0:
                cent = shape(shape_rec.shape).centroid
                if(valid(cent.y,cent.x)):
                    of.write(str(cent.x)+" "+str(cent.y)+" "+str(pop)+"\n")
                else:
                    dropped.append(shape_rec.record[3])
    json.dump(dropped,open('dropped_tracts.json','w'))

import sys
write_client_file(sys.argv[1],sys.argv[2])

