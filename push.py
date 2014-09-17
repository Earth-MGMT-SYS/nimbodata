import os
import sys

def main(argv):
	
  # GRUNT: RUN TESTS
  try:
    os.system("grunt");
  except:
    print "TESTS HAVE ERRORS... FIX BEFORE PUSHING"
    sys.exit()
  
  #HG COMMIT/PUSH
  try:
    os.system('hg commit -m "%s"' % str(argv[1]))
  except:
    print "COULD NOT PUSH TO REMOTE REPOSITORY"

if __name__ == '__main__':
  import sys
  main(sys.argv)	
