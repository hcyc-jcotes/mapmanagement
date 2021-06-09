import numpy as np
import matplotlib.pyplot as plt
from quadtree import Point, Rect, QuadTree
from matplotlib import gridspec

np.random.seed(60)

width, height = 600, 400

# Generate coordinate data
N = 100
coords = np.random.randn(N, 2) * height/3 + (width/2, height/2)
# print (coords.shape)

# Add id field to coordinate data
id = np.arange(1,N+1,1)
coords = np.insert(coords, 0, id, axis=1)
# print(coords)

# Generate QuadTree points
points = [Point(*coord) for coord in coords]

# Set Domain
domain = Rect(width/2, height/2, width, height)

# Make Tree
qtree = QuadTree(domain, 3)
for point in points:
    qtree.insert(point)

fig = plt.figure()
ax = plt.subplot()
ax.set_xlim(0, width)
ax.set_ylim(0, height)
qtree.draw(ax)

# Scatter all points
ax.scatter([p.x for p in points], [p.y for p in points],edgecolors='blue', s=4)
ax.set_xticks([])
ax.set_yticks([])

# Make region around query pt (140,190)
region = Rect(140, 190, 15, 150)
found_points = []
qtree.query(region, found_points)
# print('Number of found points =', len(found_points))

ax.scatter(140,190, facecolors='red', edgecolors='b', s=42)

# Scatter NN in red
ax.scatter([coords[p-1][1] for p in found_points], [coords[p-1][2] for p in found_points],
           facecolors='red', s=12)

# Draw query region around the query point
region.draw(ax, c='r')

ax.invert_yaxis()
plt.tight_layout()
plt.show()