from PySide.QtCore import *
from PySide.QtGui import *

class render_base(QObject):

		def __init__(self):
				QObject.__init__(self)
				self.dn = "Test"
				self.renderableKeys = {}
				
		#this must be implemented for this class to work		
		#def gatherValues(self, k):
	
		def render(self, q_table):
				q_table.setRowCount(0)
				q_table.setRowCount(len(self.renderableKeys))
				rowCount = 0
				ks = sorted(self.renderableKeys.keys())
				for key in ks:
						valItem = None
						keyItem = QTableWidgetItem(str(key))
						keyItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
						q_table.setItem(rowCount, 0, keyItem)
						e, tp, f = self.renderableKeys[key]
						v = self.gatherValues(key)
						t, p = tp
						if t == "STR":
								valItem = QTableWidgetItem(str(v))
								q_table.setItem(rowCount, 1, valItem)
								if not (e):
										valItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
						if t == "INT":
								valItem = QSpinBox()
								valItem.setValue(v)
								valItem.setMinimum(p[0])
								valItem.setMaximum(p[1])
								nf = self.intClosure(f)
								valItem.valueChanged.connect(nf)
								q_table.setCellWidget(rowCount, 1, valItem)
						if t == "SELECT":
								valItem = QComboBox()
								for i in p:
										valItem.addItem(i)
								valItem.setCurrentIndex(p.index(v))
								nf = self.selectLookupClosure(p,f)
								valItem.currentIndexChanged.connect(nf)
								q_table.setCellWidget(rowCount, 1, valItem)
						if t == "BOOL":
								valItem = QComboBox()
								valItem.addItem("True")
								valItem.addItem("False")
								nf = self.boolClosure(f)
								valItem.currentIndexChanged.connect(nf)
								q_table.setCellWidget(rowCount, 1, valItem)
						rowCount += 1
				q_table.resizeColumnsToContents()
				q_table.parent().clearSize()
		
		def selectLookupClosure(self, p, f):
				def closed(x):
						return f(str(p[int(x)]))
				return closed
		
		def intClosure(self, f):
				def closed(x):
						return f(int(x))
				return closed
				
		def boolClosure(self, f):
				def closed(x):
						vs = ["True", "False"]
						v = vs[int(x)]
						return f(bool(v))
				return closed
						
		def display_name(self):
				return self.dn
						
		def alter(self, key, value):
				if (key in self.renderableKeys):
						e,t,f = self.renderableKeys[key]
						if value is not None and f is not None:
								f(str(value))
						
class render_table(QTableWidget):
		def __init__(self, parent=None):
				super(render_table, self).__init__(parent)
				self.focus_obj = None
				self.cellChanged.connect(self.cellChangedEvent)
		
		#object must be or inherit from render_base
		def render_obj(self, obj):
				self.focus_obj = obj
				self.render_clear()
				self.parent().setWindowTitle("Data View - " + obj.display_name())
				obj.render(self)
		
		def render_clear(self):
				for i in range(0, self.rowCount()):
						self.removeRow(1)
				self.clearContents()
				self.parent().setWindowTitle("Data View - Nothing right now.")
				
		
		def cellChangedEvent(self, row, col):
				it = self.item(row,col) 
				if (it.__class__.__name__ == "QTableWidgetItem") and (not(self.focus_obj == None)):
						if (not (self.item(row, col) is None)) and (not (self.item(row, col - 1) is None)):
								value = self.item(row, col).text()
								key = self.item(row, col - 1).text()
								self.focus_obj.alter(key, value)
