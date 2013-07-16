import cssr_interface

L_val = 20

# prefix = 'sample-60s-'
prefix = 'sample'
user   = '1'

fname = '{}{}'.format(prefix, user)

cssr_interface.run_CSSR(filename = fname, L = L_val, savefiles = True, showdot = True, is_multiline = False, showCSSRoutput = False)