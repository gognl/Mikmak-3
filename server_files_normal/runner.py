#  Used to run multiple clients
#  Not needed in final version of course

from multiprocessing import Process
from server_files_normal.main import main as server_main
from typing import Final

SERVERS_AMOUNT: Final[int] = 2


def main():
	procs = []
	for i in range(SERVERS_AMOUNT):
		proc = Process(target=server_main, args=(i,))
		proc.start()
		procs.append(proc)
		print(f'Started server {i}')

	for proc in procs:
		proc.join()


if __name__ == '__main__':
	main()
