import sys
import xml.dom.minidom
from OCC.Display.SimpleGui import init_display
from OCC.gp import *
from OCC.GC import *
from OCC.Utils.Construct import make_vertex, make_edge


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

start_display()

