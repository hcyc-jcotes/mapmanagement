from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APITestCase
from .models import Region, Sequence, Coordinate_property, User
from .views import angleFromCoordinateLib, angleFromCoordinate
from .serializers import CoordinatePropertySerializer, RegionSerializer, SequenceSerializer
from random import uniform
from .models import Region, Sequence, Coordinate_property
from .views import getdirection, angleFromCoordinateLib, angleFromCoordinate, neighbors, deltaneighbors
from random import uniform
import numpy as np
from utils.quadtree import Point, Rect, QuadTree
from sklearn.neighbors import KDTree

# Unit tests for API views
# List of Coordinates from the API


class CoordinatePropertyListTestCase(APITestCase):
    def test_list_coordinates(self):
        coordinates_count = Coordinate_property.objects.count()
        response = self.client.get('/api/coordinates/')
        # check that the number of coordinates is correct
        self.assertEqual(len(response.data), coordinates_count)

# List of Regions from the API


class RegionListTestCase(APITestCase):
    def test_list_regions(self):
        regions_count = Region.objects.count()
        response = self.client.get('/api/regions/')
        # check that the number of regions is correct
        self.assertEqual(len(response.data), regions_count)

# List of Sequences from the API


class SequenceListTestCase(APITestCase):
    def test_list_sequences(self):
        sequences_count = Sequence.objects.count()
        response = self.client.get('/api/sequences/')
        # check that the number of sequences is correct
        self.assertEqual(len(response.data), sequences_count)


class DirectionTestCase(TestCase):
    def testcalculatedirection(self):
        count = 0
        while count < 100:
            xfirst = uniform(-180, 180)
            yfirst = uniform(-90, 90)
            xsecond = uniform(-180, 180)
            ysecond = uniform(-90, 90)
            firstresult = angleFromCoordinate(yfirst, xfirst, ysecond, xsecond)
            secondresult = angleFromCoordinateLib(
                yfirst, xfirst, ysecond, xsecond)
            error = abs(firstresult - secondresult)
            if (error > 180):
                error = 360 - error
            error = error/360
            count += 1
            self.assertTrue(0 <= error <= 0.05)

# Unit tests for serializers


class TestRegionSerializer(TestCase):
    def setUp(self):
        self.region_attributes = {
            "id": 1,
            "name": "Saigon",
            "min_longitude": 123.45,
            "min_latitude": 67.89,
            "max_longitude": 143.21,
            "max_latitude": 88.76,
            "view_longitude": 131.2,
            "view_latitude": 81.91,
            "stored_at": "2021-05-18 10:48:00"
        }

        self.region = Region.objects.create(**self.region_attributes)
        self.serializer = RegionSerializer(instance=self.region)

    def test_contains_expected_fields(self):
        data = self.serializer.data

        self.assertEqual(set(data.keys()), set(['id', 'name', 'min_longitude', 'min_latitude', 'max_longitude',
                                                'max_latitude', 'view_longitude', 'view_latitude', 'last_update', 'stored_at']))

    def test_name_field_content(self):
        data = self.serializer.data

        self.assertEqual(data['name'], self.region_attributes['name'])

    def test_max_longitude_field_content(self):
        data = self.serializer.data

        self.assertEqual(data['max_longitude'],
                         self.region_attributes['max_longitude'])

    def test_stored_at_field_content(self):
        data = self.serializer.data

        self.assertEqual(data['stored_at'],
                         self.region_attributes['stored_at'])


class TestCoordinatePropertySerializer(TestCase):
    def setUpCoordinate(self):
        self.coordinate_attributes = {
            "id": 1,
            "ca": 11.23,
            "image_key": "ABC",
            "sequence_key": 1,
            "longitude": 156.23,
            "latitude": 56.23,
            "direction": 100,
            "neighbors": "2",
            "weather":  "N.A.",
            "filename": "test.png"
        }

        self.coordinate = Coordinate_property.objects.create(
            **self.coordinate_attributes)
        self.serializer = CoordinatePropertySerializer(
            instance=self.coordinate)


class TestSequenceSerializer(TestCase):
    def setUpSequence(self):
        self.sequence_attributes = {
            "id": 1,
            "camera_make": "Apple",
            "captured_at": "2021-05-18 10:48:00",
            "created_at": "2021-05-18 10:48:00",
            "key": "ABCDEFG",
            "pano": True,
            "region_key_id": 1,
            "user_key_id": 1,
            "stored_at": "2021-05-18 10:48:00",
            "points_in_seq": 88.76,
        }

        self.sequence = Sequence.objects.create(**self.sequence_attributes)
        self.serializer = SequenceSerializer(instance=self.sequence)


class TestQuadTree(TestCase):
    def test_nearest_neighbours_algo(self):
        N = 100
        np.random.seed(60)
        width, height = 600, 400
        NNcoords = np.random.randn(N, 2) * height/3 + (width/2, height/2)
        id = np.arange(1, N+1, 1)
        coords = np.insert(NNcoords, 0, id, axis=1)
        # Generate QuadTree points
        points = [Point(*coord) for coord in coords]
        # Set Domain
        domain = Rect(width/2, height/2, width, height)
        # Make Quad Tree
        qtree = QuadTree(domain, 3)
        for point in points:
            qtree.insert(point)
        region = Rect(coords[0][1], coords[0][2], 150, 150)
        found_points = []
        # Query Quad Tree
        qtree.query(region, found_points)
        found_points = np.array(sorted(found_points))
        print("Quad Tree Neighbours : ", found_points)
        # Make KD Tree
        ktree = KDTree(NNcoords, leaf_size=3)
        indx = []
        # Query KD Tree
        dist, ind = ktree.query(NNcoords[:1], k=len(found_points))
        ids = ind[0]
        for i in range(0, len(ids)):
            ids[i] = ids[i]+1
            indx.append(ids[i])
        indx = np.sort(indx)
        print("Kd Tree Neighbours   : ", indx)
        for x, y in zip(found_points, indx):
            self.assertEqual(x, y)
