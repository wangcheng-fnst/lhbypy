import bt_test.run_strategy as rs
import sys

def main(argv):
    strategy = argv[1]
    rs.run_test(strategy)

if __name__ == "__main__":
  main(sys.argv)