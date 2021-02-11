from vincenty import vincenty
from geopy import distance
from itertools import product ,combinations
from decimal import Decimal
from math import cos, sin, sqrt, radians, degrees, asin, atan2
from numpy import dot ,cross

datas = [((23.88595474585783, 121.3827856231044), 129.65),
((24.58457763544925, 121.68409782140633), 54.41), 
((25.18538614875814, 121.57913094113091), 17.13)]

# All coordinate set structure (latitude,longitude) !
# Radius unit <km>

def Distant(coordinate_1,coordinate_2):
    return distance.distance(coordinate_1,coordinate_2).km
'''
def Distant(coordinate_1,coordinate_2):
    # Function here calaulate distanse by WGS 
    # Using Vincenty's formula
    return vincenty(coordinate_1 , coordinate_2)
'''
def Devider(up,down,right,left):
    # Function here devide the target area into 2*2 pcs 
    # and return their center coordinates <itertools.product object> 
    longitude = [i*((right-left)/4)+left for i in range(1,4,2)]
    latitude  = [i*(( up  -down)/4)+down for i in range(1,4,2)]
    return product(longitude,latitude)

def geocentric_converter(coord):
    # Function here convert the longitude & latitude into geocentric coordinate
    # Not ellipsoidal case !
    # return (x,y,z) <tuple>
    longitude = radians(coord[1])
    latitude  = radians(coord[0])
    x = Decimal(cos(longitude)*cos(latitude))  # x = cos(lon)*cos(lat)
    y = Decimal(sin(longitude)*cos(latitude))  # y = sin(lon)*cos(lat)
    z = Decimal(sin(latitude))                 # z = sin(lat)
    return (x,y,z)

def intersection(dat1,dat2):
    # Function here calculate two coords' intersection points
    # Not ellipsoidal case !
    # ref:https://gis.stackexchange.com/questions/48937/calculating-intersection-of-two-circles
    geocentric_1 = geocentric_converter(dat1[0])
    geocentric_2 = geocentric_converter(dat2[0])
    r1 = Decimal(radians(((dat1[1]*1000)/1852)/60)) 
    r2 = Decimal(radians(((dat2[1]*1000)/1852)/60))
    
    q = Decimal(dot(geocentric_1,geocentric_2))
    if q**2 != 1 :
        a = (Decimal(cos(r1)) - Decimal(cos(r2))*q) / (1 - q**2)
        b = (Decimal(cos(r2)) - Decimal(cos(r1))*q) / (1 - q**2)
        n = cross(geocentric_1,geocentric_2)

        x0_1 = [a*i for i in geocentric_1]
        x0_2 = [b*i for i in geocentric_2]
        x0 = [sum(i) for i in zip(x0_1, x0_2)]

        if (dot(x0, x0) <= 1) & (dot(n,n) != 0):
            t = Decimal(sqrt((1 - dot(x0, x0)) / dot(n,n)))
            t1 = t
            t2 = -t

            result1 = x0 + t1*n
            result2 = x0 + t2*n
        
            result1_lat = degrees(asin (result1[2]))
            result1_lon = degrees(atan2(result1[1], result1[0]))
            result1 = (result1_lat, result1_lon)

            result2_lat = degrees(asin (result2[2]))
            result2_lon = degrees(atan2(result2[1], result2[0]))
            result2 = (result2_lat, result2_lon)
            return [result1, result2]
        elif (dot(n,n) == 0):
            return("The centers of the circles can be neither the same point nor antipodal points.")
        else:
            return("The circles do not intersect")
    else:
        return("The centers of the circles can be neither the same point nor antipodal points.")

def area(p1,p2,p3):
    vec1 = (p2[0]-p1[0],p2[1]-p1[1])
    vec2 = (p3[0]-p1[0],p3[1]-p1[1])
    return vec1[0]*vec2[1]-vec1[1]*vec2[0]

def perimiter(p1,p2,p3):
    return Distant(p1,p2)+Distant(p3,p2)+Distant(p1,p3)

'''
def multilateration(data):
    # Using three point(data) as initial point
    latitudes = [i[0][0] for i in data]
    longitudes= [i[0][1] for i in data]
    up,down,right,left = max(latitudes),min(latitudes),max(longitudes),min(longitudes)
    lon_length,lat_length = 10000,10000
    while (lon_length>0.0000000000000000000000001) or (lat_length>0.0000000000000000000000001):
        lon_length = (right-left)/20
        lat_length = ( up  -down)/20
        mid_lon =  [i*lon_length + left for i in range(1,20,2)]
        mid_lat  = [i*lat_length + down for i in range(1,20,2)]
        mid_coords = list(product(mid_lat,mid_lon))
        result = [(Distant(i,datas[0][0])-datas[0][1])**2+(Distant(i,datas[1][0])-datas[1][1])**2+(Distant(i,datas[2][0])-datas[2][1])**2 for i in mid_coords]
        target = mid_coords[result.index(min(result))]
        up,down,right,left = target[0]+lat_length,target[0]-lat_length,target[1]+lon_length,target[1]-lon_length  
    return target
'''

def multilateration(data):
    # Using three intersection point as initial point (6 choose 3,by minimum the perimiter)
    counterpart = intersection(data[0],data[1])+intersection(data[1],data[2])+intersection(data[0],data[2]) 
    combs = list(combinations(counterpart,3))
    comb_area = [perimiter(i[0],i[1],i[2]) for i in combs]
    target = list(combs)[comb_area.index(min(comb_area))]
    print(target)
    latitudes = [i[0] for i in target]
    longitudes= [i[1] for i in target]
    up,down,right,left = max(latitudes),min(latitudes),max(longitudes),min(longitudes)
    lon_length,lat_length = 10000,10000
    while (lon_length>0.000000000001) or (lat_length>0.00000000001):
        lon_length = (right-left)/20
        lat_length = ( up  -down)/20
        mid_lon =  [i*lon_length + left for i in range(1,20,2)]
        mid_lat  = [i*lat_length + down for i in range(1,20,2)]
        mid_coords = list(product(mid_lat,mid_lon))
        result = [(Distant(i,datas[0][0])-datas[0][1])**2+(Distant(i,datas[1][0])-datas[1][1])**2+(Distant(i,datas[2][0])-datas[2][1])**2 for i in mid_coords]
        target = mid_coords[result.index(min(result))]
        up,down,right,left = target[0]+lat_length,target[0]-lat_length,target[1]+lon_length,target[1]-lon_length  
    return target

print(multilateration(datas))
