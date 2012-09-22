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
		self.drawingAreaWidth = 420
		self.drawingAreaHeight = 400
		self.tableWidth = 420
		self.tableHeight = 400
		self.zoomFactor = 5
		self.zoomLevel = 1
		self.viewDict = {}
		self.viewDict['lines'] = []
		self.viewDict['circles'] = []
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
		self.cairoContext = widget.window.cairo_create()
		self.draw_grid()
		for line in self.viewDict['lines']:
			(xGridClicked, yGridClicked, xGridReleased, yGridReleased,solid, selected) = line
			print "drawing real line from ", xGridClicked, ",", yGridClicked, " to " , xGridReleased, ",", yGridReleased 
			xGridClicked, yGridClicked = self.translate_real_to_gtk(xGridClicked, yGridClicked)
			xGridReleased, yGridReleased = self.translate_real_to_gtk(xGridReleased, yGridReleased)
			if solid:			
				print "drawing gtk solid line from ", xGridClicked, ",", yGridClicked, " to " , xGridReleased, ",", yGridReleased
				self.draw_line(xGridClicked, yGridClicked, xGridReleased, yGridReleased, selected, 1.0)
			else:
				self.draw_line_dashed(xGridClicked, yGridClicked, xGridReleased, yGridReleased,
 selected, 1.0)
				print "drawing gtk solid line from ", xGridClicked, ",", yGridClicked, " to " , xGridReleased, ",", yGridReleased
		for circle in self.viewDict['circles']:			
			(xGridClicked, yGridClicked, radius, selected) = circle
			xGridClicked, yGridClicked = self.translate_real_to_gtk(xGridClicked, yGridClicked)
			radius = self.translate_dimension_real_to_gtk(radius)
			self.draw_circle(xGridClicked, yGridClicked, radius, selected, 1.0)
		return
	

	def vertex_in_view(self, vertexIn):
		xIn, yIn = vertexIn
		for vertex in self.viewDict['vertices']:
			x,y = vertex
			if ((x == xIn) and (y == yIn)):
				return True
		return False
	def edge_in_view(self, edgeIn):
		x1In, y1In, x2In, y2In = edgeIn
		for edge in self.viewDict['lines']:
			x1, y1, x2, y2, type = edge
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
	def draw_circle(self,x, y, radius, selected, width):
		self.cairoContext.set_dash(())
		if selected:
			self.cairoContext.set_source_rgb(1,0,0)
		else:
			self.cairoContext.set_source_rgb(0,0,0)
		self.cairoContext.set_line_width(width)
		self.cairoContext.move_to(x, y)
		self.cairoContext.arc(x, y, radius, 0, 2*math.pi) 
		self.cairoContext.stroke()
		return	

	def draw_line(self,x1, y1, x2, y2, selected, width):
		self.cairoContext.set_dash(())
		if selected:
			self.cairoContext.set_source_rgb(1,0,0)
		else:
			self.cairoContext.set_source_rgb(0,0,0)
		
		
		self.cairoContext.move_to(x1, y1)
		self.cairoContext.line_to(x2, y2)
		self.cairoContext.set_line_width(width)		
		self.cairoContext.stroke()
		return

	def draw_line_dashed(self,x1, y1, x2, y2, selected, width):
		self.cairoContext.set_dash((5,3))
		if selected:
			self.cairoContext.set_source_rgb(1,0,0)
		else:
			self.cairoContext.set_source_rgb(0,0,0)
		self.cairoContext.set_line_width(width)
		self.cairoContext.move_to(x1, y1)
		self.cairoContext.line_to(x2, y2)
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
			self.draw_line(x1, y1, x2, y2, False, 0.1)
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
			self.draw_line(x1, y1, x2, y2, False, 0.1)
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
			print "translated grid clicked from ", self.xGridClicked, ",", self.yGridClicked, " to "
			self.xGridClicked, self.yGridClicked = self.translate_gtk_to_real(self.xGridClicked, self.yGridClicked)
			print self.xGridClicked, ",", self.yGridClicked

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
					print "line selected" 			
				i = i + 1
			
			for circle in circles:
				(xc,yc,circle,selected) = circle
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
				print "line selected "
				x1, y1, x2, y2, solid, selected = lines[lineMinIndex]
				if selected:
					lines[lineMinIndex] = (x1, y1, x2, y2, solid, False)
				else:
					lines[lineMinIndex] = (x1, y1, x2, y2, solid, True)
			
			elif circleSelected:
					xc, yc, radius, selected = circles[circleMinIndex]
					if selected:
						circles[circleMinIndex] = (xc, yc, radius, False)
					else:
						circles[circleMinIndex] = (xc, yc, radius, True)
			
			xDrawingAreaWidth, yDrawingAreaHeight = self.translate_real_to_gtk(self.drawingAreaWidth, self.drawingAreaHeight)
			self.drawingArea.draw(gtk.gdk.Rectangle(0,0,xDrawingAreaWidth, yDrawingAreaHeight))
		return
		
	def on_DrawingArea_button_released(self, widget, event):
		
    		#find the closest point on the grid
		xGrid = int(event.x)
		yGrid = int(event.y)
		self.xGridReleased = xGrid
		self.yGridReleased = yGrid
		print "translated grid released from ", self.xGridReleased, ",", self.yGridReleased, " to "
		self.xGridReleased, self.yGridReleased = self.translate_gtk_to_real(self.xGridReleased, self.yGridReleased)
		print self.xGridReleased, ",", self.yGridReleased
		lines = self.viewDict['lines']
		circles = self.viewDict['circles']
		print self.drawObject.solidMode
		print self.drawObject.drawMode
		#store line segments as end points and selected flag		
		if self.drawObject.solidMode == self.drawObject.solid :
			if self.drawObject.drawMode == self.drawObject.lineMode :
				"appending solid line"
				lines.append((self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased, True, False))
			elif self.drawObject.drawMode == self.drawObject.circleMode:
				radius = self.distance_two_points(self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased)
				circles.append((self.xGridClicked, self.yGridClicked, radius, True, False))	
		elif self.drawObject.solidMode == self.drawObject.dashed:
			if self.drawObject.drawMode == self.drawObject.lineMode :
				lines.append((self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased, False, False))
			elif self.drawObject.drawMode == self.drawObject.circleMode:
				radius = self.distance_two_points(self.xGridClicked, self.yGridClicked, self.xGridReleased, self.yGridReleased)
				circles.append((self.xGridClicked, self.yGridClicked, radius, False, False))
		self.compute_vertices()	
		
		self.drawingArea.draw(gtk.gdk.Rectangle(0,0,400,420))
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
		return doc

class Draw:
	def __init__(self):
		#initialize variables
		#initialize mainWindow dimensions
		self.mainWindowWidth = 960
		self.mainWindowHeight = 720
		#initialize draw modes
		self.modeNotSelected = 0		
		self.lineMode = 1
		self.rectangleMode = 2
		self.circleMode = 3		
		self.splineMode = 4		
		self.selectMode = 5
		self.deleteMode = 6
		self.drawMode = self.modeNotSelected
		#initialize solid modes		
		self.solid = 0
		self.dashed = 1
		self.solidMode = self.solid		
		self.notebookViews = []
	
		self.mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.mainWindow.set_title("Draw")
		#define main vBox
		self.mainVBox = gtk.VBox()
		#create menu itemsy
		self.fileMenu = gtk.MenuItem("File")
		self.fileSubMenu = gtk.Menu()

		#create menu sub items
		#create a buffer
		buf = "Open" 
		# Create a new menu-item with a name...
		self.menuitemOpen = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.fileSubMenu.append(self.menuitemOpen)
		# Connect signals
		self.menuitemOpen.connect("activate", self.on_menuitem_open_activated)
		#create a buffer
		buf = "Save" 
		# Create a new menu-item with a name...
		self.menuitemSave = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.fileSubMenu.append(self.menuitemSave)
		# Connect signal
		self.menuitemSave.connect("activate", self.on_menuitem_save_activated)
		#create a buffer
		buf = "Save As"
		# Create a new menu-item with a name...
		self.menuitemSaveAs = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.fileSubMenu.append(self.menuitemSaveAs)
		# Connect signals
		self.menuitemSaveAs.connect("activate", self.on_menuitem_saveas_activated)		
		#create a buffer
		buf = "Scan"
		# Create a new menu-item with a name...
		self.menuitemScan = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.fileSubMenu.append(self.menuitemScan)
		# Connect signals
		self.menuitemScan.connect("activate", self.on_menuitem_scan_activated)
		#create a buffer
		buf = "Quit" 
		# Create a new menu-item with a name...
		self.menuitemQuit = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.fileSubMenu.append(self.menuitemQuit)
		# Connect signals
		self.menuitemQuit.connect("activate", self.on_menuitem_quit_activated)
		#set menu hierarchy for menu and submenu
		self.fileMenu.set_submenu(self.fileSubMenu)
		#make the menu bar
		self.menuBar = gtk.MenuBar()            
		#append menu items to menu bar and add to main v box		
		self.menuBar.append(self.fileMenu)
		self.mainVBox.pack_start(self.menuBar, False, False, 2)
				

		#create menu items
		self.editMenu = gtk.MenuItem("Edit")
		self.editSubMenu = gtk.Menu()

		#create menu sub items
		#create a buffer
		buf = "Select" 
		# Create a new menu-item with a name...
		self.menuitemSelect = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.editSubMenu.append(self.menuitemSelect)
		# Connect signals
		self.menuitemSelect.connect("activate", self.on_menuitem_select_activated)
		#create a buffer
		buf = "Delete" 
		# Create a new menu-item with a name...
		self.menuitemDelete = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.editSubMenu.append(self.menuitemDelete)
		# Connect signals
		self.menuitemDelete.connect("activate", self.on_menuitem_delete_activated)
		
		#set menu hierarchy for menu and submenu
		self.editMenu.set_submenu(self.editSubMenu)
		#append menu items to menu bar and add to main v box		
		self.menuBar.append(self.editMenu)


		#create menu items
		self.inferMenu = gtk.MenuItem("Infer")
		self.inferSubMenu = gtk.Menu()

		#create menu sub items
		#create a buffer
		buf = "Model" 
		# Create a new menu-item with a name...
		self.menuitemInferModel = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.inferSubMenu.append(self.menuitemInferModel)
		# Connect signals
		self.menuitemInferModel.connect("activate", self.on_menuitem_infer_model_activated)
		
		#create a buffer
		buf = "Save As" 
		# Create a new menu-item with a name...
		self.menuitemInferSaveAs = gtk.MenuItem(buf)
		# ...and add it to the menu.
		self.inferSubMenu.append(self.menuitemInferSaveAs)
		# Connect signals
		self.menuitemInferSaveAs.connect("activate", self.on_menuitem_infer_saveas_activated)
		
		#set menu hierarchy for menu and submenu
		self.inferMenu.set_submenu(self.inferSubMenu)
		#append menu items to menu bar and add to main v box		
		self.menuBar.append(self.inferMenu)
		
		#init notebook for display of views
		self.mainNotebook = gtk.Notebook()
		self.mainNotebook.set_tab_pos(gtk.POS_TOP)		
		self.mainNotebook.set_show_tabs(True)
		self.mainNotebook.set_current_page(1)
		#add main notewbook to main vbox				
		self.mainVBox.add(self.mainNotebook)
		#add main vbox to main window
		self.mainWindow.add(self.mainVBox)		
		#init buttons
		self.buttonHBox = gtk.HBox()
		self.buttonZoomIn = gtk.Button()
		self.buttonZoomIn.set_label("ZoomIn")
		self.buttonZoomOut = gtk.Button()
		self.buttonZoomOut.set_label("ZoomOut")
		self.buttonSolid = gtk.Button()
		self.buttonSolid.set_label("Dashed")		
		self.buttonLine = gtk.Button()
		self.buttonLine.set_label("Line")
		
		self.buttonRectangle = gtk.Button()
		self.buttonRectangle.set_label("Rectangle")
		self.buttonCircle = gtk.Button()
		self.buttonCircle.set_label("Circle")
		self.buttonSpline = gtk.Button()
		self.buttonSpline.set_label("Spline")

		self.buttonSelect = gtk.Button()
		self.buttonSelect.set_label("Select")
		self.buttonDelete = gtk.Button()
		self.buttonDelete.set_label("Delete")
		#add buttons to hbox
		self.buttonHBox.pack_start(self.buttonZoomIn, False, False)
		self.buttonHBox.pack_start(self.buttonZoomOut, False, False)
		self.buttonHBox.pack_start(self.buttonSolid, False, False)
		self.buttonHBox.pack_start(self.buttonLine, False, False)
		self.buttonHBox.pack_start(self.buttonRectangle, False, False)	
		self.buttonHBox.pack_start(self.buttonCircle, False, False)	
		self.buttonHBox.pack_start(self.buttonSpline, False, False)				
		self.buttonHBox.pack_start(self.buttonSelect, False, False)
		self.buttonHBox.pack_start(self.buttonDelete, False, False)		
		#add buttons hbxo to vbox
		self.mainVBox.pack_start(self.buttonHBox, False, False)
		
				
		#initialize view objects 
		self.frontView = View(View.FrontView, self)
		self.topView = View(View.TopView, self)
		self.sideView = View(View.SideView, self)

		#add view objects to notebook		
		self.frontView.add_to_notebook(self.mainNotebook)
		self.notebookViews.append(self.frontView)		
		self.topView.add_to_notebook(self.mainNotebook)
		self.notebookViews.append(self.topView)
		self.sideView.add_to_notebook(self.mainNotebook)
		self.notebookViews.append(self.sideView)
		
		
		#set size of the widgets
		self.mainWindow.set_size_request(self.mainWindowWidth, self.mainWindowHeight)
		#connect the signals
		
		self.mainWindow.connect("destroy", lambda w: gtk.main_quit())
		self.buttonZoomIn.connect("clicked", self.on_buttonZoomIn_clicked)
		self.buttonZoomOut.connect("clicked", self.on_buttonZoomOut_clicked)
		self.buttonSolid.connect("clicked", self.on_buttonSolid_clicked)
		self.buttonLine.connect("clicked", self.on_buttonLine_clicked)
		self.buttonRectangle.connect("clicked", self.on_buttonRectangle_clicked)
		self.buttonCircle.connect("clicked", self.on_buttonCircle_clicked)
		self.buttonSpline.connect("clicked", self.on_buttonSpline_clicked)
		self.buttonSelect.connect("clicked", self.on_buttonSelect_clicked)
		self.buttonDelete.connect("clicked", self.on_buttonDelete_clicked)
		self.mainWindow.connect("key-press-event", self.on_keypress)
		#finally show the widgets
		self.mainVBox.show()
		self.menuitemOpen.show()
		self.menuitemSave.show()
		self.menuitemSaveAs.show()
		self.menuitemScan.show()
		self.menuitemQuit.show()
		self.fileMenu.show()
		self.fileSubMenu.show()
		self.menuitemSelect.show()
		self.menuitemDelete.show()
		self.editMenu.show()
		self.editSubMenu.show()
		self.menuitemInferModel.show()
		self.menuitemInferSaveAs.show()
		self.inferMenu.show()
		self.inferSubMenu.show()

		self.menuBar.show()
		self.mainNotebook.show()
		self.buttonHBox.show()
		self.buttonZoomIn.show()
		self.buttonZoomOut.show()
		self.buttonSolid.show()
		self.buttonLine.show()
		self.buttonRectangle.show()
		self.buttonCircle.show()
		self.buttonSpline.show()
		self.buttonSelect.show()
		self.buttonDelete.show()
		self.frontView.show()
		self.topView.show()
		self.sideView.show()		
		self.mainWindow.show()


		return
	def infer_3d_model(self):
		#We look at the front view vertices and the side view vertices and for each vertex whose x axis values match we add a 3d vertex
		self.vertices3d = []
		frontViewVertices = self.frontView.viewDict['vertices']
		topViewVertices = self.topView.viewDict['vertices']
		vertices3d_dict = {}
		for vertex_front in frontViewVertices:
			x_front, z_front =  vertex_front
			for vertex_top in topViewVertices:
				x_top, y_top = vertex_top
				if x_front == x_top:
					vertex3d = (x_front, y_top, z_front)
					if not (vertex3d in vertices3d_dict):
						self.vertices3d.append(vertex3d)
						vertices3d_dict[vertex3d] = vertex3d
		'''
		We look at a sorted view of all possible edges from the 3d vertices Vi, vj
		For each edge whose projection edge on each of the vthree faces - front, top and side is either contained within			
		an edge on the view or is a vertex on the web, we mark as a 3d edge
		''' 
		self.edges3d=[]
		numVertices3d = len(self.vertices3d)
		i = 0
		j = 0
		for i in range(0, numVertices3d):
			for j in range(i+1, numVertices3d):
				xi,yi,zi = self.vertices3d[i]
				xj, yj, zj = self.vertices3d[j]
				currEdge = (xi,yi,zi,xj,yj,zj)
				if self.valid_edge_3d(currEdge):
					self.edges3d.append(currEdge)

		return
	
		return False
	def valid_edge_3d(self, edge):
		x1,y1,z1,x2,y2,z2 = edge		
		#Evaluate the front view projection of the edge
		#Case 1, x1 = x2 and z1 = z2 => projection is a point x1,z1
		if ((x1 == x2) and (z1 == z2)):
			vertexProjected = (x1,z1)
			if not (self.frontView.vertex_in_view(vertexProjected)):
				return False
		else:
			#=>projection is an edge
			edgeProjected = (x1, z1, x2, z2)
			if not(self.frontView.edge_in_view(edgeProjected)):
				return False
		#Evaluate the top view projection of the edge
		#Case 1, x1 = x2 and y1 = y2 => projection is a point x1,y1
		if ((x1 == x2) and (y1 == y2)):
			vertexProjected = (x1,y1)
			if not (self.topView.vertex_in_view(vertexProjected)):
				return False
		else:
			#=>projection is an edge
			edgeProjected = (x1, y1, x2, y2)
			if not(self.topView.edge_in_view(edgeProjected)):
				return False
		#Evaluate the side view projection of the edge
		#Case 1, y1 = y2 and z1 = z2 => projection is a point y1,z1
		if ((y1 == y2) and (z1 == z2)):
			vertexProjected = (y1,z1)				
			if not (self.sideView.vertex_in_view(vertexProjected)):				
				return False
		else:
			#=>projection is an edge
			edgeProjected = (y1, z1, y2, z2)
			if not(self.sideView.edge_in_view(edgeProjected)):
				return False
		return True
	
	def print_xml_3d_model(self):
		#create the root element
		doc = Document()
		solidElem = doc.createElement("solid")		
		doc.appendChild(solidElem)
		#create the vertices element
		verticesElem = doc.createElement("vertices")
		solidElem.appendChild(verticesElem)
		#iterate over vertices and add them to the xml
		for vertex in self.vertices3d:
			x,y,z = vertex
			vertexElem = doc.createElement("vertex")
			vertexElem.setAttribute("x",str(x))
			vertexElem.setAttribute("y",str(y))
			vertexElem.setAttribute("z",str(z))
			verticesElem.appendChild(vertexElem)
		#create the edges element
		edgesElem = doc.createElement("edges")
		solidElem.appendChild(edgesElem)
		#iterate over edges and add them to the xml
		for edge in self.edges3d:
			x1,y1,z1,x2,y2,z2 = edge
			edgeElem = doc.createElement('edge')
			edgeElem.setAttribute("x1",str(x1))
			edgeElem.setAttribute("y1",str(y1))
			edgeElem.setAttribute("z1",str(z1))
			edgeElem.setAttribute("x2",str(x2))
			edgeElem.setAttribute("y2",str(y2))
			edgeElem.setAttribute("z2",str(z2))
			edgesElem.appendChild(edgeElem)
		return doc
	def on_buttonZoomIn_clicked(self, widget):
		currView = self.notebookViews[self.mainNotebook.get_current_page()]		
		currZoomLevel = currView.zoomLevel
		if currZoomLevel < 5:
			currZoomLevel = currZoomLevel + 1
			self.notebookViews[self.mainNotebook.get_current_page()].zoomLevel = currZoomLevel
			currView.drawingArea.set_size_request(currView.drawingAreaWidth*currZoomLevel, currView.drawingAreaHeight*currZoomLevel)
			currView.drawingArea.draw(gtk.gdk.Rectangle(0,0,420,400))
		return

	def on_buttonZoomOut_clicked(self, widget):		
		currView = self.notebookViews[self.mainNotebook.get_current_page()]		
		currZoomLevel = currView.zoomLevel
		if currZoomLevel > 1:
			currZoomLevel = currZoomLevel - 1
			self.notebookViews[self.mainNotebook.get_current_page()].zoomLevel = currZoomLevel
			currView.drawingArea.set_size_request(currView.drawingAreaWidth*currZoomLevel, currView.drawingAreaHeight*currZoomLevel)
			currView.drawingArea.draw(gtk.gdk.Rectangle(0,0,420,400))
		return


	def on_buttonSolid_clicked(self, widget):
		if self.solidMode == self.solid:		
			self.solidMode = self.dashed
			self.buttonSolid.set_label("Solid")
		else:
			self.solidMode = self.solid
			self.buttonSolid.set_label("Dashed")
		return
	def on_buttonLine_clicked(self, widget):
		self.drawMode = self.lineMode
		return
	def on_buttonRectangle_clicked(self, widget):
		self.drawMode = self.rectangleMode
		return

	def on_buttonCircle_clicked(self, widget):
		self.drawMode = self.circleMode
		return

	def on_buttonSpline_clicked(self, widget):	
		self.drawMode = self.splineMode
		return

	def on_buttonSelect_clicked(self, widget):
		self.drawMode = self.selectMode 
		return

	def on_buttonDelete_clicked(self, widget):
		self.drawMode = self.deleteMode
		self.handle_delete()

	def handle_delete(self):
		self.currView = self.notebookViews[self.mainNotebook.get_current_page()]
		#get the current active view
		#iterate over the lines and delete the selected lines
		lines = self.currView.viewDict['lines']
		circles = self.currView.viewDict['circles']
		i = 0
		for line in lines:
			(x1,y1,x2,y2, solid, selected) = line
			if selected:
				del(lines[i])
				i = i -1
			i = i + 1
		
		for circle in circles:
			(xc,yc,radius, selected) = circle
			if selected:
				del(circles[i])
				i = i -1
			i = i + 1
		currView = self.notebookViews[self.mainNotebook.get_current_page()]
		currView.drawingArea.draw(gtk.gdk.Rectangle(0,0,400,420))
		currView.compute_vertices()		
		return
	
	# Print a string when a menu item is selected
	def on_menuitem_open_activated(self, widget):
		self.saveAsFile = ""
		dialog = gtk.FileChooserDialog("Open", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.openFile = dialog.get_filename()
		elif response == gtk.RESPONSE_CANCEL:
			self.openFile = ""
		dialog.destroy()
		if not (self.openFile == ""):
			#clear the views data
			self.frontView.viewDict = {}
			self.topView.viewDict = {}
			self.sideView.viewDict = {}
			self.frontView.viewDict['lines'] = []
			self.frontView.viewDict['circles'] = []
			self.topView.viewDict['lines'] = []
			self.topView.viewDict['circles'] = []
			self.sideView.viewDict['lines'] = []
			self.sideView.viewDict['circles'] = []
			#parse the file
			tree = ET.parse(self.openFile)
			root = tree.getroot()
			#handle all the views	
			frontViewEdges = root.findall("./front_view/edges/edge")
			lines = self.frontView.viewDict['lines']
			for edge in frontViewEdges:
				#Extract edge type and cordinates of end points 
				type = edge.attrib['type']
				vertices = edge.findall("./vertex")
				vertex1 = vertices[0]
				vertex2 = vertices[1]
				x1 = int(vertex1.attrib['x'])
				y1 = int(vertex1.attrib['y'])
				x2 = int(vertex2.attrib['x'])
				y2 = int(vertex2.attrib['y'])
				if (type == "Solid"):
					lines.append((x1,y1,x2,y2,True,False))
				elif (type == "Dashed"):
					dashedLines.append((x1,y1,x2,y2,True,False))
			self.frontView.compute_vertices()	
			self.frontView.drawingArea.draw(gtk.gdk.Rectangle(0,0,400,420))				
			topViewEdges = root.findall("./top_view/edges/edge")
			lines = self.topView.viewDict['Lines']			
			for edge in topViewEdges:
				#Extract edge type and cordinates of end points 
				type = edge.attrib['type']
				vertices = edge.findall("./vertex")
				vertex1 = vertices[0]
				vertex2 = vertices[1]
				x1 = int(vertex1.attrib['x'])
				y1 = int(vertex1.attrib['y'])
				x2 = int(vertex2.attrib['x'])
				y2 = int(vertex2.attrib['y'])
				if (type == "Solid"):
					lines.append((x1,y1,x2,y2,True, False))
				elif (type == "Dashed"):
					dashedLines.append((x1,y1,x2,y2,False, False))
			self.topView.compute_vertices()	
			self.topView.drawingArea.draw(gtk.gdk.Rectangle(0,0,400,420))				
			sideViewEdges = root.findall("./side_view/edges/edge")
			lines = self.sideView.viewDict['lines']		
			for edge in sideViewEdges:
				#Extract edge type and cordinates of end points 
				type = edge.attrib['type']
				vertices = edge.findall("./vertex")
				vertex1 = vertices[0]
				vertex2 = vertices[1]
				x1 = int(vertex1.attrib['x'])
				y1 = int(vertex1.attrib['y'])
				x2 = int(vertex2.attrib['x'])
				y2 = int(vertex2.attrib['y'])
				if (type == "Solid"):
					lines.append((x1,y1,x2,y2,True,False))
				elif (type == "Dashed"):
					lines.append((x1,y1,x2,y2,True,False))
			self.sideView.compute_vertices()	
			self.sideView.drawingArea.draw(gtk.gdk.Rectangle(0,0,400,420))		
		
		return


	def on_menuitem_save_activated(self, widget):
		return
	def on_menuitem_saveas_activated(self,widget):
		self.saveAsFile = ""
		dialog = gtk.FileChooserDialog("Save Project", None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.saveAsFile = dialog.get_filename()
		elif response == gtk.RESPONSE_CANCEL:
			self.saveAsFile = ""
		dialog.destroy()
		if not (self.saveAsFile == ""):
			#get the xml of each view
			front_view_xml_doc = self.frontView.print_xml()
			top_view_xml_doc = self.topView.print_xml()
			side_view_xml_doc = self.sideView.print_xml()
			f = open(self.saveAsFile, 'w')
			xml_doc_out = Document()
			viewsElem = xml_doc_out.createElement("views")
			xml_doc_out.appendChild(viewsElem)
			ele = front_view_xml_doc.documentElement;			
			if not (ele == None):
				copyNode = xml_doc_out.importNode(ele, True);
				xml_doc_out.documentElement.appendChild(copyNode);
			ele = top_view_xml_doc.documentElement;			
			if not (ele == None):
				copyNode = xml_doc_out.importNode(ele, True);
				xml_doc_out.documentElement.appendChild(copyNode);

			ele = side_view_xml_doc.documentElement;	
			if not (ele == None):
				copyNode = xml_doc_out.importNode(ele, True);
				xml_doc_out.documentElement.appendChild(copyNode);
			xml_doc_out.writexml(f, encoding='utf-8', indent='	', newl='\n')
			f.close()
		return
	
	def on_menuitem_infer_model_activated(self, widget):
		self.infer_3d_model()
		return
	def on_menuitem_infer_saveas_activated(self, widget):
		self.saveAsFileModel = ""		
		dialog = gtk.FileChooserDialog("Save Model", None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.saveAsFileModel = dialog.get_filename()
		elif response == gtk.RESPONSE_CANCEL:
			self.saveAsFileModel = ""
		dialog.destroy()
		if not (self.saveAsFileModel == ""):
			#get the xml of each view
			model_xml_doc = self.print_xml_3d_model()
			f = open(self.saveAsFileModel, 'w')
			model_xml_doc.writexml(f, encoding='utf-8', indent='	', newl='\n')
			f.close()
		return
	def on_keypress(self, widget, event):
		if (event.keyval == gtk.keysyms.Delete):  
			self.handle_delete()		
		return
	def on_menuitem_scan_activated(self, widget):
		return
	def on_menuitem_quit_activated(self, widget):
		return
	def on_menuitem_select_activated(self, widget):
		return
	def on_menuitem_delete_activated(self, widget):
		return
	def main(self):
		gtk.main()
if __name__ == "__main__":
	draw =  Draw()
	draw.main()

			
