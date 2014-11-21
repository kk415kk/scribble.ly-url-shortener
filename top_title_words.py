"""
To run:
    python top_title_words.py data/anonymous-msweb.data
To store output:
    python top_title_words.py data/anonymous-msweb.data > results/top_title_words.out
"""

from mrjob.job import MRJob
from combine_user_visits import csv_readline

class CommonTitles(MRJob):

    def mapper(self, line_no, line):
        cell = csv_readline(line)
        if cell[0] == 'A':
            words = cell[3].split(" ")
            for word in words:
              yield word.lower(), 1

    def reducer(self, word, counts):
        yield word, sum(counts)
        
if __name__ == '__main__':
    CommonTitles.run()
