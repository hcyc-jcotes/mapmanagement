from sklearn.neighbors import DistanceMetric

dist = DistanceMetric.get_metric('minkowski')
# 71
V=[[-34.9206615,138.593159],[-34.9204979,138.5932858]]
# 70
V2=[[-34.9206615,138.593159],[-34.9203855,138.5932794]]

distance = dist.pairwise(V)
distance2 = dist.pairwise(V2)

print ("dist",distance)
print ("dist2",distance2)
# from sklearn.neighbors import DistanceMetric
# dist = DistanceMetric.get_metric('minkowski')
# X = [[138.5957872, -34.9182049],[138.5956894, -34.9181906]]
# print(dist.pairwise(X))
# array([[ 0.        ,  5.19615242],
#        [ 5.19615242,  0.        ]])
# A = (
#     [1,0.000456],
#     [2,0.000455],
#     [3,0.000324],
#     [6,0.000343]
#     )
# final_neigh =[]
# B=sorted(A,key=lambda x:x[1])
# # print("neighs_sorted = ",neig)				
# final_neigh+=([x[0] for x in B])
# print(final_neigh)