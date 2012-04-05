from renderClasses import *

class render_signature(render_base):
		def __init__(self, signature, stems):
				super(render_signature, self).__init__()
				self.signature = signature
				self.stems = stems
				self.dn = "Signature - "+self.signature
				self.renderableKeys["Signature"] = (False, ("STR",[]), None)
				self.renderableKeys["Stems"] = (False, ("STR",[]), None)
		
		def gatherValues(self, k):
				if k == "Signature":
						return self.signature
				if k == "Stems":
						output = ""
						first = True
						for j in self.stems:
								if first:
										output += j
										first = False
								else:
										output += ", "+j
						return output

class render_word(render_base):
		def __init__(self, word, signature):
				super(render_word, self).__init__()
				self.signature = signature
				self.word = word
				self.dn = "Word - "+self.word
				self.renderableKeys["Word"] = (False, ("STR",[]), None)
				self.renderableKeys["Signature"] = (False, ("STR",[]), None)
		
		def gatherValues(self, k):
				if k == "Signature":
						return self.signature
				if k == "Word":
						return self.word

class render_stem(render_base):
		def __init__(self, stem, words, signature, count):
				super(render_stem, self).__init__()
				self.signature = signature
				self.words = words
				self.stem = stem
				self.count = count
				self.dn = "Stem - "+self.stem
				self.renderableKeys["Words"] = (False, ("STR",[]), None)
				self.renderableKeys["Signature"] = (False, ("STR",[]), None)
				self.renderableKeys["Count"] = (False, ("STR",[]), None)
				self.renderableKeys["Stem"] = (False, ("STR",[]), None)
		
		def gatherValues(self, k):
				if k == "Signature":
						return self.signature
				if k == "Words":
						output = ""
						first = True
						for j in self.words:
								if first:
										output += j
										first = False
								else:
										output += ", "+j
						return output
				if k == "Count":
						return str(self.count)
				if k == "Stem":
						return self.stem


		

