# -*- coding: <utf-16> -*- 
unicode = True
import codecs
import os
import sys

unicodeFlag = True
FileEncoding = "utf-16"

import string
import operator
mywords=dict()
from math import sqrt
from  collections import defaultdict 
#import numpy
#from numpy import *
#import networkx

# Import graphviz
#TODO WHY IS THIS HERE?
import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')





#import gv
# --------------------------------------------------------------------------- # 

def readfile1(infile, wordtoindex, wordindex, wordlist, howmanyneighbors, myedges):
	wordcount = 0
	for line in infile:	 
		words = line.split()
		if len(words) == 0:
			continue
	 
		if words[0] == "#":
			languagename = words[1]
			shortfilename = words[2]
			continue
		for word in words:
			if not word in wordtoindex:
				wordtoindex[word] = wordindex
				wordindex += 1
				#mynodes[word] = 1
		wordcount += 1  
	

		word = words[0]
		wordlist.append(word)
		for i in range(1, howmanyneighbors):
			neighborword = words[i]
	
			if not word in myedges: #my edges is used because we often need to iterate over the second variable (across a row, so to speak)
				myedges[word] = dict()
			myedges[word][neighborword]= 1

			if not words[i] in myedges:
				myedges[words[i]] = dict()
			myedges[words[i]][word] = 1
 
	for word in wordlist:
		print word
		wordno = wordtoindex[word]
		for word2 in myedges[word]:   
			wordno2 = wordtoindex[word2]
			edgelist.append ( (wordno, wordno2) ) #this is convenient for outputting.
			
	return (languagename, shortfilename, wordcount, myedges, wordtoindex, wordlist, edgelist )
# --------------------------------------------------------------------------- # 


def printGephinodes(outfileGephi, HowManyWords, wordlist, edgelist, wordcount, edgecount,  wordtoindex): 

	print >>outfileGephi, "\t\t<nodes count=\" ", wordcount, " \"> "
	#for i in range(HowManyWords):
	for word in wordlist:
		#print i, wordlist[i]
		#thisword = wordlist[i]
		thisword = word
		i = wordtoindex[word]
		lineToPrint = "\t\t\t<node id =\""
		lineToPrint += str(i)
		lineToPrint += "\" label =\""
		lineToPrint += thisword
		lineToPrint +="\""
		#lineToPrint += "/"
		lineToPrint += ">"
		print >>outfileGephi, lineToPrint
	 
		tag = list()
		tag.append("NULL-ed-ing-s_NULL")
		tag.append("NULL-ed-ing-s_s")
		tag.append("NULL-ed-ing-s_ing")
		tag.append("NULL-ed-ing-s_ed")

		if thisword in color:
			if color[thisword] == tag[0] :		 
				lineToPrint =  "\t\t\t\t<viz:color r=\"239\" g=\"173\" b=\"66\" a=\"0.6\"/>"		 
				print >>outfileGephi, lineToPrint
				lineToPrint =  "\t\t\t\t<viz:size value=\"20\"/>"		 
				print >>outfileGephi, lineToPrint	 
	 		 
	
			if color[thisword] == tag[1]:		 
				lineToPrint =  "\t\t\t\t<viz:color r=\"39\" g=\"200\" b=\"66\" a=\"0.6\"/>"		 
				print >>outfileGephi, lineToPrint
				lineToPrint =  "\t\t\t\t<viz:size value=\"20\"/>"		 
				print >>outfileGephi, lineToPrint
	 		 
		 
			if color[thisword] == tag[2]:		 
				lineToPrint =  "\t\t\t\t<viz:color r=\"39\" g=\"50\" b=\"150\" a=\"0.6\"/>"		 
				print >>outfileGephi, lineToPrint
				lineToPrint =  "\t\t\t\t<viz:size value=\"20\"/>"		 
				print >>outfileGephi, lineToPrint
			 

			if color[thisword] == tag[3]:		 
				lineToPrint =  "\t\t\t\t<viz:color r=\"39\" g=\"0\" b=\"10\" a=\"0.6\"/>"		 
				print >>outfileGephi, lineToPrint
				lineToPrint =  "\t\t\t\t<viz:size value=\"20\"/>"		 
				print >>outfileGephi, lineToPrint

		lineToPrint ="\t\t\t</node>"
		print >>outfileGephi, lineToPrint

	print >>outfileGephi, "\t\t</nodes>"

	# Print Gephi edges
	print >>outfileGephi, "\t\t<edges count=\" ", edgecount, " \"> "
	for edgeno in range(len(edgelist)):
		sourceno = edgelist[edgeno][0]
		targetno = edgelist[edgeno][1]
		lineToPrint = "\t\t\t<edge id =\""
		lineToPrint += str(edgeno)
		lineToPrint += "\" source = \""
		lineToPrint += str(sourceno)
		lineToPrint += "\" target = \""
		lineToPrint +=  str(targetno)
		lineToPrint += "\"/>"
		print >>outfileGephi, lineToPrint
	print >>outfileGephi, "\t\t</edges>"
	print >>outfileGephi, "\t</graph>"
	print >>outfileGephi, "\t</gexf>"

# ---------------------------------------------------------------------------------------------------------------

wordtoindex = dict()
HowManyWords = 1000
languagename = "chinese"
shortname = "_" + "small_chinese_corpus"
outnametag = ""
 
filename 	= languagename + shortname + "_PoS_closest_10_neighbors.txt"
colorfilename 	= languagename + shortname + "_suffixalsigtransforms.txt"
outfilenameGephi= languagename + shortname +  outnametag + ".gexf"
outfilename2 	= languagename + shortname +  outnametag + "pagerank.txt"
colorfilename = ""

if unicodeFlag:
	outfileGephi = codecs.open (outfilenameGephi, "w", encoding = FileEncoding)
	outfile2 	= codecs.open (outfilename2, "w", encoding = FileEncoding)
	infile 		= codecs.open (filename, encoding = FileEncoding)
else:
	outfileGephi = open (outfilenameGephi, "w")
	outfile2 = open (outfilename2, "w")
	infile = open(filename)

 
print >>outfileGephi, "<gexf xmlns=\"http://www.gexf.net/1.2draft\" xmlns:viz=\"http://www.gexf.net/1.2draft/viz\">"
print >>outfileGephi, "\t<graph defaultedgetype=\"directed\" idtype=\"string\" type=\"static\">"

color = dict() 
if len(colorfilename) > 0:
	colorfile = open(colorfilename)
	for line in colorfile:
		thisword, thiscolor = line.split()
		if thisword == "#":
			continue
		color[thisword] = thiscolor
		#print thisword, color[thisword]
 
 
mynodes 			= dict()
myedges 			= dict()
howmanyneighbors 	= 4
closestNeighbors 	= dict() 
wordlist 			= list()
edgelist 			= list()
closestNeighbors	= dict()
edgecount 			= 0 
wordindex 			= 0
pagerank 			= dict()
alpha 				= 0.2
seedword 			= "should"
pagerank[seedword] 	= 1.0


# Read file!
(languagename, shortfilename, wordcount, myedges, wordtoindex, wordlist, edgelist ) = readfile1 (infile, wordtoindex, wordindex, wordlist, howmanyneighbors, myedges)
 
print "starting graph"

# First we normalize the rows:
for word in myedges:
	rowsum = 0
	for word2 in myedges[word]:
		rowsum += float(myedges[word][word2])
	for word2 in myedges[word]:
		myedges[word][word2] = myedges[word][word2]/rowsum
 

pagerank2 = dict()
# 1st iteration:
for word in myedges:
	if word in pagerank and pagerank[word] > 0:
		print >>outfile2, "1:", word
		for word2 in myedges[word]:
			pagerank2[word2] = alpha * (1-alpha) * myedges[word][word2]* pagerank[word]
			print >>outfile2, word, word2, pagerank2[word2]
 
print >>outfile2, "testing pointers..."
pagerank = dict()
for word in pagerank2:	
	for word2 in pagerank2[word]: 
		pagerank[word][word2] = pagerank2[word][word2]

print >>outfile2, "------------------------"

print >>outfile2, "testing pointers..."
for word in pagerank:
	print word
	for word2 in pagerank[word]:
		print "\t", word2


pagerank2 = dict()

 

for word in myedges:
	if word in pagerank and pagerank[word] > 0:
		for word2 in myedges[word]:
			pagerank[word2] += alpha * (1-alpha) * myedges[word][word2]* pagerank[word]
			print >>outfile2, word, word2, pagerank[word2]




#  Print Gephi nodes
printGephinodes(outfileGephi, HowManyWords, wordlist, edgelist, wordcount, edgecount,  wordtoindex)


 


 
"""" 
 
print "Printing all words' neighbors."
wordsAlreadyPinnedDict 	= dict()
wordsAlreadyExpandedDict = dict()
TotalList 				= list()
word 					= "the"
TotalList.append(word)
columnindex 				= 0
maxcolumnindex 				= 3
rowindex				= 0
currentpointer 				= 0
x 					= columnindex 
y 					= rowindex
colors 	=["gray", "lightgray","red","green","blue","cyan","magenta","yellow"]
colorindex 	= 0
print >>outfile1, "\n\\cnodeput(",x,",",y,"){", word,"}{",word,"}"
wordsAlreadyPinnedDict[word] = 1
columnindex += 1 


while currentpointer < len(TotalList) and currentpointer < 1000:
	word = TotalList[currentpointer]	
	if word in wordsAlreadyExpandedDict:		 
		currentpointer += 1
		continue
	if colorindex == len(colors)-1:
		colorindex = 0
	colorindex += 1
	color = colors[colorindex]
	for index in range(len(closestNeighbors[word])):
		word2 = closestNeighbors[word][index]
		if not word2 in wordsAlreadyPinnedDict: 
			x = columnindex*4 
			columnindex += 1
			if columnindex > maxcolumnindex:
				columnindex 	= 0
				rowindex 	+= 1
			y = rowindex*3	
			print >>outfile1, "\n\\cnodeput(",x,",",y,"){", word2,"}{",word2,"}"
		 
			TotalList.append(word2)	
			wordsAlreadyPinnedDict[word2] = 1

		
		print >>outfile1, "\n\\ncarc[arcangle=10,linecolor=", color, ",linewidth=2pt]{->}{", word, "}{",word2, "}"
	 
	currentpointer += 1
	wordsAlreadyExpandedDict[word] = 1	

print >>outfile1, "End of this chain."

"""
 


#outfile1.close() 
outfileGephi.close()



