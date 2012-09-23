import gtk
import pygtk
import cairo
import math
from xml.dom.minidom import Document
import xml.etree.ElementTree as ET
from view import *

class Draw:
	def __init__(self):
		#initialize variables
		#initialize mainWindow dimensions
		self.mainWindowWidth = 720
		self.mainWindowHeight = 640
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
		self.frontView.viewType = View.FrontView
		self.topView = View(View.TopView, self)
		self.topView.viewType = View.TopView
		self.sideView = View(View.SideView, self)
		self.sideView.viewType = View.SideView

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
		For each edge whose projection edge on each of the vthree faces - front, top and side is either 		contained within an edge on the view or is a vertex on the web, we mark as a 3d edge
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

		''' Process Circles. For each circle we look at the other views. If the other view has a box
		containing the circle - we add a cylinder to the 3d model. If the other view has a circle, 
		add a sphere to the model		
		'''
		self.cylinders3d = []
		self.spheres3d = []

		#iterate over each view and find all the circles

		frontViewCircles = self.frontView.viewDict['circles']
		for circle in frontViewCircles:
			#see if there is a matching box in the other views
			matchCircleFrontTop = matchCircleBox(circle, self.frontView, self.topView)
			for matchResult in matchCircleFrontTop:
				x1,y1,z1,x2,y2,z2,radius = matchResult
				#append cylinder
				self.cylinder3d.append(x1, y1, z1, x2, y2, z2, radius)
			
		return

	def match(self, circle, view1, view2):
		retVal = []
		if ((view1.viewType == View.FrontView) and (view2.viewType == View.TopView)):
			#circle is in front view and box to be matched in top view
			xc, yc, radius, solid, selected = circle
			xcminusr = xc - radius
			xvplusr = xc + radius
			edges1 = []
			#find edge1 => passes through xcminusr and perpendicular to x axis
			for line in view2.viewDict['lines']:
				x11, y11, x12, y12, solid, selected = line
				if (x11 == x12):
					#=>edge is perpendicular to x axis
					if (x11 == xcminusr):
						edges1.append(line)
			edges2 = []			
			#find edge2 => passes through xcplusr and perpendicular to x axis
			for line in view2.viewDict['lines']:
				x21, y21, x22, y22, solid, selected = line
				if (x21 == x22):
					#=>edge is perpendicular to x axis
					if (x21 == xcplusr):
						edges2.append(line)
			
			#find edge e3 perpendicular to edge1 and intersect between e1 and e2 is  2 * radius
			for line in view2.viewDict['lines']:
				x31, y31, x32,y32, solid, selected = line
				if (y31 == y32):
				 	#=>edge is pependicular to y axis
					#now if intersect between e1 and e2 is 2 * radius => valid edge3 
					for edge1 in edges1:
						for edge2 in edges2:
							x11, y11, x12, y12, solid, selected = edge1
							x21, y21, x22, y22, solid, selected = edge2
							#check if intersect point lies on edge3
							if self.point_on_line(x11,y31,x31,y31, x32,y32):
								if self.point_on_line(x21,y31, x31,y31, x32,y32):
									#=> edge3 is valid
									edges3.append((line, edge1, edge2))
			#now iterate over the edges and return a pair
			i = 0			
			for edge3 in edge3:
				j = 0
				for edge4 in edge3:	
					if not (i == j):
						edge33, edge31, edge32 = edge3
						edge43, edge41, edge42 = edge4
						#if edge31 = edge41 and edge32 = edge42 append a cylinder
						if (edge31 == edge41):
							if (edge32 == edge41):	
								x1, y1, z1 = xc, edge33[1], yc 
								x2, y2, z2 = xc, edge43[1], yc
								retVal.append((x1,y1,z1,x2,y2,z2,radius))				
						#if edge31 = edge42 and edge32 = edge41 append a cylinder
						if (edge31 == edge42):
							if (edge32 == edge41):	
								x1, y1, z1 = xc, edge33[1], yc 
								x2, y2, z2 = xc, edge43[1], yc
								retVal.append((x1,y1,z1,x2,y2,z2,radius))
						j = j + 1
					i = i + 1
			return retVal
								

	#test if point lies on segment by checking distances 
	def point_on_line(x, y, x1, y1, x2, y2):
		distance1 = self.distance_two_points(x,y, x1, y1)
		distance2 = self.distance_two_points(x,y,x2,y2)
		distance12 = self.distance_two_points(x1,y1,x2,y2)
		if ((distance1 + distance2) == distance12):
			return True
		return False

	#distance between a point a (x1, y1) and a point (x2,y)
	def distance_two_points(self, x1, y1, x2, y2):
		y2y1 = float(y2) - float(y1)
		x2x1 = float(x2) - float(x1)		
		distanceSquared = y2y1*y2y1 + x2x1*x2x1
		retVal = math.sqrt(distanceSquared)
		return retVal

	def matchCircleBox(circle, view):
		return (False, 0,0,0,0,0,0)
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
		#create the edges element
		cylindersElem = doc.createElement("cylinders")
		solidElem.appendChild(cylindersElem)
		for cylinder in self.cylinder3d:
			x1,y1,z1,x2,y2,z2, radius = cylinder
			cylinderElem = doc.createElement('cylinder')
			cylinderElem.setAttribute("x1",str(x1))
			cylinderElem.setAttribute("y1",str(y1))
			cylinderElem.setAttribute("z1",str(z1))
			cylinderElem.setAttribute("x2",str(x2))
			cylinderElem.setAttribute("y2",str(y2))
			cylinderElem.setAttribute("z2",str(z2))
			cylinderElem.setAttribute("radius",str(radius))
			cylindersElem.appendChild(cylinderElem)
		return doc
	def on_buttonZoomIn_clicked(self, widget):
		currView = self.notebookViews[self.mainNotebook.get_current_page()]		
		currZoomLevel = currView.zoomLevel
		if currZoomLevel < 5:
			currZoomLevel = currZoomLevel + 1
			self.notebookViews[self.mainNotebook.get_current_page()].zoomLevel = currZoomLevel
			currView.drawingArea.set_size_request(currView.drawingAreaWidth*currZoomLevel, currView.drawingAreaHeight*currZoomLevel)
			currView.drawingArea.queue_draw()
		return

	def on_buttonZoomOut_clicked(self, widget):		
		currView = self.notebookViews[self.mainNotebook.get_current_page()]		
		currZoomLevel = currView.zoomLevel
		if currZoomLevel > 1:
			currZoomLevel = currZoomLevel - 1
			self.notebookViews[self.mainNotebook.get_current_page()].zoomLevel = currZoomLevel
			currView.drawingArea.set_size_request(currView.drawingAreaWidth*currZoomLevel, currView.drawingAreaHeight*currZoomLevel)
			currView.drawingArea.queue_draw()
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
			(xc,yc,radius, solid, selected) = circle
			if selected:
				del(circles[i])
				i = i -1
			i = i + 1
		currView = self.notebookViews[self.mainNotebook.get_current_page()]
		currView.drawingArea.queue_draw()
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
			self.frontView.drawingArea.queue_draw()			
			topViewEdges = root.findall("./top_view/edges/edge")
			lines = self.topView.viewDict['lines']			
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
			self.topView.drawingArea.queue_draw()			
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
			self.sideView.drawingArea.queue_draw()	
		
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

			
