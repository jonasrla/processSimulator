from processSimulator import Schedule
from processSimulator import Process

queues = [
    [Process(1, burst=80, ios=1)],
    [Process(1, burst=80, ios=1), Process(2, 40), Process(3, 20, 4)],
    [Process(1, burst=10), Process(2, burst=5, ios=4), Process(3, burst=30, ios=1)],
]

# 150 2
# {'burst': 150, 'IO': 2}
# {'time': 50, 'kind': 'CPU'}, {'time': 20, 'kind': 'IO'}, {'time': 50, 'kind': 'CPU'}, {'time': 20, 'kind': 'IO'}, {'time': 50, 'kind': 'CPU'}

for i, queue in enumerate(queues):
    print '# Example', i + 1
    teste = Schedule(queue)
    teste.run()
    print
