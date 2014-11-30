"""
To run:
    python top_users.py data/user-visits_msweb.data
To store output:
    python top_users.py data/user-visits_msweb.data > results/top_users.out
"""

from mrjob.job import MRJob
from combine_user_visits import csv_readline

class TopVisitors(MRJob):

    def mapper(self, line_no, line):
        cell = csv_readline(line)
        if cell[0] == 'V':
          yield cell[3], 1

    def reducer(self, uid, counts):
        total = sum(counts)
        if total > 20:
          yield uid, total
        
if __name__ == '__main__':
    TopVisitors.run()
