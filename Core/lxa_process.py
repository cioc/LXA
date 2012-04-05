#THIS CONTAINS THE TRHEAD FOR LXA

import time
import datetime
import operator
import sys
import os
import codecs # for utf8
import string
import copy
from collections import defaultdict
from lxa_module import * 
from PySide import QtCore
from PySide.QtCore import *
from PySide.QtGui import *

class lxaJob(QtCore.QThread):
		#THESE EVENTS ARE NECESSARY FOR ALERTING THE FRONT END AS PROCESSING IS DONE
		progress_event = Signal(str, int)
		end_event = Signal()

		def __init__(self):
				QThread.__init__(self)
				#THESE WILL BE PASSSED IN WHEN EVERYTHING IS RUN IN ORDER TO SEPARATE OUR FRONT AND BACKEND
				self.path = ""
				self.DiffType = ""
				self.FindSuffixesFlag = True
				self.g_encoding = ""
				self.side = ""
				self.MinimumStemLength = 0
				self.MaximumAffixLength = 0
				self.MinimumNumberofSigUses = 0
				self.language = ""
				self.infolder = ""
				self.size = 0
				self.smallfilename = ""
				self.infilename = ""
				self.outfolder = ""
				self.outfilename = ""
				self.outfileSigTransformsname = ""
				self.outfileSigTransforms = ""
				self.StemFileExistsFlag	= False
				
				#OUTPUT VALUES
				self.SigToTuple		= {}		
				self.Signatures 		= {}
				self.WordToSig		= {}
				self.StemToWord 		= {}
				self.StemCounts		= {}
				self.StemToSig 		= {}
				self.numberofwords 	= 0
		
		def getOutput(self):
				return (self.SigToTuple,	self.Signatures, self.WordToSig, self.StemToWord, self.StemCounts, self.StemToSig, 	self.numberofwords)	
				
		def loadOrCreateStemFiles(self):
				stemfilename = self.infolder + self.language + "_" + str(self.size) + "Kwords_" + self.side + "_stems" + ".txt"
				if os.path.isfile(stemfilename):
						#TODO REPLACE THESE WITH SIGNALS
						print "stem file is named: ", stemfilename
						print "stem file found"
						self.StemFileExistsFlag = True
						stemfile=open(stemfilename)
						filelines = stemfile.readlines()
						for line in filelines:		
								pieces=line.split()
								stem = pieces[0]			 
								self.StemCounts[stem] = 1 #  pieces[1]	
								self.StemToWord[stem] = set()
								for i in range (2, len(pieces)):
									word = pieces[i]
									self.StemToWord[stem].add(word)		
				else:
						#TODO REPLACE WITH SIGNAL
						print "stem file not found"
						self.SigToTuple = MakeBiSignatures(self.wordlist, self.SigToTuple, self.FindSuffixesFlag)
						for sig in self.SigToTuple.keys():
								if len( self.SigToTuple[sig] ) < self.MinimumNumberofSigUses:		 
										del self.SigToTuple[sig]
								else:
										for stem, word1, word2, bisigstring in self.SigToTuple[sig]:				
												if not stem in self.StemToWord:
														self.StemToWord[stem] = set()
														self.StemToWord[stem].add(word1)
														self.StemToWord[stem].add(word2)		 
						#TODO REPLACE WITH SIGNAL
						print "Completed filtering out pairs used only a few times."
				for stem in self.StemToWord:
						self.StemCounts[stem] = 0
						for word in self.StemToWord[stem]:
								self.StemCounts[stem] += self.WordCounts[word]

				if (not self.StemFileExistsFlag): # we use this to create a one-time list of stems with their words
						if self.g_encoding == "utf8":
								outfile2 = codecs.open(stemfilename,encoding="utf-8",mode="w")
						else:
								outfile2 = open (stemfilename,"w")

						for stem in self.StemToWord.keys():			 
								print >>outfile2, stem,	self.StemCounts[stem],	 
								for word in self.StemToWord[stem]:
										print >>outfile2, word,
								print >>outfile2
						outfile2.close()
		
		#STEP 2
		def compareToCollapseSignatures(self):
				StemCountThreshold = 15
				outputtemplate = "%25s  %25s  %5d %35s %35s"
				SigPairList = []
				MaxNumberOfSimilarSignatures = 3
				print "2a. Calculating signature differences"
				print >>self.outfile, "\n\n*** 2a. Signature differences \n"
				for m in range (len(self.Signatures)-1):
						sig1= self.Signatures.keys()[m]
						if len( self.Signatures[sig1] ) < StemCountThreshold:
								continue
						ListOfSigComparisons = []
						for n in range (m, len(self.Signatures) - 1 ):			
								sig2 = self.Signatures.keys()[n]
								if len( self.Signatures[sig2] ) < StemCountThreshold:
										continue
								siglist1 = sig1.split('-')
								siglist2 = sig2.split('-')
								if not len(siglist1) == len(siglist2): 
										continue
								if sig1 == sig2:
										continue		 
								(diff, alignedlist1, alignedlist2)  = SignatureDifference( sig1, sig2, self.outfile )
								if diff > 0 :
										ListOfSigComparisons.append((diff, sig1,sig2, alignedlist1, alignedlist2))
						ListOfSigComparisons.sort(key = lambda stuff: stuff[0], reverse= True)
						for i in range(len(ListOfSigComparisons)):
								if i == MaxNumberOfSimilarSignatures:
										break
								(diff, sig1,sig2, alignedlist1, alignedlist2) = ListOfSigComparisons[i]
								#print >>outfile, outputtemplate %(sig1, sig2, diff, alignedlist1, alignedlist2)
								SigPairList.append((sig1, sig2, diff, alignedlist1, alignedlist2))
	
				SigPairList.sort(   key = lambda quintuple: quintuple[2] , reverse = True)
				for quintuple in SigPairList:
						print >>self.outfile, "---------------------------------------------------------------------------------------------" 
						print >>self.outfile, outputtemplate %(  quintuple[0], quintuple[1], quintuple[2],quintuple[3], quintuple[4] )
						basictableau1=intrasignaturetable()
						#print >>outfile, quintuple[3], listToSignature(quintuple[3])
						basictableau1.setsignature(listToSignature( quintuple[3]) )
						basictableau1.displaytofile (self.outfile)
						basictableau2=intrasignaturetable()
						basictableau2.setsignature( listToSignature(quintuple[4]) ) 
						basictableau2.displaytofile (self.outfile)
						basictableau1.minus_aligned(basictableau2, self.DiffType)
						print >>self.outfile, basictableau1.displaytolist_aligned(self.outfile)	
		
		#step 3a
		def findLargerGroupsOfSignatures(self):		
				print >>self.outfile, "\n\n  *** 3a. Find larger groupings of signatures \n\n"
				print "3a. Find larger groupings of signatures"
				self.SortedListOfSignatures = sorted( Signatures.items(), lambda x,y: cmp(len(x[1]), len(y[1]) ) , reverse=True)
				self.SortedList = []
				for sig  in Signatures.keys():	
						self.SortedList.append((sig,getrobustness(sig,Signatures[sig])))
				self.SortedList = sorted( SortedList, lambda x,y: cmp(x[1], y[1] ) , reverse=True)
			 
				self.RemainingSignatures = Signatures
				self.Subsignatures = {}
				self.Satellites = {}
				topsetcount = 10
				for n in range (topsetcount):
						topsig = self.SortedList[n][0]
						topsigset = set (topsig.split('-'))
						for m in range(n+1,  len(self.SortedList) ):
								lowsig = self.SortedList[m][0]
								#print topsig, lowsig
								if not lowsig in self.RemainingSignatures:
										continue
								if subsignature(lowsig,topsig):
										if not topsig in self.Subsignatures:
												self.Subsignatures[topsig] = []
										self.Subsignatures[topsig].append(lowsig)
						if topsig in self.Subsignatures:
								print >>self.outfile, "\nSubsignatures", topsig, self.Subsignatures[topsig]
	
					#TODO add control for this
						if False:
								for m in range(n+1,  len(self.SortedList) ):
										lowsig = self.SortedList[m][0]
										lowsigset = set(lowsig.split('-'))
										if len (lowsigset ) == len (topsigset ) + 1 and topsigset <= lowsigset: 
												moon = lowsigset ^ topsigset			
												if not topsig in Satellites:
														self.Satellites[topsig] = []			
												self.Satellites[topsig].append(  ( moon.pop(), len(Signatures[lowsig]) ) )
								if topsig in self.Satellites:
										print >>self.outfile, "\nSatellites", topsig, self.Satellites[topsig]
									
				print >>self.outfile, "\n\n  *** 3b. End of finding larger groupings of signatures \n\n"
				print "3b. End of finding larger groupings of signatures." 
		
		#STEP 4
		def shiftSameLetterNGrams(self):
				#TODO MAKE SOME OF THESE GLOBAL
				sizethreshold 		= 5 
				exceptionthreshold 	= self.StemCounts
				proportionthreshold = .9
				proportion 			= 0.000
				MaximalLettersToShift = 4
				outputtemplate = "%25s %25s %3s  %5f  "

				print "4. Check with each stem of a sig if they all end with the same gram." 
				print >>self.outfile, "\n\n*** 4. Check with each stem of a sig if they all end with the same gram. Shift one letter from end of stems.\n"

				for loopno in range(MaximalLettersToShift):
						print >> self.outfile, "*** Loop number in letter shift: " , loopno + 1
						for sig in self.Signatures.keys():	 			
								stemlist = sorted(self.Signatures[sig])	 
								if len(stemlist) < sizethreshold: 
										continue
								(CommonLastLetter, ExceptionCount, proportion) = TestForCommonSuffix(stemlist, self.outfile, self.FindSuffixesFlag)
								if ExceptionCount <= exceptionthreshold and proportion >= proportionthreshold:			 
										self.StemToWord, newsig = ShiftFinalLetter(self.StemToWord, self.StemCounts, stemlist, CommonLastLetter, sig, self.FindSuffixesFlag, self.outfile)  
										print >>self.outfile, outputtemplate % (sig, newsig,   CommonLastLetter, proportion)		
						NoLengthLimitFlag = True
						self.StemToWord, self.Signatures, self.WordToSig, self.StemToSig = MakeSignatures(self.StemToWord, self.StemToSig, self.FindSuffixesFlag,self.outfile, NoLengthLimitFlag) 
				print >> self.outfile, "\n\n*** 4. End of shifting one letter from end of stems" 
				print "4. End of shifting one letter from end of stems" 
				printSignatures(self.Signatures, self.WordToSig, self.StemCounts, self.outfile, self.g_encoding, self.FindSuffixesFlag)	
		
		#STEP 5
		def improveSignaturesForRobustness(self):
				NumberOfCorrections =0
				print >> self.outfile, "***"
				print >> self.outfile, "*** 5. Finding robust suffixes in stem sets\n\n"
				print "5a. Finding robust suffixes in stem sets"
				for loopno in range(1, NumberOfCorrections):
						bestrobustness = 0
						count = 0
						globalbestrobustness = 0
						bestsigtochange = ''
						shift = ''
						bestwidth = alignedlist1
						bestchunk = ''
						print >>self.outfile, "\n\nIteration", loopno  ," Best chunk found at end of stems in signatures: \n"
						for sig in self.Signatures.keys():
								n = 0			
								stemlist = sorted(self.Signatures[sig])	 
								bestchunk, bestrobustness = findmaximalrobustsuffix (self.stemlist, self.outfile,count) 
								if  bestchunk:
										print >>self.outfile, "Here is a best chunk",  sig, bestchunk 
										if bestrobustness > globalbestrobustness:
												globalbestrobustness = bestrobustness
												bestsigtochange = sig
												shift = bestchunk 
						print loopno, "Best sig to change: ", bestsigtochange, globalbestrobustness, shift, "\n"
						print >>self.outfile, "\n\nLoop number:", loopno, "Best sig to change: ", bestsigtochange, globalbestrobustness, shift, "\n"
						sig_target=bestsigtochangeStemToWord
						if len(shift) == 1:
								print >>self.outfile, "best chunk is 1 letter"
								self.StemToWord, self.Signatures = ShiftSignature(sig_target,shift,self.StemToWord,self.Signatures, self.outfile)
						if len(shift) > 1:
								print >>self.outfile, "best chunk is big: "
								self.StemToWord, self.Signatures = PullOffSuffix (sig_target, shift, self.StemToWord, self.Signatures, self.outfile)
						print >> self.outfile
						self.StemToWord, self.Signatures, self.WordToSig, self.StemToSig = MakeSignatures(self.StemToWord, self.StemToSig, self.FindSuffixesFlag, self.outfile) 
						printSignatures(self.Signatures, self.WordToSig, self.StemCounts, self.outfile, self.g_encoding, self.FindSuffixesFlag)
		
		#STEP 6
		def allomorphyDetection(self):
				StemCountThreshold 			= 5
				StemProportionThreshold 	= .9
				print >>self.outfile, "\n\n***6. Pairs of stems of adjacent lengths.\n"
				outputtemplate = "%35s : %35s  %15s %15s %50s"

				self.BiSigPatterns = {}
				for sig in self.Signatures.keys():		 
						stemlist = list(self.Signatures[sig])
						stemlist.sort()
						for stem in stemlist:			
								localwords = self.StemToWord[stem]
								stem2 = stem[:-1]		
								if self.g_encoding == "utf8":
										finalletter = stem[-1] + " "
								else:
										finalletter = "(" + stem[-1] + "): "				
								if stem2 in self.StemToWord.keys():
										overlapwordset = localwords.intersection(self.StemToWord[stem2])	
										wordstring = ""
								 		for word in overlapwordset:
												wordstring += " " + word 
										if len(overlapwordset) > 1:				 
												sig2 = self.StemToSig[stem2]
												if self.FindSuffixesFlag:
														print >>self.outfile, outputtemplate %(sig, sig2, stem, stem2, wordstring)
												else:
														print >>outfile, "<", sig, ": ", sig2, ">\n\t",stem[::-1], stem2[::-1], overlapwordset
												pattern = finalletter + "=" + sig + "=" + sig2 
												if not pattern in self.BiSigPatterns.keys():
														self.BiSigPatterns[pattern]=1
												else:
														self.BiSigPatterns[pattern]+=1
				 
				print "6b. End of dealing with multiple sigs for stems"

				print >>self.outfile, "***\n\nSummary: "
				outputtemplate = "%5s  %5s  %20s  %20s   "
				patternlist = sorted( self.BiSigPatterns, key = self.BiSigPatterns.get, reverse = True)
				threshold = 2
				for item in patternlist:
						if self.BiSigPatterns[item] > threshold:
								letter, sig1, sig2 = item.split("=")
								print >>self.outfile, outputtemplate % ( self.BiSigPatterns[item], letter, sig1, sig2 )
					 
				print >>self.outfile, "\n\n" 

				print >>self.outfile, "-------------------------------------------------------"
				print >>self.outfile, "6. End of dealing with signatures with multiple stems"
				print >>self.outfile, "-------------------------------------------------------"	
		
		#step 7
		#TODO ADD TO PROCESS
		def separateJoinedAffixes(self):
				self.SortedListOfSignatures = sorted( self.Signatures.items(), lambda x,y: cmp(len(x[1]), len(y[1]) ) , reverse=True)
				self.DisplayList = []

				for sig, stemlist in self.SortedListOfSignatures:	
						self.DisplayList.append((sig,len(stemlist),getrobustness(sig,stemlist)))
				if False:
						for signo in range (len(self.DisplayList)):
								sig = self.DisplayList[signo][0]
								affixlist = sig.split('-')
								if not len(affixlist) == 2:
										continue;
								if not affixlist[0]=='NULL':
										continue;
								if len(self.Signatures[sig]) < 10:
										continue;
								print >>self.outfile, "Signature", sig
								tally = 0
								stemset = self.Signatures[sig]
								for stem in stemset:
										biggerword = stem + affixlist[1]
										for otherstem in self.StemToWord.keys():
												if otherstem == stem:
														continue
												if otherstem == biggerword:
														continue
												if len(otherstem) > len(stem):
														continue
												if biggerword in self.StemToWord[otherstem]:
														tally += 1
														print >>self.outfile, biggerword, "(", otherstem, ")"
												#StemToWord[otherstem].discard(biggerword)
								print >>self.outfile, "Tally = ", tally

					#StemToWord, Signatures, WordToSig, StemToSig =  MakeSignatures(StemToWord, FindSuffixesFlag, outfile) 
					#printSignatures(Signatures, WordToSig, StemCounts, outfile, g_encoding, FindSuffixesFlag)
					#printWordsToSigTransforms(Signatures, WordToSig, StemCounts, outfileSigTransforms, g_encoding, FindSuffixesFlag)

				if False: 
					self.PerfectSignatures={}
					basictableau=intrasignaturetable()
					basictableau.setsignature( self.DisplayList[0][0] )
					basictableau.displaytofile(self.outfile)

					print "On to loop"
					minimumstemcount = 15
					print >>self.outfile, "\n\nPerfect signatures: \n"
					ShortList = []
					MaxSizeForShortList = 100
					for sig1, numberofstems, robustness in self.DisplayList:
							if numberofstems < minimumstemcount:
									continue
							tableau1=intrasignaturetable()
							tableau1.setsignature(sig1)		 
							print >>self.outfile, "\n\n--------------------------------------------------\n\t", "sig 1: ", sig1
							print >>self.outfile, "--------------------------------------------------\n\t" 	
							tableau1.displaytofile(outfile)
							print >>self.outfile, '\n' 
							for sig2, numberofstems2, robustness2 in self.DisplayList:
									if numberofstems2 < minimumstemcount:
											continue
									if sig1 == sig2:
											continue
									if not sig1.count('-') == sig2.count('-'):
											continue
									print >>self.outfile, "\n\n---------------------------------\n\t", "sig 2: ", sig2
									tableau2 = intrasignaturetable()
									tableau2.setsignature(sig2) 
									tableau2.minus(tableau1, DiffType)
									print >>outfile, "Difference of tableaux:"
									compressedSize = tableau2.displaytofile(outfile)
									for n in range(len(self.ShortList)):
											#print ShortList[n]
											if compressedSize < self.ShortList[n][2]:
													self.ShortList.insert(n, (sig1, sig2, compressedSize) )
													#print sig2
													break;		
									if n < MaxSizeForShortList:
											self.ShortList.append ( (sig1, sig2, compressedSize) ) 
									if len(self.ShortList) > MaxSizeForShortList:
											del self.ShortList[-1] 		
					print >>self.outfile, "end of loop: "
					for n in range(len(ShortList)):
							print >>self.outfile, ShortList[n]
		
		#THIS IS VERY CUMBERSOME, BUT WE WILL USE IT FOR NOW	
		def copyData(self, path, DiffType, FindSuffixesFlag, g_encoding, side , MinimumStemLength, MaximumAffixLength, MinimumNumberofSigUses, language, infolder, size, smallfilename, infilename, outfolder, outfilename, outfileSigTransformsname, outfileSigTransforms, StemFileExistsFlag):
				self.path = path
				self.DiffType = DiffType
				self.FindSuffixesFlag = FindSuffixesFlag
				self.g_encoding = g_encoding
				self.side = side
				self.MinimumStemLength = MinimumStemLength
				self.MaximumAffixLength = MaximumAffixLength
				self.MinimumNumberofSigUses = MinimumNumberofSigUses
				self.language = language
				self.infolder = infolder
				self.size = size
				self.smallfilename = smallfilename
				self.infilename = infilename
				self.outfolder = outfolder
				self.outfilename = outfilename
				self.outfileSigTransformsname = outfileSigTransformsname
				self.outfileSigTransforms = outfileSigTransforms
				self.StemFileExistsFlag	= StemFileExistsFlag
		
		#WE NEED FILE TYPE DETECTION (CORPUS VERSUS WORD COUNTS...)	
		def run(self):
				if len(self.path) > 1:
						self.infilename = self.path
				if not os.path.isfile(self.infilename):
						#SIGNAL NEEDED file does not exist WARNING
						#this will abort this process
						print "TEMP"
				self.progress_event.emit("opening corpus...", 0)
				if self.g_encoding == "utf8":
						self.infile = codecs.open(self.infilename, encoding = 'utf-8')
						self.outfile = codecs.open(self.outfilename, encoding =  "utf-8", mode = 'w',)
				else:
						self.infile = open(self.infilename) 
						self.outfile = open(self.outfilename,mode='w')
						 
				self.filelines= self.infile.readlines()
				self.WordCounts={}
				self.progress_event.emit("importing words...", 1)
				for line in self.filelines:
						pieces = line.split(' ')
						word=pieces[0] 
						#word = word[:-1] # for french only?
						word = word.lower()		 
						if (len(pieces)>1):
								self.WordCounts[word] = int( pieces[1] )
						else:
								self.WordCounts[word]=1
								
 				self.wordlist = self.WordCounts.keys()
 				self.progress_event.emit("sorting words...", 2)
 				self.wordlist.sort()
 				
 				self.numberofwords = len(self.wordlist)
 				
 				self.loadOrCreateStemFiles()

				#STEP 1
				#TODO SIGNAL
				print "1. Make signatures 1" 
				self.progress_event.emit("making signatures...", 3)
				self.StemToWord, self.Signatures, self.WordToSig, self.StemToSig =  MakeSignatures(self.StemToWord, self.StemToSig, self.FindSuffixesFlag, self.outfile) 
				#TODO FIGURE OUT HOW TO HANDLE THIS ONE
				printSignatures(self.Signatures, self.WordToSig, self.StemCounts, self.outfile, self.g_encoding, self.FindSuffixesFlag)
				
				#STEP 2
				self.progress_event.emit("collapsing signatures", 4)
				self.compareToCollapseSignatures()
				
				#STEP THREE REMOVED BECAUSE OF NEVER EXECUTED
				
				#STEP 4
				self.progress_event.emit("shifting same letter NGrams...", 5)
				self.shiftSameLetterNGrams()
				
				#STEP 5
				self.progress_event.emit("improving signatures for robustness...", 6)
				self.improveSignaturesForRobustness()
				
				#STEP 6
				self.progress_event.emit("allomorphy detection...", 7)
				self.allomorphyDetection()
				
				
				self.progress_event.emit("saving data...", 8)
				self.allomorphyDetection()
				print >>self.outfile, "***\n\nSummary: "
				outputtemplate = "%5s  %5s  %20s  %20s   "
				patternlist = sorted( self.BiSigPatterns, key = self.BiSigPatterns.get, reverse = True)
				threshold = 2
				for item in patternlist:
						if self.BiSigPatterns[item] > threshold:
								letter, sig1, sig2 = item.split("=")
								print >>self.outfile, outputtemplate % ( self.BiSigPatterns[item], letter, sig1, sig2 )
					 
				print >>self.outfile, "\n\n" 

				print >>self.outfile, "-------------------------------------------------------"
				print >>self.outfile, "6. End of dealing with signatures with multiple stems"
				print >>self.outfile, "-------------------------------------------------------"
				
				#what is left of STEP 7
				self.progress_event.emit("sorting signature list...", 9)
				self.SortedListOfSignatures = sorted( self.Signatures.items(), lambda x,y: cmp(len(x[1]), len(y[1]) ) , reverse=True)
				DisplayList = []

				for sig, stemlist in self.SortedListOfSignatures:	
						DisplayList.append((sig,len(stemlist),getrobustness(sig,stemlist)))
				self.progress_event.emit("saving signature transforms...", 10)
				printWordsToSigTransforms(self.Signatures, self.WordToSig, self.StemCounts, self.outfileSigTransforms, self.g_encoding, self.FindSuffixesFlag)
				
				self.outfile.close()	

				print self.outfilename 
				self.progress_event.emit("Complete!", 11)
				localtime = time.asctime( time.localtime(time.time()) )
				print "Local current time :", localtime
				numberofwords = len(self.wordlist)
				logfilename = self.outfolder + "logfile.txt"
				logfile = open (logfilename,"a")

				print >> logfile,  self.outfilename.ljust(60), '%30s wordcount: %8d data source:' %(localtime, numberofwords ), self.infilename.ljust(50) 				
				self.end_event.emit()
