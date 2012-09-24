import gtk
import pygtk
import cairo
import math
from xml.dom.minidom import Document
import xml.etree.ElementTree as ET
class View:
	FrontView = 1
	TopView = 2
	SideView = 3
	def __init__(self, type, drawObject):
		#copy initialization variables
		#type of view - front, top or side		
		self.type = type
		#the draw object which has initialized this view - for book keeping purposes 
		self.drawObject = drawObject
		#initialize variables
		self.viewType = View.FrontView	
		self.drawingAreaWidth = 420
		self.drawingAreaHeight = 400
		self.tableWidth = 420
		self.tableHeight = 400
		self.zoomFactor = 5
		self.zoomLevel = 1
		self.viewDict = {}
		self.viewDict['lines'] = []
		self.viewDict['circles'] = []
		self.viewDict['arcs']= []
		self.viewDict['vertices'] = []
		

		#initialze normal area
		self.drawingArea = gtk.DrawingArea()
		self.scrolledWindow = gtk.ScrolledWindow()
		self.scrolledWindow.add_with_viewport(self.drawingArea)
		self.table = gtk.Table(3,2)
		self.hRuler = gtk.HRuler()
		self.vRuler = gtk.VRuler()
		self.hRuler.set_range(0, 400, 0, 400)
		self.vRuler.set_range(0, 300, 0, 300)
		self.table.attach(self.hRuler, 1, 2, 0, 1, yoptions=0)
		self.table.attach(self.vRuler, 0, 1, 1, 2, xoptions=0)
		self.table.attach(self.scrolledWindow, 1, 2, 1, 2)
		self.labelView = gtk.Label("")
		if (self.type == View.FrontView):	
			self.labelView = gtk.Label("Front View")
		elif (self.type == View.TopView):
			self.labelView = gtk.Label("Top View")			
		elif (self.type == View.SideView):
			self.labelView = gtk.Label("Side View")
		#set the size of widgets
		self.drawingArea.set_size_request(self.drawingAreaWidth, self.drawingAreaHeight)
		self.table.set_size_request(self.tableWidth, self.tableHeight)
		#connect the signals
		self.drawingArea.connect("motion-notify-event", self.on_DrawingArea_motion_notify)
		self.drawingArea.connect("button-press-event", self.on_DrawingArea_button_pressed)
		self.drawingArea.connect("button-release-event", self.on_DrawingArea_button_released)
		self.drawingArea.connect('expose-event',self.drawingarea_expose)
		self.drawingArea.set_events(gtk.gdk.EXPOSURE_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
		return
	#Given gtk coordiantes of a drawing area, give out real coordinates
	def translate_gtk_to_real(self,x, y):
		y = y / (self.zoomFactor * self.zoomLevel)
		y = self.drawingAreaHeight - y
		x = x / (self.zoomFactor * self.zoomLevel)

		return (x, y)
	#Given real coordiantes of a drawing area, give out gtk coordinates
	def translate_real_to_gtk(self,x,y):
		x = x * self.zoomLevel * self.zoomFactor
		y = y * self.zoomLevel * self.zoomFactor
		y = self.drawingAreaHeight * self.zoomLevel * self.zoomFactor - y
		return (x, y)

	#Given gtk dimension of a drawing area, give out real dimension
	def translate_dimension_gtk_to_real(self,x):
		x = x / (self.zoomFactor * self.zoomLevel)
		return x
	#Given real dimension of a drawing area, give out gtk dimension
	def translate_dimension_real_to_gtk(self,x):
		x = x * self.zoomLevel * self.zoomFactor
		return x
	def show(self):
		self.drawingArea.show()
		self.scrolledWindow.show()
		self.table.show()
		self.hRuler.show()
		self.vRuler.show()
		self.hRuler.show()
		self.vRuler.show()
		return
	def add_to_notebook(self, notebook):
		notebook.append_page(self.table, self.labelView)		
		return
	
	
	def drawingarea_expose(self, widget, data):
		self.drawingArea.set_size_request(self.drawingAreaWidth * self.zoomLevel * self.zoomFactor, self.drawingAreaHeight * self.zoomLevel * self.zoomFactor)
		self.table.set_size_request(self.tableWidth * self.zoomLevel * self.zoomFactor, self.tableHeight * self.zoomLevel * self.zoomFactor)	
		self.cairoContext = widget.window.cairo_create()
		self.draw_grid()
		for line in self.viewDict['lines']:
			(xGridClicked, yGridClicked, xGridReleased, yGridReleased,solid, selected) = line
			xGridClicked, yGridClicked = self.translate_real_to_gtk(xGridClicked, yGridClicked)
			xGridReleased, yGridReleased = self.translate_real_to_gtk(xGridReleased, yGridReleased)
			self.draw_line(xGridClicked, yGridClicked, xGridReleased, yGridReleased, solid, selected, 1.0)
		for circle in self.viewDict['circles']:
			(xGridClicked, yGridClicked, radius, solid, selected) = circle
			xGridClicked, yGridClicked = self.translate_real_to_gtk(xGridClicked, yGridClicked)
			radius = self.translate_dimension_real_to_gtk(radius)
			self.draw_circle(xGridClicked, yGridClicked, radius, solid, selected, 1.0)
		return
	

	def vertex_in_view(self, vertexIn):
		xIn, yIn = vertexIn
		for vertex in self.viewDict['vertices']:
			x,y = vertex
			if ((x == xIn) and (y == yIn)):
				return True
		return False
	def edge_in_view(self, edgeIn):
		print edgeIn
		x1In, y1In, x2In, y2In = edgeIn
		for edge in self.viewDict['lines']:
			x1, y1, x2, y2, solid, selected= edge
			#check if x1In, y1In lies on the edge
			distancepIn1p1 = self.distance_two_points(x1In,y1In, x1, y1)
			distancepIn1p2 = self.distance_two_points(x1In,y1In, x2, y2)
			distancep1p2 = self.distance_two_points(x1,y1,x2,y2)
			if ((distancepIn1p1 + distancepIn1p2) == distancep1p2):
				#check if x2In, y2In lies on the edge
				distancepIn2p1 = self.distance_two_points(x2In,y2In, x1, y1)
				distancepIn2p2 = self.distance_two_points(x2In,y2In, x2, y2)
				if ((distancepIn2p1 + distancepIn2p2) == distancep1p2):
					return True
	def draw_circle(self,x, y, radius, solid, selected, width):
		if solid:
			self.cairoContext.set_dash(())
		else:
			self.cairoContext.set_dash((5,3))
		if selected:
			self.cairoContext.set_source_rgb(1,0,0)
		else:
			self.cairoContext.set_source_rgb(0,0,0)
		self.cairoContext.set_line_width(width)
		self.cairoContext.move_to(x, y)
		self.cairoContext.arc(x, y, radius, 0, 2*math.pi) 
		self.cairoContext.stroke()
		return	

	def draw_line(self,x1, y1, x2, y2, solid,selected,width):
		if solid:
			self.cairoContext.set_dash(())
		else:
			self.cairoContext.set_dash((5,3))
			
		if selected:
			self.cairoContext.set_source_rgb(1,0,0)
		else:
			self.cairoContext.set_source_rgb(0,0,0)
		
		
		self.cairoContext.move_to(x1, y1)
		self.cairoContext.line_to(x2, y2)
		self.cairoContext.set_line_width(width)		
		self.cairoContext.stroke()
		return


	def draw_grid(self):
		i = 0
		x1 = i
		y1 = 0
		x2 = i
		y2 = self.drawingAreaHeight
		while (i < self.drawingAreaWidth):
			x1 = i
			y1 = 0
			x2 = i
			y2 = self.drawingAreaHeight
			x1,y1 = self.translate_real_to_gtk(x1, y1)
			x2,y2 = self.translate_real_to_gtk(x2, y2)
			self.draw_line(x1, y1, x2, y2, True, False, 0.1)
			i = i + 1
		i=0
		x1 = 0
		y1 = i
		x2 = self.drawingAreaWidth
		y2 = i
		while (i < self.drawingAreaHeight):
			x1 = 0
			y1 = i
			x2 = self.drawingAreaWidth
			y2 = i
			x1,y1 = self.translate_real_to_gtk(x1, y1)
			x2,y2 = self.translate_real_to_gtk(x2, y2)
			self.draw_line(x1, y1, x2, y2, True, False, 0.1)
			i = i + 1

	#distance between a point c (x,y) and the segment between the points a (x1, y1) and b (x2, y2) 
	def distance_vector(self,x,y, x1, y1, x2, y2):
		if (x == x1) and (y == y1):
			return 0
		if (x == x2) and (y == y2):
			return 0
		x = float(x)
		y = float(y)
		x1 = float(x1)
		y1 = float(y1)
		x2 = float(x2)
		y2 = float(y2)
		ab = y2-y1, x2-x1           		# Vector ab
		dd = math.sqrt(ab[0]**2+ab[1]**2)         # Length of ab
		ab = ab[0]/dd, ab[1]/dd               	# unit vector of ab
		n = -ab[1], ab[0]                    	# normal unit vector to ab
		ac = x2-x, y2-y          		# vector ac
		retVal = math.fabs(ac[0]*n[0]+ac[1]*n[1]) # Projection of ac to n (the minimum distance)
		return retVal

	#distance between a point a (x1, y1) and a point (x2,y)
	def distance_two_points(self, x1, y1, x2, y2):
		y2y1 = float(y2) - float(y1)
		x2x1 = float(x2) - float(x1)		
		distanceSquared = y2y1*y2y1 + x2x1*x2x1
		retVal = math.sqrt(distanceSquared)
		return retVal
	#distance between a point c (x,y) and the segment between the points a (x1, y1) and b (x2, y2) 
	def distance_area(self,x,y, x1, y1, x2, y2):
		if (x == x1) and (y == y1):
			return 1
		if (x == x2) and (y == y2):
			return 0
		ab = self.distance_two_points(x1, y1, x2, y2)
		bc = self.distance_two_points(x2,y2, x,y)
		ca = self.distance_two_points(x,y,x1,y1)
		s = (ab + bc + ca)/2
		area = math.sqrt(s*(s-ab)*(s-bc)*(s-ca))
		if not(ab == 0):
			retVal = (2 * area) / ab
		else:
			return 999999
		return retVal

	def on_DrawingArea_motion_notify(self, widget, event):	
		return		

	def on_DrawingArea_button_pressed(self, widget, event):
		
     		# was it a multiple click?
		if event.type == gtk.gdk.BUTTON_PRESS:
			#store the point coordinates
			#find the closest point on the grid
			xGrid = int(event.x)
			yGrid = int(event.y)
			self.xGridClicked = xGrid
			self.yGridClicked = yGrid
			self.xGridClicked, self.yGridClicked = self.translate_gtk_to_real(self.xGridClicked, self.yGridClicked)
			

		if self.drawObject.drawMode == self.drawObject.selectMode:
			#iterate over the lines and the line to which the event point is closest mark as selected
			x = event.x
			y = event.y
			x,y = self.translate_gtk_to_real(event.x, event.y)		
			lines = self.viewDict['lines']
			circles = self.viewDict['circles']
			i = 0
			lineSelected = False;
			circleSelected = False
			#Treat distances less than 1 pixel unit as select zone
			minDistance = 1000
			for line in lines:
				(x1,y1,x2,y2,solid,selected) = line
				curDistance = self.distance_area(x,y,x1,y1,x2,y2)
				if curDistance < minDistance:
					minDistance = curDistance
					lineMinIndex = i
					lineSelected = True 			
				i = i + 1
			
			for circle in circles:
				(xc,yc,circle,solid,selected) = circle
				'''
				for a circle distance is the absolute value of radius minus the distance 
				between the point and the center of the circle
				'''
				distancePointCenter = self.distance_two_points(x, y, xc, yc)
				curDistance = radius = distancePointCenter
				if curDistance < 0:	
					curDistance = (-1) * curDistance
				if curDistance < minDistance:
					circleSelected = True
					solidLineSelected = False
					dashedLineSelected = False
					circleMinIndex = i
				i = i + 1		
				
			if lineSelected:
				x1, y1, x2, y2, solid, selected = lines[lineMinIndex]
				if selected:
					lines[lineMinIndex] = (x1, y1, x2, y2, solid, False)
				else:
					lines[lineMinIndex] = (x1, y1, x2, y2, solid, True)
			
			elif circleSelected:
					xc, yc, radius, solid, selected = circles[circleMinIndex]
					if selected:
						circles[circleMinIndex] = (xc, yc, radius, solid, False)
					else:
						circles[circleMinIndex] = (xc, yc, radius, solid, True)
			
			
			self.drawingArea.queue_draw()
		return
		
	def on_DrawingArea_button_released(self, widget, event):
		
    		#find the closest point on the grid
		xGrid = int(event.x)
		yGrid = int(event.y)
		self.xGridReleased = xGrid
		self.yGridReleased = yGrid
		lines = self.viewDict['lines']
		circles = self.viewDict['circles']
		arcs = self.viewDict['arcs']
		self.xGridReleased, self.yGridReleased = self.translate_gtk_to_real(self.xGridReleased, self.yGridReleased)
		#store line segments as end points and selected flag		
		if self.drawObject.solidMode == self.drawObject.solid :
			if self.drawObject.drawMode == self.drawObject.lineMode :
				lines.append((self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased, True, False))
			elif self.drawObject.drawMode == self.drawObject.circleMode:
				radius = self.distance_two_points(self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased)
				radius = int(radius)
				circle = (self.xGridClicked, self.yGridClicked, radius, True, False)
				circles.append(circle)	
			elif self.drawObject.drawMode == self.drawObject.arcMode:
				radius = self.distance_two_points(self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased)
				radius = int(radius)
				self.saveAsFile = ""
				dialog = gtk.Dialog("Open", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
				startAngleLabel = gtk.Label()
				startAngleLabel.set_text("Start Angle")
				dialog.vbox.pack_start(startAngleLabel)
				startAngleLabel.show()
				startAngle = gtk.Entry()			
				dialog.vbox.pack_start(startAngle)
				startAngle.show()	

				endAngleLabel = gtk.Label()
				endAngleLabel.set_text("End Angle")
				dialog.vbox.pack_start(endAngleLabel)
				endAngleLabel.show()
				endAngle = gtk.Entry()			
				dialog.vbox.pack_start(endAngle)
				endAngle.show()
	
				dialog.run
				response = dialog.run()
				if response == gtk.RESPONSE_OK:
					startAngle = int(startAngle.get_text())
					endAngle = int(endAngle.get_text())
					radius = self.distance_two_points(self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased)
					arc = (self.xGridClicked, self.yGridClicked,radius, startAngle, endAngle, True,False)
					 
				elif response == gtk.RESPONSE_CANCEL:
					print "cancel"
				dialog.destroy()
		
				
		elif self.drawObject.solidMode == self.drawObject.dashed:
			if self.drawObject.drawMode == self.drawObject.lineMode :
				lines.append((self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased, False, False))
			elif self.drawObject.drawMode == self.drawObject.circleMode:
				radius = self.distance_two_points(self.xGridClicked,self.yGridClicked,self.xGridReleased,self.yGridReleased)
				radius = int(radius)		
				circle = (self.xGridClicked, self.yGridClicked, radius, False, False)
				circles.append(circle)
		self.compute_vertices()	
		
		self.drawingArea.queue_draw()
		return

	def import_xml(self, xml_str):
		#delete all the edges
		#read from xml and insert edges accordingly
		return

	def compute_vertices(self):
		vertices_dict = {}
		self.viewDict['vertices'] = []
		vertices_list = self.viewDict['vertices']
		for line in self.viewDict['lines']:
			x1,y1,x2,y2,solid, selected = line
			if not ((x1,y1) in vertices_dict):
				vertices_dict[(x1,y1)]=(x1,y1)
				vertices_list.append((x1,y1))	
			if not ((x2,y2) in vertices_dict):
				vertices_dict[(x2,y2)]=(x2,y2)
				vertices_list.append((x2,y2))
	def print_xml(self):
		#create the root element
		doc = Document()
		if self.type == View.FrontView: 
			viewElem = doc.createElement("front_view")
		elif self.type == View.TopView:
			viewElem = doc.createElement("top_view")
		elif self.type == View.SideView:
			viewElem = doc.createElement("side_view")		
		doc.appendChild(viewElem)
		#create the vertices element
		verticesElem = doc.createElement("vertices")
		viewElem.appendChild(verticesElem)
		#iterate over vertices and add them to the xml
		for vertex in self.viewDict['vertices']:
			x1,y1 = vertex
			vertexElem1 = doc.createElement("vertex")
			vertexElem1.setAttribute("x",str(x1))
			vertexElem1.setAttribute("y",str(y1))				
			verticesElem.appendChild(vertexElem1)
		#create the edges element
		edgesElem = doc.createElement("edges")
		viewElem.appendChild(edgesElem)
		#iterate over the edges and add them to the xml
		for line in self.viewDict['lines']:
			x1,y1,x2,y2,solid,selected = line
			vertexElem1 = doc.createElement("vertex")
			vertexElem1.setAttribute("x",str(x1))
			vertexElem1.setAttribute("y",str(y1))
			vertexElem2 = doc.createElement("vertex")
			vertexElem2.setAttribute("x",str(x2))
			vertexElem2.setAttribute("y",str(y2))
			edgeElem = doc.createElement("edge")
			edgeElem.appendChild(vertexElem1)
			edgeElem.appendChild(vertexElem2)
			if solid:
				edgeElem.setAttribute("type", "Solid")
			else:
				edgeElem.setAttribute("type", "Dashed")
			edgesElem.appendChild(edgeElem)
		#create the circles element
		circlesElem = doc.createElement("circles")
		viewElem.appendChild(circlesElem)
		#iterate over the edges and add them to the xml
		for circle in self.viewDict['circles']:
			x,y,radius,solid,selected = circle
			circleElem = doc.createElement("circle")
			circleElem.setAttribute("x",str(x))
			circleElem.setAttribute("y",str(y))
			circleElem.setAttribute("radius", str(radius))
			if solid:
				circleElem.setAttribute("type", "Solid")
			else:
				circleElem.setAttribute("type", "Dashed")
			circlesElem.appendChild(circleElem)
		
		return doc

