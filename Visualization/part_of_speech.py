#TODO REFRACTOR TO CLASS 
#TODO NEED TO TAKE INPUT FROM tri_gram_maker
# -*- coding: <utf-16> -*- 
import codecs
import os
import sys
import string
import operator
from math import sqrt
from  collections import defaultdict 
import numpy
from numpy import *

mywords=dict()

unicodeFlag = True
FileEncoding =  "utf-16"
 
NumberOfWordsUsedForMatrix 	= 3000
NumberOfEigenvectors 		= 11
HowManyWordsToShow		= 3000
howManyNeighborsToShow 		= 10

if HowManyWordsToShow > NumberOfWordsUsedForMatrix:
	print "No -- the number of words to be shown must be no larger than the number of words used for the matrix."

wordtoindex 		= dict()
internalwords 		= dict()
linecount 			= 0
externalwordlist 	= list() # this means that the info comes from the independent word file
internalwordlist	= list() # this is a word list created from the trigram file.
 
shortfilename 		= "small_chinese_corpus"
languagename 		= "chinese"
 
infileTrigramsname 	= "../../data/" + languagename + "/" + shortfilename + "_trigrams.trig"
infileWordsname 	= "../../data/" + languagename + "/" + shortfilename + "_words.txt" 
 
outfilename1 		= languagename + "_" + shortfilename + "_PoS_words_eigen" + ".txt"
outfileneighborsname 	= languagename + "_" + shortfilename + "_PoS_closest" + "_" + str(howManyNeighborsToShow) + "_neighbors.txt"
outfilename3 		= languagename + "_" + shortfilename + "_PoS_file3.txt"

print "I am looking for: ", infileTrigramsname

if unicodeFlag:
	trigramfile 		=codecs.open(infileTrigramsname, encoding = FileEncoding)
	wordfile 		=codecs.open(infileWordsname, encoding = FileEncoding)

	outfilewordseigen	= codecs.open (outfilename1, "w",encoding = FileEncoding)
	outfileneighbors	= codecs.open (outfileneighborsname, "w",encoding = FileEncoding)
else:
	outfilewordseigen	= open (outfilename1, "w")
	outfileneighbors	= open (outfileneighborsname, "w")
	wordfile		= open(infileWordsname)
	trigramfile 		= open(infileTrigramsname)


punctuation 		= " $/+.,;:?!()\"[]"
 
 


print languagename, shortfilename, NumberOfWordsUsedForMatrix

print >>outfilewordseigen, "#", languagename, shortfilename, "Number of words used for matrix", NumberOfWordsUsedForMatrix, "Number of words analyzed", HowManyWordsToShow, "Number of neighbors identified", howManyNeighborsToShow

print >>outfileneighbors, "#", languagename, shortfilename, "Number of words used for matrix", NumberOfWordsUsedForMatrix, "Number of words analyzed", HowManyWordsToShow, "Number of neighbors identified", howManyNeighborsToShow

 
WordToIndex = dict()
contexts = dict()


if infileTrigramsname[-5:]==".trig":
	for line in wordfile:
		#print "line 57", line
		pieces = line.split()
		print pieces[0] 
		if pieces[0] == "#":
			continue
		mywords[pieces[0]] = int(pieces[1])
		externalwordlist.append(pieces[0])
	print "1. We have read in the word file.", len(externalwordlist) , "words."
	wordfile.close()

	print "2. Reading in trigram file."
	for line in trigramfile:
		line = line.split()
		if line[0] == "#":
			continue
		thesewords = line[0].split("_")
		#Center trigrams
		for word in thesewords:
			if not word in internalwords:
				internalwords[word] = 1
			context = thesewords[0] + "_" +  thesewords[2]
			if not context in contexts:
				contexts[context] = dict()
			if not thesewords[1] in contexts[context]:
				contexts[context][thesewords[1]] = 1
			contexts[context][thesewords[1]] += 1
		
		
			#Left trigrams
			context = thesewords[1] + "_" + thesewords[2]
			if not context in contexts:
				contexts[context] = dict()
			if not thesewords[0] in contexts[context]:
				contexts[context][thesewords[0]] = 1
			contexts[context][thesewords[0]] += 1

			#Right trigrams
				
			context = thesewords[0] + "_" + thesewords[1]
			if not context in contexts:
				contexts[context] = dict()
			if not thesewords[2] in contexts[context]:
				contexts[context][thesewords[2]] = 1
			contexts[context][thesewords[2]] += 1

	internalwordlist = internalwords.keys()
	print "Number of internal words: ", len(internalwordlist) 
	internalwordlist.sort()
	externalwordlist = sorted(mywords,key=mywords.__getitem__,reverse=True)
	print "Length of internal word list: ", len(internalwordlist) 
 	print "\tGenerating shorter wordlist..."
 	for wordno in range(NumberOfWordsUsedForMatrix):
		word = externalwordlist[wordno]
		wordtoindex[word] = wordno
	print "Done."

	print "3. We will consider the top", NumberOfWordsUsedForMatrix, " words." 

if infileTrigramsname[-4:-1] == ".txt":
	for line in file:
		if not line:
			break
		linecount +=1
		line = line[:-1]
		words = line.split()
		words.append("#")
		previousword = "#" 
		wordnumber = 0
		for word in words:
			word = word.lower()
			for c in punctuation:
				word = word.replace(c,"")
			if len(word)==0:
				#word = "DUMMY"
				continue 			
			if word in mywords:
				mywords[word] += 1
			else:
				mywords[word] = 1
	file.close() 
 

	print "4. Vocabulary size:", len(mywords), " but we will shorten it." 
	# Sort word list by frequency:
	internalwordlist = sorted(mywords,key=mywords.__getitem__,reverse=True)
 

 
	for wordno in range(NumberOfWordsUsedForMatrix):
		word = internalwordlist[wordno]
		wordtoindex[word] = wordno
		#print >>outfilewordseigen, wordno, word, mywords[word]

	linecount = 0
	file = open(infilename) 
	for line in file: 	 
		if not line:
			break
		linecount +=1
		#if linecount > 1000:
		#	break
		line = line[:-1]
		words = line.split()
		words.append("#")
		previousword = "#" 
		wordnumber = 0
		for word in words:
			word = word.lower()
			if wordnumber == 0:
				wordnumber = 1
				word1 = word
				continue
			if wordnumber == 1:
				wordnumber = 2
				word2 = word
				continue
			word3 = word
			if not word1 in mywords or not word2 in mywords or not word3 in mywords:
				word1 = word2
				word2 = word3
				continue
			context = word1 + "_" + word3
			if context not in contexts:		
				contexts[context] = dict() 
			if not word2 in contexts[context]:
				contexts[context][word2] = 1
			else:
				contexts[context][word2] += 1
##--------------------------------------------------------------
# Left side bigrams
			context = word1 + "+" + word2 + "_"
			if context not in contexts:		
				contexts[context] = dict()
			if not word3 in contexts[context]:
				contexts[context][word3] = 1
			else:
				contexts[context][word3] += 1
##--------------------------------------------------------------
##--------------------------------------------------------------
# Right side bigrams
			context = "_"+ word2 + "+" + word3
			if context not in contexts:		
				contexts[context] = dict()
			if not word1 in contexts[context]:
				contexts[context][word1] = 1
			else:
				contexts[context][word1] += 1
##--------------------------------------------------------------			
			word1 = word2
			word2 = word3


			
print "5. Vocabulary size:", len(mywords)

contextlist = contexts.keys() 
contextlist.sort(key=lambda tuple:tuple[1],reverse=True)
 
 
print "6. End of words and counts"
print "7. Iterate through contexts...."
 
NearbyWords = zeros( (NumberOfWordsUsedForMatrix,NumberOfWordsUsedForMatrix) )
 
for context in contexts:		 
	for word1 in contexts[context]:	
		if not word1 in wordtoindex:
			continue
		w1 = wordtoindex[word1]	
		for word2 in contexts[context]:
			if not word2 in wordtoindex:
				continue
			w2 = wordtoindex[word2]
			if not w1 == w2:		
				NearbyWords[w1][w2] += 1
print "\tDone."

print "8. We normalize nearness measurements...."
Diameter = defaultdict()
for w1 in range(NumberOfWordsUsedForMatrix):
	for w2 in range(NumberOfWordsUsedForMatrix):
		if w1 == w2:
			continue
		if not w1 in Diameter:
			Diameter[w1] = 0		 
		Diameter[w1] += NearbyWords[w1][w2] 
print "\t Done."
print "9. We compute the incidence graph....",
incidencegraph= zeros( (NumberOfWordsUsedForMatrix,NumberOfWordsUsedForMatrix) )
for w1 in range( NumberOfWordsUsedForMatrix ):
	for w2 in range( NumberOfWordsUsedForMatrix ):
		if w1 == w2:
			incidencegraph[w1,w1] = Diameter[w1]
		else:
			incidencegraph[w1, w2] = NearbyWords[w1,w2]	

print "Done."
 		 

 

print "10. We normalize the laplacian....",
#Normalize the laplacian:
mylaplacian = zeros((NumberOfWordsUsedForMatrix,NumberOfWordsUsedForMatrix) )
for i in range(NumberOfWordsUsedForMatrix):
	mylaplacian[i,i] = 1
	for j in range(NumberOfWordsUsedForMatrix):
		if not i == j:
			if incidencegraph[i,j] == 0:
				mylaplacian[i,j]=0
			else:
				mylaplacian[i,j] = -1 * incidencegraph[i,j]/ math.sqrt ( Diameter[i] * Diameter[j] )		 	
print "Done."

print "11. Compute Laplacian"
myeigenvalues, myeigenvectors = numpy.linalg.eigh(mylaplacian)

print >>outfilewordseigen, "the eigenvectors"
print >>outfilewordseigen, myeigenvectors
print "12. Finished printing eigenvctors to file."
"""
#  write latex output:
data = dict()
print ("Printing contexts to file.")
formatstr = '%15d  %15s %10.3f'

NumberOfDimensionsToRecord = 10 
 
mylist = list()
for eigenno in range(NumberOfWordsUsedForMatrix):
	mylist=list()	
	if eigenno < 20:
		data[eigenno] = list()
#	print >>outfile
#	print >>outfile, "\nNumber", eigenno,":",  myeigenvalues[eigenno]
	for i in range (NumberOfWordsUsedForMatrix):		 
		mylist.append( (i,myeigenvectors[i, eigenno]) )
		mylist.sort(key=lambda x:x[1])
	for i in range(NumberOfWordsUsedForMatrix):			 
#		print >>outfile, "%5d %10s %10.3f" %  ( i, wordlist[mylist[i][0]], mylist[i][1] )
		if eigenno < 20:
			if i < 20:
				data[eigenno].append((i, wordlist[mylist[i][0]], mylist[i][1] ))
			if i > NumberOfWordsUsedForMatrix - 20:
				data[eigenno].append((i, wordlist[mylist[i][0]], mylist[i][1] ))
			
#Latex output
print >>outfile1, filename
for eigenno in data.keys():
	print >>outfile1
	print >>outfile1, "Eigenvector number", eigenno 
	print >>outfile1, "\\begin{tabular}{lll}\\toprule"
	print >>outfile1, " & word & coordinate \\\\ \\midrule "
	for (i, word, coord) in data[eigenno]:
		print >>outfile1,  "%5d & %10s &  %10.3f \\\\" % (i, word, coord) 
	print >>outfile1, "\\bottomrule \n \\end{tabular}", "\n\n"

"""	
#=================================================================

print "13. Finding coordinates in space of low dimensionality."

coordinates 		= dict()
wordsdistance 		= dict()
closestNeighbors 	= dict() #a dict whose values are lists; the lists are the closest words to the key.

if HowManyWordsToShow > len(internalwordlist):
	HowManyWordsToShow = len(internalwordlist)

thislist = list() 


print "\t 1. How many words to show:", HowManyWordsToShow
for wordno in range(HowManyWordsToShow):
	coordinates[wordno]= list() 
	for i in range (1,NumberOfEigenvectors):
		coordinates[wordno].append ( myeigenvectors[ wordno, i ] )
for wordno in range(HowManyWordsToShow):	 
	word = externalwordlist[wordno]
	print >>outfilewordseigen, "line 336", word
        if word not in wordsdistance:
            wordsdistance[word] = list()
	for wordno2 in range (HowManyWordsToShow):		 
		distance = 0
		for coordno in range(NumberOfEigenvectors-1):
			x = coordinates[wordno][coordno] - coordinates[wordno2][coordno]
			distance += abs(x * x * x)		 
                wordsdistance[externalwordlist[wordno]].append((wordno2,distance))
		print >>outfilewordseigen, "\t", externalwordlist[wordno2], distance		


print "\t 2. Finding closest neighbors on the manifold('s approximation)."
		 
for wordno in range(HowManyWordsToShow):    
	word = externalwordlist[wordno]
	if not word in internalwordlist:
		print "This word not found in trigrams, unfortunately:", word
		
	#print "\t2:", word
	if not word in closestNeighbors:
		closestNeighbors[word] = list()
	wordsdistance[word].sort(key=lambda x:x[1])     
	print >>outfileneighbors, word, 
	for index in range (1,howManyNeighborsToShow+1):
		wordno2 = wordsdistance[word][index][0]
		if wordno == wordno2:
			continue	
		word2 = externalwordlist[wordno2]
		print >>outfileneighbors, word2,
		closestNeighbors[word].append(word2)	 	 
	print >>outfileneighbors
outfileneighbors.close()

 

outfilewordseigen.close()
outfileneighbors.close()
 


