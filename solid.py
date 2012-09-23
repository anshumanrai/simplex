import sys
import math
import xml.dom.minidom
from OCC.Display.SimpleGui import init_display
from OCC.gp import *
from OCC.GC import *
from OCC.Utils.Construct import make_vertex, make_edge
from OCC.BRepPrim import BRepPrim_Cylinder
from OCC.BRepPrimAPI import *

#distance between a point a (x1, y1) and a point (x2,y)
def distance_two_points(x1, y1, z1, x2, y2,z2):
	z2z1 = float(z2) - float(z1)
	y2y1 = float(y2) - float(y1)
	x2x1 = float(x2) - float(x1)		

	distanceSquared = z2z1*z2z1 + y2y1*y2y1 + x2x1*x2x1
	retVal = math.sqrt(distanceSquared)
	return retVal


display, start_display, add_menu, add_function_to_menu = init_display()
print sys.argv[1]
dom = xml.dom.minidom.parse(sys.argv[1])
vertices = dom.getElementsByTagName('vertex')
for vertex in vertices:
	x = int(vertex.attributes['x'].value)
	y = int(vertex.attributes['y'].value)	
	z = int(vertex.attributes['z'].value)
	point = gp_Pnt(x,y,z)
	display.DisplayShape(make_vertex(point))
edges = dom.getElementsByTagName('edge')
for edge in edges:
	x1 = int(edge.attributes['x1'].value)
	y1 = int(edge.attributes['y1'].value)	
	z1 = int(edge.attributes['z1'].value)
	x2 = int(edge.attributes['x2'].value)
	y2 = int(edge.attributes['y2'].value)	
	z2 = int(edge.attributes['z2'].value)
	segment = GC_MakeSegment(gp_Pnt(x1,y1,z1),gp_Pnt(x2,y2,z2)).Value()	
	display.DisplayShape(make_edge(segment))	
cylinders = dom.getElementsByTagName('cylinder')
for cylinder in cylinders:
	x1 = int(cylinder.attributes['x1'].value)
	y1 = int(cylinder.attributes['y1'].value)	
	z1 = int(cylinder.attributes['z1'].value)
	x2 = int(cylinder.attributes['x2'].value)
	y2 = int(cylinder.attributes['y2'].value)	
	z2 = int(cylinder.attributes['z2'].value)
	radius = int(cylinder.attributes['radius'].value)
	height = distance_two_points(x1,y1,z1,x2,y2,z2)
	vector = gp_Vec(x2-x1, y2-y1, z2-z1)
	direction = gp_Dir(vector)
	axis = gp_Ax2(gp_Pnt(x1,y1,z1),direction)
	cylinderShape = BRepPrimAPI_MakeCylinder(axis,radius,height).Shape()
	
	display.DisplayShape(cylinderShape)
start_display()
