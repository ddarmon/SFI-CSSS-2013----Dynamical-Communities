ofile = open('nMIs.txt')

for line in ofile:
	link, nMI, link_type, uid1, uid2, username1, username2 = line.strip().split()

	print '{} & {} & {} \\\\'.format(username1, username2, nMI)