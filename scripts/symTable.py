import numpy as np
from math import sqrt

typesAvailable = ['uniform', 'uniform_bin', 'uniform_equitable']

def binarySymbolTable(n, kind): # n = table_size
	table = []
	if kind == "uniform":
		mult = float(256) / n
		for i in range(n):
			table.append((int(mult * i), int(mult * i), int(mult * i)))

	elif kind == "uniform_bin":
		div = 255 ** 3 / n
		table = [(div * i / (255 ** 2), (div * i / 255) % 255, (div * i) % 255) for i in xrange(n)]

	elif kind == "uniform_equitable":
		div = int(n ** 0.3333) # cube root
		for a in range(div + 1):
		  for b in range(div + 1):
		    for c in range(div + 1):
		      table.append((255 / div * a, 255 / div * b, 255 / div * c))

	return table

def decodeSymbol(symbol, table):
	min_dist = 99999999
	closest_term = -1
	for idx,term in enumerate(table):
		dist = 0
		for i in range(len(term)):
			dist += (symbol[i] - term[i]) ** 2
		if dist < min_dist:
			min_dist = dist
			closest_term = idx

	assert(closest_term != -1)
	return closest_term
