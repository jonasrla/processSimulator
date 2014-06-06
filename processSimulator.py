import csv

class Queue(object):
    def __init__(self):
        self.queue = []

    def add(self, proc):
        self.queue.append(proc)

    def pop(self):
        return self.queue.pop(0)

    def isEmpty(self):
        return len(self.queue) == 0

class Process(object):
    def __init__(self, pid, timeLine):
        self.pid = pid
        self.timeLine = timeLine
        self.inIO = (timeLine[0]["kind"] == "IO")
        self.isOver = False

    def getPid(self):
        return self.pid

    def work(self):
        if not self.inIO:
            self.timeLine[0]["time"] -= 1
            if self.timeLine[0]["time"] == 0:
                if len(self.timeLine) == 1:
                    self.isOver = True

                else:
                    self.inIO = True
                    self.timeLine.pop(0)
        else:
            raise Exception("Executando CPU em IO")

        
    def readWrite(self):
        if self.inIO:
            self.timeLine[0]["time"] -= 1
            if self.timeLine[0]["time"] == 0:
                if len(self.timeLine) == 1:
                    self.isOver = True

                else:
                    self.inIO = False
                    self.timeLine.pop(0)
        else:
            raise Exception("Executando IO em CPU")

    def isInterrupted(self):
        return self.inIO

    def checkIO(self):
        return not self.inIO

    # def isOver(self):
    #     return self.isOver




class RoundRobin(Queue):
    def __init__(self, quantum, lista):
        Queue.__init__(self)
        self.quantum = quantum
        self.queue = [{
            "process": Process(lista[i]["pid"], lista[i]["timeLine"]),
            "quantum": self.quantum
        } for i in range(len(lista))]

    def add(self, proc):
        self.queue.append({"process": proc, "quantum": self.quantum})

    def returnQueue(self, proc,remainingQuantum):
        self.queue.append({"process": proc, "quantum": remainingQuantum})

    def run(self):
        # print "run len(" + str(len(self.queue)) + ") " + str(self.quantum)
        pid = self.queue[0]["process"].getPid()
        if (not self.queue[0]["process"].isInterrupted()):
            self.queue[0]["process"].work()
            self.queue[0]["quantum"] -= 1
            #print self.queue[0]["quantum"]
            if (self.queue[0]["process"].isOver):
                self.pop()
            return pid

    def timeOut(self):
        return self.queue[0]["quantum"] == 0

    def isInterrupted(self):
        return self.queue[0]["process"].isInterrupted()

class IO(Queue):
    def __init__(self):
        Queue.__init__(self)

    def run(self):
        self.queue[0][0].readWrite()

    def finishedIO(self):
        return self.queue[0][0].checkIO()


class FCFS(Queue):
    def __init__(self, lista):
        Queue.__init__(self)
        self.queue = [process(lista[i]["pid"],lista[i]["timeLine"]) for i in range(len(lista))]

    def run(self):
        print "run len(" + str(len(self.queue)) + ") " + "fcfs"
        pid = self.queue[0].getPid()
        if (not self.queue[0].isInterrupted()):
            self.queue[0].work()
            if self.queue[0].isOver:
                self.queue.pop(0)
            return pid

    def isInterrupted(self):
        return self.queue[0].isInterrupted()

    def returnQueue(self, proc):
        self.add(proc)


class Schedule(object):
    def __init__(self,listaq0,listaq1,listaq2):
        self.q0 = RoundRobin(10, listaq0)
        self.q1 = RoundRobin(20, listaq1)
        self.q2 = FCFS(listaq2)
        self.io = IO()
        self.log = []

    def isOver(self):
        return self.q0.isEmpty() and self.q1.isEmpty() and self.q2.isEmpty() and self.io.isEmpty()

    def run(self):
        validCycle = True
        while not self.isOver():
            
            if not self.q0.isEmpty():
                if self.q0.isInterrupted():
                    validCycle = False
                    info = self.q0.pop()
                    self.io.add((info["process"],0,info["quantum"]))

                elif not self.q0.timeOut():
                    pid = self.q0.run()
                    if pid != None:
                        self.log.append(str(pid) + " q0")

                elif self.q0.timeOut():
                    validCycle = False
                    print "timeOut 1"
                    info = self.q0.pop()
                    self.q1.add(info["process"])

            elif not self.q1.isEmpty():
                if self.q1.isInterrupted():
                    validCycle = False
                    info = self.q1.pop()
                    self.io.add((info["process"],1,info["quantum"]))

                elif not self.q1.timeOut():
                    pid = self.q1.run()
                    if pid != None:
                        self.log.append(str(pid) + " q1")

                elif self.q1.timeOut():
                    validCycle = False
                    print "timeOut 2"
                    info = self.q1.pop()
                    self.q2.add(info["process"])

            elif not self.q2.isEmpty():
                if self.q2.isInterrupted():
                    validCycle = False
                    proc = self.q2.pop()
                    self.io.add((proc,2,0))
                
                else:
                    pid = self.q2.run()
                    if pid != None:
                        self.log.append(str(pid) + " q2")

            if (not self.io.isEmpty()) and validCycle:
                self.io.run()
                if self.io.finishedIO():
                    info = self.io.pop()
                    if info[1] == 0:
                        self.q0.returnQueue(info[0],info[2])
                    elif info[1] == 1:
                        self.q1.returnQueue(info[0],info[2])
                    else:
                        self.q2.returnQueue(info[0])
            elif not validCycle:
                validCycle = True
        i = 0
        for elem in self.log:
            i += 1
            print str(i) + " " + elem

c = [{"time":40, "kind":"IO"}, {"time":20, "kind":"CPU"}]
b = [{"time":40, "kind":"CPU"}, {"time":20, "kind":"IO"}, {"time":40, "kind":"CPU"}]
a = [{"time":40, "kind":"CPU"}]

teste = Schedule([{"pid":1, "timeLine":c}],[],[])
teste.run()

# if __name__ == "__main__":
#   import argparse
#   parser = argparse.ArgumentParser(description='Calcula o diagram de Gantt para uma dada configuracao inicial de processos')

#   parser.add_argument('file', metavar='file', nargs='1',help='Arquivo csv com os dados de entrada')

# 	if args.file:
# 		with open(filename, 'rb') as f:
# 			reader = csv.reader(f)
# 			try:
# 				reader.next()
# 				for row in reader:
# 						process_record(row)
# 			except csv.Error as e:
# 				print >> sys.stderr, 'Error on file %s, line %d: %s' % (filename, reader.line_num, e)
# 	else:
# 		parser.print_help()
