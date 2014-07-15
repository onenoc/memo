class MemoizedObject:
	def __init__(self, definition, cache_object, args, kwargs):
		self.definition = definition
		self.cache_object = cache_object
		self.args = args
		self.kwargs = kwargs

