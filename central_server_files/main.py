import threading
from collections import deque

import LB
import login
from structures import *


def main():
	new_clients_q: deque[Client] = deque()
	msgs_to_clients_q: deque[MsgToClient] = deque()

	threads: list[threading.Thread] = []

	LB_Thread = threading.Thread(target=LB.LB_main, args=(new_clients_q, msgs_to_clients_q))
	threads.append(LB_Thread)

	login_Thread = threading.Thread(target=login.login_main, args=(new_clients_q, msgs_to_clients_q))
	threads.append(login_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()


if __name__ == '__main__':
	main()
