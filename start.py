import sys
import multiprocessing
from run import runweb

def worker(port):
	server = runweb.AppUno()
	server.start(port = port)

if __name__ == '__main__':
	jobs = []
	ports = [8081]
	for port in ports:
		p = multiprocessing.Process(target=worker, args=(port,))
		jobs.append(p)
		p.start()
