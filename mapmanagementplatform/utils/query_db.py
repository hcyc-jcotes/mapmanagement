import numpy as np
import matplotlib.pyplot as plt
from utils.quadtree import Point, Rect, QuadTree
import time
import sqlite3
import requests

from numba import jit, cuda

# SQL connection to db
conA = sqlite3.connect('db.sqlite3')
# cursor
curA = conA.cursor()
# query to get long lat values
get_data = "SELECT id,longitude,latitude FROM frontend_coordinate_property"
curA.execute(get_data)
# loading id ,long, long values into data
data = curA.fetchall()

# process data
coords = np.array(data)

# make a local copy
original_data = np.copy(coords)
# print(original_data)

# drop ID. from coords
coords = coords[:,1:3]
# print(coords)

query2 = "SELECT MAX(longitude) , MAX(latitude) from frontend_coordinate_property"
curA.execute(query2)
max_long_lat = curA.fetchall()
# print ("maxis = ",max_long_lat)

query2 = "SELECT MIN(longitude) , MIN(latitude) from frontend_coordinate_property"
curA.execute(query2)
min_long_lat = curA.fetchall()

# normalize values
normalize_long = 180
normalize_lat  = 90

tot_long= 360
tot_lat = 180

max_long = (max_long_lat[0][0]+normalize_long)*100
max_lat  = (max_long_lat[0][1]+normalize_lat )*100

min_long = (min_long_lat[0][0]+normalize_long)*100
min_lat  = (min_long_lat[0][1]+normalize_lat )*100

# print(max_long_lat[0][0],max_long,max_long_lat[0][1],max_lat)

coords[:,0] = (coords[:,0]+ normalize_long)*10
coords[:,1] = (coords[:,1]+ normalize_lat)* 10

center_long = ((max_long + min_long) /2 ) * 10
center_lat = ((max_lat + min_lat) /2 ) * 10

print("center ",center_lat,center_long)
# sanity check after normalization
## print(old_coords[:,1]+ normalize_lat == coords[:,0],old_coords[:,2]+normalize_long == coords[:,1] )
print(coords)

# points = [Point(*coord) for coord in coords]
# print(len(points))
# print(type(points))

# width, height = 180,360
# domain = Rect(width/2, height/2, width, height)
domain = Rect(3185,550,10,5)
print(type(domain))

def tree_builder(domain,points):
    print("SCRIPT INTEGRATED")
    qtree = QuadTree(domain, 30)
    return qtree

def query_tree(region,found_points):
    qtree.query(region, found_points)
    return found_points

# def tree_builder2(domain,points):
#     qtree = QuadTree(domain, 3)
#     for point in points:
#         # print("inserting ",point)
#         qtree.insert(point)
#     return qtree

# start = time.process_time()
# qtree = tree_builder(domain,points)
# for point in points:
#         qtree.insert(point)
# gen_time = time.process_time() - start
# print("gen time =",gen_time)

# start = time.process_time()
# qtree2 = tree_builder2(domain,points)
# gen_time = time.process_time() - start
# print("gen time without gpu acceleration=",gen_time)


print('Number of points in the domain =', len(qtree))

# fig = plt.figure()
# ax = plt.subplot()
# ax.set_xlim(0, max_lat)
# ax.set_ylim(0, max_long)
# qtree.draw(ax)

# ax.scatter([p.x for p in points], [p.y for p in points], s=4)
# ax.set_xticks([])
# ax.set_yticks([])

# region = Rect(3185.6, 549.7, 0.010, 0.010)
# found_points = []


# start = time.process_time()
# found_points = query_tree(region,found_points)
# query_time = time. process_time() - start

# print("\nquery time =",query_time)
# print('Number of found points =', len(found_points))

# ax.scatter([p.x for p in found_points], [p.y for p in found_points],
#            facecolors='none', edgecolors='r', s=32)

# region.draw(ax, c='r')

# plt.tight_layout()
# plt.show()