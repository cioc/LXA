# decided to use pyside; http://www.pyside.org/
# it is a package of python binding for QT whose core developers are staffed by nokia 
# also, good documentation and tutorials
# and LGPL license!
# still deciding on wheather or not to use QtQuick - some issues on ubuntu 10.04 

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from UI.renderClasses import *
from UI.lxa5 import *
from UI.render_classes_specific import *
from UI.copora_right_click_menu import *
from Core.lxa_process import *

#globals
g_copora_list = []
g_corpus_selected = None
g_thread_list = []
			
class AboutDialog(QDialog):
		def __init__(self, parent=None):
				super(AboutDialog, self).__init__(parent)
				self.setGeometry(200,200,200,200)
				self.setWindowTitle('About lxa')
				
class DataWidget(QDockWidget):
		def __init__(self): 
				super(DataWidget, self).__init__()
				self.setFeatures(QDockWidget.DockWidgetMovable)
				self.setWindowTitle("Data View")
				self.dataView = render_table(self)
				self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
				self.dataView.setGeometry(10,25,self.size().width() - 10,self.size().height() - 10)
				self.dataView.insertColumn(0)
				self.dataView.insertColumn(1)
				self.dataView.setHorizontalHeaderLabels(["Item", "Value"])
				#TODO START HERE - FIX THIS IN THE MORNING
				#self.lxa = render_base()
				
				#self.dataView.render_obj(self.lxa)
		
		def render_obj(self, obj):
				self.dataView.render_obj(obj)
		
		def render_clear(self):
				self.dataView.render_clear()
				
		def resizeEvent(self, e):
				self.dataView.move(5,25)
				self.dataView.resize(e.size().width() - 10, e.size().height() - 10)
				self.dataView.resizeColumnsToContents()
				self.dataView.setColumnWidth(1, e.size().width() - 30 - self.dataView.columnWidth(0))
		
		def clearSize(self):
				self.dataView.move(5,25)
				self.dataView.resize(self.size().width() - 10, self.size().height() - 10)
				self.dataView.resizeColumnsToContents()
				self.dataView.setColumnWidth(1, self.size().width() - 30 - self.dataView.columnWidth(0))

class CorporaWidget(QDockWidget):
		def __init__(self, dataView):
				super(CorporaWidget, self).__init__()
				self.dataView = dataView
				self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
				self.setWindowTitle("Copora")
				self.coporaListView = QListWidget(self)
				#self.coporaListView.addItem("hello")
				self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
				self.setWidget(self.coporaListView)
				self.coporaListView.itemClicked.connect(self.itemClicked)
				self.setAcceptDrops(True)
				self.coporaListView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
				self.coporaListView.customContextMenuRequested.connect(self.right_click)
		def dragEnterEvent(self, e):
				if e.mimeData().hasFormat('text/plain'):
						e.accept()
				else:
						e.ignore()
						
		def dropEvent(self, e):
				#update this when we are figuring corpus loading
				pieces = e.mimeData().text().split(":")
				path = pieces[1].strip()[2:]
				self.loadCoporaFromFile(path)
				
		def loadCoporaFromFile(self, path):
				pieces = path.split("/")
				dn = pieces[len(pieces) - 1]
				nlxa = lxa5(dn,path)
				g_copora_list.append(nlxa)
				self.coporaListView.addItem(dn)
				self.coporaListView.currentItemChanged.connect(self.itemSelected)
		
		def right_click(self,pos):
				self.coporaListView.rmenu = corpus_right_menu(self.coporaListView.currentRow(), self)
				self.coporaListView.rmenu.exec_(self.coporaListView.mapToGlobal(QPoint(pos.x(),pos.y())))
		
		def remove_item(self, index):
				self.coporaListView.rmenu = None
				self.coporaListView.takeItem(index)
				global g_corpus_selected 
				g_corpus_selected = None
				global g_copora_list
				g_copora_list.pop(index)
				self.parent().dataWidget.render_clear()
				
	
		
		def itemClicked(self, item):
				index = self.coporaListView.indexFromItem(item).row()
				if index >= 0 and index < len(g_copora_list):
						global g_corpus_selected 
						g_corpus_selected = index
						self.dataView.render_obj(g_copora_list[index])
				
		def itemSelected(self, curr, prev):
				index = self.coporaListView.row(curr)
				if index >= 0 and index < len(g_copora_list):
						global g_corpus_selected 
						g_corpus_selected = index
						self.dataView.render_obj(g_copora_list[index])
		
				
				
				
class DataTabsWidget(QDockWidget):
		def __init__(self, dataView):
				super(DataTabsWidget, self).__init__()
				self.dataView = dataView
				self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
				self.setMinimumWidth(250)
				self.setWindowTitle("Data Items")
				self.dataTabs = QTabWidget(self)
				
				self.signatureListView = QListWidget(self.dataTabs)
				self.dataTabs.addTab(self.signatureListView, "Signatures")
				self.signatureListView.itemClicked.connect(self.signature_selected)
				
				self.wordListView = QListWidget(self.dataTabs)
				self.dataTabs.addTab(self.wordListView, "Words")
				self.wordListView.itemClicked.connect(self.word_selected)
				
				self.StemListView = QListWidget(self.dataTabs)
				self.dataTabs.addTab(self.StemListView, "Stems")
				self.StemListView.itemClicked.connect(self.stem_selected)
		
		def signature_selected(self, item):
				index = item.text()
				stems = g_copora_list[g_corpus_selected].Signatures[index]
				rs = render_signature(index, stems)
				self.dataView.render_obj(rs)
		
		def word_selected(self, item):
				index = item.text()
				
				stem = g_copora_list[g_corpus_selected].WordToSig[index]
				rs = render_word(index, stem)	
				self.dataView.render_obj(rs)
		
		def stem_selected(self, item):
				index = item.text()
				words = g_copora_list[g_corpus_selected].StemToWord[index]
				signature = g_copora_list[g_corpus_selected].StemToSig[index]
				count = g_copora_list[g_corpus_selected].StemCounts[index]
				rs = render_stem(index, words, signature, count)
				self.dataView.render_obj(rs)
								
				
		def display_signatures(self, signatures):
				ks = sorted(signatures.keys())
				for k in ks:
						self.signatureListView.addItem(k)
		
		def display_words(self, words):
				ks = sorted(words.keys())
				for k in ks:
						self.wordListView.addItem(k)
						
		def display_stems(self, stems):
				ks = sorted(stems.keys())
				for k in ks:
						self.StemListView.addItem(k)
				
		def resizeEvent(self, e):
				self.dataTabs.move(10,25)
				self.dataTabs.resize(e.size().width() - 5, e.size().height() - 10)	
				
class MainWindow(QMainWindow):
		def __init__(self, parent=None):
				super(MainWindow, self).__init__()
								
				self.buildMenu()		
				
				self.buildMainArea()
				
				self.settings = None
				self.load_settings()
				self.setWindowTitle('lxa')
				
		def load_settings(self):
				self.settings = QSettings("University of Chicago", "lxa")
				self.settings.beginGroup("MW")
				sv = self.settings.value("size", QSize(1024, 600))
				if (isinstance(sv, QSize)):
						self.resize(sv)
				else:
						self.resize(sv.toSize())
				pv = self.settings.value("pos", QPoint(0, 0))
				if (isinstance(pv, QPoint)):
						self.move(pv)
				else:
						self.move(pv.toPoint())
				self.settings.endGroup()
				self.settings.beginGroup("copora")
				
				copora_count = int(self.settings.value("count", 0))
				for i in range(0, copora_count):
						path = self.settings.value("copora_"+str(i), "")
						self.coporaWidget.loadCoporaFromFile(path)
				self.settings.endGroup()

		def save_settings(self):
				self.settings = QSettings("University of Chicago", "lxa")
				self.settings.beginGroup("MW")
				self.settings.setValue("size", self.size())
				self.settings.setValue("pos", self.pos())
				self.settings.endGroup()
				self.settings.beginGroup("copora")
				copora_count = len(g_copora_list)
				self.settings.setValue("count", copora_count)
				index = 0
				for c in g_copora_list:
						self.settings.setValue("copora_"+str(index), c.path)
						index += 1
				self.settings.endGroup()
				
		def closeEvent(self, e):
				self.save_settings()
				e.accept()
						
		def buildMenu(self):
				exitAct = QAction('&Quit',self)
				exitAct.setShortcut('Ctrl+Q')
				exitAct.setStatusTip('Quit')
				exitAct.triggered.connect(self.close)
				
				loadAct = QAction('&LoadCorpus',self)
				loadAct.setShortcut('Ctrl+O')
				loadAct.setStatusTip('Load Corpus')
				loadAct.setText("Load Corpus or Word Counts")
				loadAct.triggered.connect(self.loadCorpusDialog)
				
				appSettingsAct = QAction("&GSettings", self)
				appSettingsAct.setStatusTip("Settings")
				appSettingsAct.setText("Settings")
				
				exportAct = QAction("&Export", self)
				exportAct.setStatusTip("Export")
				exportAct.setText("Export (gexf)")
				
				aboutAct = QAction("&About", self)
				aboutAct.setStatusTip("About")
				aboutAct.setText("About")
				aboutAct.triggered.connect(self.showAbout)
					
				menubar = self.menuBar()
				fileMenu = menubar.addMenu('&File')
				fileMenu.addAction(loadAct)
				fileMenu.addAction(exportAct)
				fileMenu.addSeparator()
				fileMenu.addAction(appSettingsAct)
				fileMenu.addAction(aboutAct)
				fileMenu.addSeparator()
				fileMenu.addAction(exitAct)
				
				self.statusBar().showMessage("Ready")
				
				processAct = QAction("&Compute lxa", self)
				processAct.setStatusTip("Compute lxa")
				processAct.setText("Compute lxa")
				processAct.triggered.connect(self.computeLxa)
				
				showMenu = menubar.addMenu('&Process')
				showMenu.addAction(processAct)
		
		def buildMainArea(self):				
				self.dataWidget = DataWidget()
				self.setCentralWidget(self.dataWidget)
				
				self.coporaWidget = CorporaWidget(self.dataWidget)
				self.addDockWidget(Qt.RightDockWidgetArea,self.coporaWidget)
				
				self.dataTabsWidget = DataTabsWidget(self.dataWidget)
				self.addDockWidget(Qt.LeftDockWidgetArea, self.dataTabsWidget)
				
		def showMain(self):
				self.show()
				
		def computeLxa(self):
				self.noCorpusSelected()
				
		def noCorpusSelected(self):
				if g_corpus_selected is None:
						msgBox = QMessageBox()
						msgBox.setWindowTitle("No Corpus Selected")
						msgBox.setText("Please select a corpus to continue.")
						msgBox.exec_()
				else:
						self.progress = QProgressDialog("Performing LXA...", "cancel", 0, 11, self)
						self.progress.setWindowTitle("Performing LXA...")
						self.progress.forceShow()
						#progress.setWindowModality(Qt.WindowModal)
						job = lxaJob()
						global g_thread_list
						g_thread_list.append(job)
						
						job.progress_event.connect(self.handle_progress_event)
						job.end_event.connect(self.handle_end_event)
						
						c = g_copora_list[g_corpus_selected]
						#SHARE NOTHING
						job.copyData(c.path, c.DiffType, c.FindSuffixesFlag, c.g_encoding, c.side , c.MinimumStemLength, c.MaximumAffixLength, c.MinimumNumberofSigUses, c.language, c.infolder, c.size, c.smallfilename, c.infilename, c.outfolder, c.outfilename, c.outfileSigTransformsname, c.outfileSigTransforms, c.StemFileExistsFlag)
						
						job.start()
		
		@QtCore.Slot(str,int)
		def handle_progress_event(self, msg, val):
				self.progress.setLabelText(msg)
				self.progress.setValue(val)
		
		def handle_end_event(self):
				(SigToTuple, Signatures, WordToSig, StemToWord, StemCounts, StemToSig, numberofwords) = g_thread_list[-1].getOutput()
				#FORGET THAT THREAD
				#TODO MAKE SURE THIS ACTUALLY GETS GARBAGE COLLECTED OR DELETE IT MANUALLY
				g_thread_list.pop()
				#LOAD OUR DATA BACK IN FROM THE PROCESS
				g_copora_list[g_corpus_selected].SigToTuple = SigToTuple
				g_copora_list[g_corpus_selected].Signatures = Signatures
				g_copora_list[g_corpus_selected].WordToSig = WordToSig
				g_copora_list[g_corpus_selected].StemToWord = StemToWord
				g_copora_list[g_corpus_selected].StemCounts = StemCounts
				g_copora_list[g_corpus_selected].StemToSig = StemToSig
				g_copora_list[g_corpus_selected].numberofwords = numberofwords
				
				self.dataTabsWidget.display_signatures(g_copora_list[g_corpus_selected].Signatures)
				self.dataTabsWidget.display_words(g_copora_list[g_corpus_selected].WordToSig)
				self.dataTabsWidget.display_stems(g_copora_list[g_corpus_selected].StemToWord)
						
			
		def showAbout(self):
				ad = AboutDialog(self)
				ad.show()
				
		def loadCorpusDialog(self):
				path, t = QFileDialog.getOpenFileName(self, "Open Corpus or Word Counts", "", "Text files (*.txt);;XML files (*.xml)")
				if (not (path == "")):
						self.coporaWidget.loadCoporaFromFile(path)
				
				
if __name__ == '__main__':
		lxa = QApplication(sys.argv)
		mw = MainWindow()
		mw.showMain()
		sys.exit(lxa.exec_())

