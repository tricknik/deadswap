from sweetpotato.core import TaskAdapter

class do(TaskAdapter):
	def run(self):
		target = self.task.getProperty('target')
		if not target:
			target = self.task.getProperty('value')
		if target:
			self.call(target)

	def call(self, target):
		prange = self.task.getProperty('range')
		if hasattr(prange,'pop'):
			args = []
			for arg in prange:
				args.append(int(arg))
			list = range(*args)	
		elif prange and str(prange).isdigit():
			list = range(int(prange))
		else:
			list = self.task.getProperty('list')
		if not list:
			list = [target]
		self.doList(target, list)
	def doList(self, target, list):
		iterationToken = self.task.getProperty('settoken')
		sweetpotato = self.task.sweetpotato
		for item in list:
			if iterationToken:
				sweetpotato.setToken(iterationToken, item)
			sweetpotato.run(target)
