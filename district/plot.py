import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn import cluster
from sklearn.preprocessing import scale


gdf = gpd.read_file('results.wkt')
