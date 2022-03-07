import bt_test.run_strategy as rs
import sys

def main(argv):
    strategy = argv[0]
    print(strategy)
    rs.run_test(strategy)

if __name__ == "__main__":
  main(sys.argv)