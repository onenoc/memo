import hashlib

class MemoizerDataFrame:
	def __init__(self, dataframe):
		self.dataframe = dataframe.copy()
		symbols = list(self.dataframe.columns.values)
		symbols_string = " , ".join(symbols)
		dataframe_info = symbols_string+str(self.dataframe)
		self.h = hashlib.md5(dataframe_info).hexdigest()
	def get_dataframe(self):
		return self.dataframe.copy()
	def get_hash(self):
		return self.h	
