#TODO GENERAL CLEAN UP + TESTING
# -*- coding: <utf-16> -*- 
import codecs
import os
import sys
from  collections import defaultdict 

class tri_gram_maker():
		def __init__():
				self.unicode = True
				self.language = "chinese"
				self.infolder = '../../data/' + language + '/'	
				self.size = 10
				self.FileEncoding = "utf-16"
				self.specificname = "chinese_large_corpus"
				self.infilename = self.infolder + self.specificname +  ".txt"
				self.wordcountlimit = 1000000
				self.n = 0
				self.words = {}
				self.maximumnumberoflines = -1
				self.outfolder = self.infolder
				self.linenumber = 0
				self.mywords=defaultdict()
				self.trigrams = dict()
				self.punctuation = " $/+:?!()\"[]"
 				if self.maximumnumberoflines > 0:
						self.suffix = "_"+ str(self.maximumnumberoflines) 
				else:
						self.suffix = ""
				self.outfilename1 	= outfolder + specificname + suffix +  "_trigrams.trig"
				self.outfilename2 	= outfolder + specificname + suffix +  "_trigramsalphabetized.trig"
				self.outfilename3 	= outfolder + specificname + suffix +  "_words.txt"
		
		def process_file(path):
				#TODO RESOLVE THIS
				self.specificname = path 
 				if unicode:
						outfiletrigrams1 = codecs.open(self.outfilename1, "w", encoding = self.FileEncoding)
						outfiletrigrams2 = codecs.open(self.outfilename2, "w",encoding = self.FileEncoding)
						outfilewords = codecs.open(self.outfilename3, "w",encoding = self.FileEncoding)
						file1 = codecs.open(self.infilename,encoding = self.FileEncoding)
				else:
						outfiletrigrams1 = open(self.outfilename, "w")
						outfiletrigrams2 = open(self.outfilename, "w")
						outfilewords 	 = open(self.outfilename, "w")
						file1 = open(self.infilename)
				print "infilename", infilename
		for line in file1:
				wordno = 0
				#print line
				if not line:
						continue
				self.linenumber += 1
				if self.aximumnumberoflines > 0 and  self.linenumber  > self.maximumnumberoflines:
						break;
				line = line[:-1]
				line = line.replace(".", " .")
				line = line.replace(",", " ,")
				line = line.replace(";", " ;")	
				self.words = line.split()
				for word in self.words:
						word = word.lower()
						for c in punctuation:
								word = word.replace(c,"")
						if len(word)==0:
								continue			
						if word in mywords:
								self.mywords[word] += 1
						else:
								self.mywords[word] = 1
						if wordno == 0:
								word1= word
								wordno = 1
								continue
						if wordno== 1:
								word2 = word
								wordno = 2
								continue
						word3 = word
						trigram = word1+"_"+ word2 + "_" + word3
						if not trigram in self.trigrams:
								self.trigrams[trigram] = 1
						else:
								self.trigrams[trigram] += 1
						#print trigram
						word1 = word2
						word2 = word3
		print "Completed counting words and trigrams."
		print >>outfilewords, "# ", len(self.mywords), "words."
		print >>outfilewords, "# ", self.infilename
		print >>outfiletrigrams1, "# ", len(self.mywords), "words."
		print >>outfiletrigrams1, "# ", self.infilename
		print >>outfiletrigrams2, "# ", len(self.mywords), "words."
		print >>outfiletrigrams2, "# ", self.infilename
		self.toptrigrams = [x for x in self.trigrams.iteritems()]
		self.toptrigrams.sort(key=lambda x:x[1], reverse=True)
	
		for trigram in self.toptrigrams:	 
				print >>outfiletrigrams1, trigram[0], trigram[1]

		self.trigramlist = list()
		for trigram in self.toptrigrams:
				self.trigramlist.append(trigram)
		self.trigramlist.sort()
	
		for trigram in self.trigramlist:
				print >>outfiletrigrams2, trigram[0], trigram[1]
		 
	
		self.top_words = [x for x in self.mywords.iteritems()]
		self.top_words.sort(key=lambda x: x[1],reverse=True)

		 
		print size
		truesize = size * 1000

		count = 0
		for word in self.top_words:	 
				count += 1
				print >>outfilewords, word[0], word[1]
				#if count > truesize:
				#	break
		outfilewords.close()
		outfiletrigrams1.close()
		outfiletrigrams2.close()
