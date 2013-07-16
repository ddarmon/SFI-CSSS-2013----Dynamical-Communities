ofile = open('adj_mat.txt')

wfile = open('network.dot', 'w')

wfile.write('digraph  {\nsize = "6,8.5";\nratio = "fill";\nnode [shape = circle];\nnode [fontsize = 24];\nedge [fontsize = 24];')

ofile.readline()

line = ofile.readline()

while line != '':
	lsplit = line.split(',')
	from_id = lsplit[0].rstrip(' ')
	to_id = lsplit[1].rstrip(' ')
	weight = lsplit[2].rstrip('\n')

	wfile.write('{} -> {} [label = "{}"];\n'.format(from_id, to_id, weight))

	line = ofile.readline()

wfile.write('}')

ofile.close()
wfile.close()