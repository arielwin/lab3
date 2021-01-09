import rasterio
from rasterio.mask import mask
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import fiona
from shapely.geometry import Polygon, Point
import math
import random
random.seed(0)

def avg_rainfall(layers,ssurgo):
    
    '''
    Function takes a list of layers and an ssurgo layer, gets a number of random test points based on
    the size of the HUC polygons and then gets the average rainfall based on the points from that layer.
    '''
    for layer in layers:
        
        dic = {'id' : [], 'huc' : [], 'geometry' : []}
        lnames = [f for f in layer.columns if 'HUC' in f][0]
        #iterate through each row and get number of points (n) to test
        for idx, row in layer.iterrows():
            extent = row['geometry'].bounds       #get extent using .bounds
            area = (row['geometry'].area/1000000) #get area of actual shape
            n = int(round((0.05*area)))           #get the number of points and round it up to a whole number

            i=0
            while i <= n:
                #get a random point within the bounds
                x = random.uniform(extent[0],extent[2]) #get a random x point within the extent
                y = random.uniform(extent[1], extent[3])#get a random y point within the extent
                p = Point(x,y)                          # combine those into a point
                #test if the point is within the polygon
                if row['geometry'].contains(p):         #if the above point is within the geometry
                    dic['geometry'].append(p)           #add the point to the ditionary
                    dic['id'].append(row[lnames][:8])   #add the huc id do the dictionary
                    dic['huc'].append(lnames)           #add the huc column name to the dictionary
                    i = i +1                            #add one and itterate 
        #define crs
        crs = {'init': 'epsg:4326'}          #set crs
        gdf = gpd.GeoDataFrame(dic, crs=crs) #dictary to gdf with crs
        gdf.groupby(by= 'id').count()        #group by huc id numbers
        
        #read the ssurgo layer
        ssurgo_output = gpd.read_file('lab3.gpkg', layer = ssurgo[0])
        ssurgo_output.crs = crs
        
        #join on huc and print average rainfall
        join = gpd.sjoin(gdf, ssurgo_output, how='left', op='within')
        joint = join.groupby(by = ['huc', 'id']).mean()
        print(joint['aws0150'])
        
listlayers = fiona.listlayers('lab3.gpkg')
ssurgo = []
wdbhuc = []
n = []

for item in listlayers:
    if 'ssurgo' in item:
        ssurgo.append(item)
    if 'huc' in item:
        wdbhuc.append(item)

huc8 = gpd.read_file('lab3.gpkg', layer = wdbhuc[0])
huc12 = gpd.read_file('lab3.gpkg', layer = wdbhuc[1])
#ssurgo = gpd.read_file('lab3.gpkg', layer = ssurgo[0])
layers = [huc8,huc12]

#run the function
avg_rainfall(layers,ssurgo)