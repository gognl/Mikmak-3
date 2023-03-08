#  Used to run multiple clients
#  Not needed in final version of course

from multiprocessing import Process
from client_files.code.main import main as client_main
from typing import Final

CLIENTS_AMOUNT: Final[int] = 200


def main():
	procs = []
	for i in range(CLIENTS_AMOUNT):
		proc = Process(target=client_main)
		proc.start()
		procs.append(proc)
		print(f'Started client {i}')

	for proc in procs:
		proc.join()


if __name__ == '__main__':
	main()
