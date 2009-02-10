#!/usr/bin/python
def main():
	from optparse import OptionParser
	import sys, logging
	sys.path.append("/dk/work/sweetpotato")
	from sweetpotato.core import Task, SweetPotato
	usage = "%prog [options] target"
	parser = OptionParser(usage=usage, version="sweetpotato 0.0.1")
	parser.add_option("-f","--file",default="plan.yaml",
		help="build file [default: %default]")
	parser.add_option("-l","--list", action="store_true", help="list targets")
	parser.add_option("-a","--list-all", action="store_true", help="list all targets")
	parser.add_option("-T",dest="tokens", metavar="TOKEN=VALUE", action="append", 
		help="set build token")
	parser.add_option("-L","--log-level", type="choice",
			help="error, warning, info [default], debug",
			choices=['error','warning','info','debug'],
			default='info')
	(options, args) = parser.parse_args()
	if 1 > len(args):
		parser.error("target missing")
	sweetpotato = SweetPotato(options)
	for target in args:
		sweetpotato.run(target)
		sweetpotato.log('PLAN FINISHED\n')
if "__main__" ==  __name__:
	main()
