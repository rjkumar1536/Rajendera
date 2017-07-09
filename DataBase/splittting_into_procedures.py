import re
import os
import sys

write_location="C:/splitting/NewFiles"
read_location="C:/Users/gilla.shivani/Downloads/DumpSPandFunc.sql"

def main(argv):
	global filename
	if(len(argv) == 2):
		write_location=argv[0]
		read_location=argv[1]		
	else:
		write_location="C:/splitting/NewFiles"
		read_location="C:/Users/gilla.shivani/Downloads/DumpSPandFunc.sql"		
	a='PROCEDURE'
	b='('
	filename=""
	with open(read_location,'r') as in_f:
		copy_mode=False
		flag=0
		for line in in_f:
			if not copy_mode:
				if line.startswith('DELIMITER ;;'):
					first_line=line
					copy_mode=True
					flag=1
			elif line.startswith('DELIMITER ;'):
				copy_mode=False
				with open(file_name,'ab')as w_f:
						w_f.write("DELIMITER ;")
			elif copy_mode==True:
				if flag==1:
					s=line
					file_name=write_location+'/'+s.split(a)[-1].split(b)[0][2:-1]+".sql"
					with open(file_name,'ab')as w_f:
						w_f.write("DELIMITER ;;")
					flag=0
				with open(file_name,'ab')as w_f:
					w_f.write(line)


if __name__ == '__main__':
	main(sys.argv[1:])