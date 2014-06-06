#TODO put a license header


class Queue(object):
    def __init__(self, proc_list=[]):
        self.queue = proc_list

    def add(self, proc):
        self.queue.append(proc)

    def pop(self):
        return self.queue.pop(0)

    def isEmpty(self):
        return len(self.queue) == 0

    def run(self):
        raise NotImplementedError('Abstract method')

    def peek(self):
        return self.queue[0]


class Process(object):
    def __init__(self, pid, burst, ios=0):
        self.pid = pid

        t_cpu = [burst / (ios + 1)] * (ios + 1)
        t_cpu[-1] += burst % (ios + 1)
        t_io = [20] * ios

        self.timeline = []
        i_cpu = iter(t_cpu)
        i_io = iter(t_io)
        while True:
            try:
                #XXX: i_io will stop after i_cpu
                self.timeline.append({'time': i_cpu.next(), 'kind': 'CPU'})
                self.timeline.append({'time': i_io.next(), 'kind': 'IO'})
            except StopIteration:
                break

        self.inIO = (self.timeline[0]["kind"] == "IO")
        self.isOver = False

    def work(self):
        if not self.inIO:
            self.timeline[0]["time"] -= 1
            if self.timeline[0]["time"] == 0:
                if len(self.timeline) == 1:
                    self.isOver = True

                else:
                    self.inIO = True
                    self.timeline.pop(0)
        else:
            raise Exception("Executando CPU em IO")

    def readWrite(self):
        if self.inIO:
            self.timeline[0]["time"] -= 1
            if self.timeline[0]["time"] == 0:
                if len(self.timeline) == 1:
                    self.isOver = True

                else:
                    self.inIO = False
                    self.timeline.pop(0)
        else:
            raise Exception("Executando IO em CPU")

    def isInterrupted(self):
        return self.inIO

    def checkIO(self):
        return not self.inIO

    # def isOver(self):
    #     return self.isOver


class RoundRobin(Queue):
    def __init__(self, quantum, proc_list=[]):
        Queue.__init__(self, proc_list)
        for proc in proc_list:
            proc.quantum = quantum
        self.quantum = quantum

    def add(self, proc):
        proc.quantum = self.quantum
        super(RoundRobin, self).add(proc)

    def returnQueue(self, proc, remainingQuantum):
        proc.quantum = remainingQuantum
        super(RoundRobin, self).add(proc)

    def run(self):
        # print "run len(" + str(len(self.queue)) + ") " + str(self.quantum)
        pid = self.queue[0].pid
        if (not self.queue[0].isInterrupted()):
            self.queue[0].work()
            self.queue[0].quantum -= 1
            #print self.queue[0].quantum
            if (self.queue[0].isOver):
                self.pop()
            return pid

    def timeOut(self):
        return self.queue[0].quantum == 0

    def isInterrupted(self):
        return self.queue[0].isInterrupted()


class IO(Queue):
    def run(self):
        proc = self.peek()
        self.queue[0].readWrite()
        return proc.pid

    def finishedIO(self):
        return self.queue[0].checkIO()


class FCFS(Queue):
    def run(self):
        print "run len(" + str(len(self.queue)) + ") " + "fcfs"
        pid = self.queue[0].pid
        if (not self.queue[0].isInterrupted()):
            self.queue[0].work()
            if self.queue[0].isOver:
                self.queue.pop(0)
            return pid

    def isInterrupted(self):
        return self.queue[0].isInterrupted()


class Schedule(object):
    def __init__(self, listaq0=[], listaq1=[], listaq2=[]):
        self.q0 = RoundRobin(10, listaq0)
        self.q1 = RoundRobin(20, listaq1)
        self.q2 = FCFS(listaq2)
        self.io = IO()
        self._log = []
        self.t = 0

    def isOver(self):
        return self.q0.isEmpty() and self.q1.isEmpty() and self.q2.isEmpty() and self.io.isEmpty()

    def log(self, msg, time_passed=True):
        self._log.append((self.t, msg))
        if time_passed:
            self.t += 1

    def run(self):
        validCycle = True
        while not self.isOver():
            cpuCycle = False

            if not self.q0.isEmpty():
                if self.q0.isInterrupted():
                    validCycle = False
                    self.io.add(self.q0.pop())

                elif not self.q0.timeOut():
                    pid = self.q0.run()
                    if pid is not None:
                        self.log(str(pid) + " q0")
                        cpuCycle = True

                elif self.q0.timeOut():
                    validCycle = False
                    print "timeOut 1"
                    self.q1.add(self.q0.pop())

            elif not self.q1.isEmpty():
                if self.q1.isInterrupted():
                    validCycle = False
                    self.io.add(self.q1.pop())

                elif not self.q1.timeOut():
                    pid = self.q1.run()
                    if pid is not None:
                        self.log(str(pid) + " q1")
                        cpuCycle = True

                elif self.q1.timeOut():
                    validCycle = False
                    print "timeOut 2"
                    self.q2.add(self.q1.pop())

            elif not self.q2.isEmpty():
                if self.q2.isInterrupted():
                    validCycle = False
                    proc = self.q2.pop()
                    self.io.add(proc)

                else:
                    pid = self.q2.run()
                    if pid is not None:
                        self.log(str(pid) + " q2")
                        cpuCycle = True

            if (not self.io.isEmpty()) and validCycle:
                pid = self.io.run()
                if self.io.finishedIO():
                    self.q0.add(self.io.pop())
                self.log(str(pid) + " io", time_passed=not cpuCycle)

            elif not validCycle:
                validCycle = True

        for t, msg in self._log:
            print t, msg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Calcula o diagram de Gantt para uma dada configuracao inicial de processos')

    parser.add_argument('file', metavar='file', nargs='1', help='Arquivo csv com os dados de entrada')

    if args.file:
        with open(args.file, 'r') as f:
            timeline = []
            for line in f:
                burst, ios = map(int, line.split())
                proc = {'burst': burst, 'IO': ios}
                timeline.append(proc)
            schedule = Schedule(timeline)
    else:
        parser.print_help()
