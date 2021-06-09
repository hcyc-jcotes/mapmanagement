import numpy as np
import matplotlib.pyplot as plt
from quadtree import Point, Rect, QuadTree
import time
import sqlite3
import requests
import math
from scipy.spatial import distance


def normalizer(lon,lat):
    lon = lon - 180
    lat  = lat - 90
    factor= 10.0 ** 7
    lon  = math.trunc (lon * factor) / factor
    lat  = math.trunc (lat * factor) / factor
    return lon,lat

def tree_builder(domain,points):
    qtree = QuadTree(domain, 30)
    for point in points:
        qtree.insert(point)
    return qtree

def query_tree(region,found_points):
    qtree.query(region, found_points)
    return found_points

def db_connection():
    # SQL connection to db
    conA = sqlite3.connect('db.sqlite3')
    # cursor
    curA = conA.cursor()
    return curA
curA=db_connection()

def get_data(curA):
    start_data_load = time.process_time()
    # query to get long lat values
    get_data = "SELECT id,longitude,latitude,direction FROM backend_coordinate_property"
    curA.execute(get_data)
    # loading id ,long, long values into data
    data = curA.fetchall()
    coords = np.array(data)
    print("number of entries in db : ",len(coords))
    # make a local copy
    original_data = np.copy(coords)
    # drop ID. from coords
    p_coords = coords[:,0:3]
    coords = coords[:,1:3]

    data_load_time = time.process_time() - start_data_load
    print("Data Loading time =",data_load_time)

    return p_coords,coords,original_data

p_coords,coords,original_data = get_data(curA)

def set_domain():
    start_domain_load = time.process_time()

    query2 = "SELECT MAX(longitude) , MAX(latitude) from backend_coordinate_property"
    curA.execute(query2)
    max_long_lat = curA.fetchall()
    # print ("maxis = ",max_long_lat)
    query3 = "SELECT MIN(longitude) , MIN(latitude) from backend_coordinate_property"
    curA.execute(query3)
    min_long_lat = curA.fetchall()
    # normalize values
    normalize_long = 180.0
    normalize_lat  = 90.0
    tot_long= 360.0
    tot_lat = 180.0
    max_long = (max_long_lat[0][0]+normalize_long)
    max_lat  = (max_long_lat[0][1]+normalize_lat )
    min_long = (min_long_lat[0][0]+normalize_long)
    min_lat  = (min_long_lat[0][1]+normalize_lat )
    # print("min_max_long", min_long, max_long,"min_max_lat",min_lat,max_lat)
    coords[:,0] = (coords[:,0] + normalize_long)
    coords[:,1] = (coords[:,1] + normalize_lat )
    # print ("coords", coords)
    center_long = ((max_long + min_long) /2 )
    center_lat = ((max_lat + min_lat) /2 )
    # width, height = 180,360
    # domain = Rect(width/2, height/2, width, height)
    domain = Rect(center_long,center_lat,1,1)
    domain_load_time = time.process_time() - start_domain_load
    print("Domain Loading time =",domain_load_time)
    return domain
domain = set_domain()
# print (domain)
# print("center lat,long ",center_lat,center_long)

# sanity check after normalization
## print(old_coords[:,1]+ normalize_lat == coords[:,0],old_coords[:,2]+normalize_long == coords[:,1] )
# print(coords)


# generate points for Quad tree
start_generatin_points = time.process_time()
points = [Point(*coord) for coord in p_coords]
points_load_time = time.process_time() - start_generatin_points
print("Points feeding tree prep time =",points_load_time)
# print(len(points))

# fig = plt.figure()
# ax = plt.subplot()
# ax.scatter([p.x for p in points], [p.y for p in points], s=4)

start_building_tree = time.process_time()
qtree = tree_builder(domain,points)
gen_time = time.process_time() - start_building_tree
print("Tree gen time =",gen_time)

print('Number of points in the domain =', len(qtree))

# fig = plt.figure()
# ax = plt.subplot()
# ax.set_xlim(318.701, 318.703)
# ax.set_ylim(55.0025, 55.0026)
# qtree.draw(ax)
# ax.scatter([p.x for p in points], [p.y for p in points], s=2)
# ax.set_xticks([])
# ax.set_yticks([])

# red search area bounding box rect.
# region = Rect(center_long, center_lat, 0.005, 0.005)

# SET PRECISION TO 7 places after decimal
factor = 10.0 ** 7
coords[:,0] = np.trunc(coords[:,0] * factor) / factor
coords[:,1] = np.trunc(coords[:,1] * factor) / factor


# empty list initialized to store nearest neighbours OF ALL COORDS
fastest_nearest_neighbours_baby = []

# QUERYING For ALL POINTS
query_allpoints = time.process_time()
# now iterate over all coordinates and store their NN after querying them on the tree.
for i in range(0,50000):
# for i in range(0,10):
    # print("Checking for coord ",i+1)
    found_points = []
    neighs = []
    lon  = coords[i][0]
    lat  = coords[i][1]
    # RETRIVE DIRECTION FOR THIS POINT
    dir_ith_pt = original_data[i][3]
    # print("i,dir_ith_pt    " , i,dir_ith_pt)
    # # for Scatter:
    # fig = plt.figure()
    # ax = plt.subplot()
    # # ax.set_xlim(318.2, 310)
    # # ax.set_ylim(55.001, 55.003)
    # ax.set_xlim(317, 319)
    # ax.set_ylim(53, 56)
    # # all points in db in grey
    # # ax.scatter([p.x for p in points], [p.y for p in points],facecolors='grey', s=2)

    # SET QUERY REGION OF SEARCH AREA OF "0.001 X 0.001" CENTERED AT LON,LAT AND
    coord_region = Rect(lon, lat, 0.001, 0.001)    
    # QUERY TREE FOR THIS POINTS(lon,lat) NN
    qtree.query(coord_region, found_points)
    # print("found_points for this coord",found_points)
    q_longi,q_lati = normalizer(lon,lat)
    query_coord = (q_longi,q_lati)
    # LOG QUERY TIME FOR FILTERING NN POINTS
    # querying_nn_points_t = time.process_time()
    for j in range (0,len(found_points)):
        # SELECT ID OF NN POINT OF QUERY POINT
        id = found_points[j]
        # print(abs(id[1]-dir_ith_pt))
        longitu = original_data[id-1][1]
        latitu  = original_data[id-1][2]
        diru    = original_data[id-1][3]
        # print("id,longitu,latitu,dir",id,longitu,latitu,original_data[id-1][3])
        # CALCULATE ANGLE CHANGE in viEW DIRECTION
        anglediff = (original_data[id-1][3]-dir_ith_pt + 180 + 360) % 360 - 180
#         # print (anglediff)
        if (anglediff <= 45 and anglediff>=-45):
#         # DIStANCE AND DIRECTION METRICS
#         # if abs(id[1]-dir_ith_pt) <= 45 :
#             # print("nn_point,query_coord",nn_point,query_coord)
#             dist = distance.euclidean(nn_point, query_coord)
            neighs.append(id)
    # print ("neighs ",neighs)
querying_total_time = time.process_time() - query_allpoints
print("\n Query time for 50000 coords = ",querying_total_time)

#     # APPEND NEAREST NIGHTBOURS IN LIST
#     fastest_nearest_neighbours_baby.append(neighs)
#     print(i+1,"neighs",fastest_nearest_neighbours_baby[i])
#     # # draw quad tree
#     # qtree.draw(ax)
#     # # ref coord in black 
#     # ax.scatter(lon,lat,facecolors='black', edgecolors='y', s=35)
#     # # found neighs in red
#     # ax.scatter([p.x for p in found_points], [p.y for p in found_points],facecolors='red', edgecolors='r', s=4)
#     # coord_region.draw(ax, c='pink')
#     # plt.tight_layout()
#     # plt.show()

# # for i in range(0,5):
# #     print (i, "'s Neighs = " , fastest_nearest_neighbours_baby[i])
    
# query_time = time.process_time() - query_allpoints
# print("\nquery time for ",len(coords)," coordintes = ",query_time)

# print(fastest_nearest_neighbours_baby[0])
# print('Number of found points =', len(found_points))

# ax.scatter([p.x for p in found_points], [p.y for p in found_points],
#            facecolors='none', edgecolors='r', s=4)
# lon  = coords[0][0]
# lat  = coords[0][1]
# ax.scatter(lon,lat,facecolors='green', edgecolors='g', s=10)
# region.draw(ax, c='r')

# plt.tight_layout()
# plt.show()