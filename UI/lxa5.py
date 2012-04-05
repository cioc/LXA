#THIS IS A REFRACTPORING WORK IN PROGRESS
#TODO RERACTOR INTO SIMPLE CLASSES WITH A PROCESSING FACTORY

import time
import datetime
import operator
import sys
import os
import codecs # for utf8
import string
import copy
from collections import defaultdict
from renderClasses import *
from PySide import QtCore

#THIS IS THE CLASS THAT USERS INTERACT WITH
#IT ALTERS INPUTS AND DISPLAYS OUTPUTS
#lxaJob CLASS ACTUALLY DOES THE PROCESSING JOB
class lxa5(render_base):
		def alter_diffType(self, v):
				self.DiffType = v
				if self.DiffType == "suffixal":
						self.FindSuffixesFlag = True
				else:		
						self.FindSuffixesFlag = False
						
		def alter_min_stem(self, v):
				self.MinimumStemLength = v
				
		def alter_max_affix(self, v):
				self.MaximumAffixLength = v
						
		def alter_encoding(self, v):
				self.g_encoding = v
				
		def alter_lang(self, v):
				self.language = v
		
		#important - must be implemented for render_base to works
		def gatherValues(self, k):
				if k == "Diff Type":
						return self.DiffType
				if k == "Encoding":
						return self.g_encoding
				if k == "Minimum Stem Length":
						return self.MinimumStemLength
				if k == "Maximum Affix Length":
						return self.MaximumAffixLength
				if k == "Path":
						return self.path
				if k == "Language":
						return self.language
		
		def display_name(self):
				return "Corpus "+self.dn
							
		def __init__(self, dn, path):
				super(lxa5, self).__init__()
				self.dn = dn
				self.path = path
				self.renderableKeys["Path"] = (False, ("STR",[]), None)
				
				self.DiffType = "suffixal"
				self.renderableKeys["Diff Type"] = (True, ("SELECT",["suffixal","prefixal"]), self.alter_diffType)
				
				self.FindSuffixesFlag = True
				self.g_encoding =  "utf8"
				self.renderableKeys["Encoding"] = (True, ("SELECT",["asci","utf8"]), self.alter_encoding)
				if self.FindSuffixesFlag:
						self.side = "suffixal"
				else:
						self.side = "prefixal"	
				self.MinimumStemLength = 5
				self.renderableKeys["Minimum Stem Length"] = (True, ("INT",[0,100]), self.alter_min_stem)
				self.MaximumAffixLength = 3
				self.renderableKeys["Maximum Affix Length"] = (True, ("INT",[0,100]), self.alter_max_affix)
				self.MinimumNumberofSigUses = 10
				self.language = "english"
				self.renderableKeys["Language"] = (True, ("STR",[]), self.alter_lang)
				#TODO need to add logic to create cache folder if it does not exist
				#TODO NEED TO FIGURE OUT PROBLEMS WITH THESE
				self.infolder = 'cache'
				self.size = 80
				self.smallfilename = "encarta"
				self.infilename = 'encarta_words.txt'
				self.outfolder = self.infolder
				self.outfilename = self.outfolder + self.language  +  "_" + str(self.size) + "Kwords_" + self.side + "_extendedsigs.txt"
				self.outfileSigTransformsname = self.outfolder + self.language + "_" + str(self.size) + "Kwords_" + self.side + "sigtransforms.txt" 
				self.outfileSigTransforms = open(self.outfileSigTransformsname, "w" )
				self.SigToTuple		= {}		
				self.Signatures 		= {}
				self.WordToSig		= {}
				self.StemToWord 		= {}
				self.StemCounts		= {}
				self.StemToSig 		= {}
				self.numberofwords 	= 0
				self.StemFileExistsFlag	= False
				
		def alterDiffType(self, v):
				 self.DiffType = str(v)
