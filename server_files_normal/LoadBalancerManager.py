import socket
import threading

class LoadBalancerManager(threading.Thread):
	"""Handles the interactions with the load-balancing server"""
