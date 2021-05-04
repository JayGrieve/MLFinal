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
import statistics
import numpy as np

votes_by_county = pd.read_csv('2020_US_County_Level_Presidential_Results.csv')

metrics = pd.read_csv('/Users/jay/Desktop/Sem6/Machine_Learning/Project/nhgis0003_csv/nhgis0003_ds244_20195_2019_tract.csv',encoding = "ISO-8859-1")

race = metrics[['STATEA','COUNTYA','ALUCE002','ALUCE003','ALUCE005','ALUCE004']]

t1 = np.array([1,2])
t2 = np.array([1,2])

dist = np.linalg.norm(t1 - t2)

