class process:
	def __init__(self, pid, time, cpuBurst):
		self.pid = pid
		self.time = time
		self.cpuBurst = cpuBurst
	def work(tempo):
		if tempo < self.time:
			self.time -=tempo
			return False
		else:
			return True



class roundRobin:
	def __init__(self, quantum):
		self.line = []
		self.quantum = quantum
class fcfs:
	def __init__(self):
		self.line = []
