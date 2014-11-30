"""
To run:
    python top_title_words.py data/anonymous-msweb.data
To store output:
    python top_title_words.py data/anonymous-msweb.data > results/top_title_words.out
"""

from mrjob.job import MRJob
from combine_user_visits import csv_readline
WRITE_FILE = "results/top_title_words.out"

class CommonTitles(MRJob):

    def mapper(self, line_no, line):
        cell = csv_readline(line)
        if cell[0] == 'A':
            words = cell[3].split(" ")
            for word in words:
              yield word.lower(), 1

    def reducer(self, word, counts):
        yield word, sum(counts)
        
def get_top_10():
    lines = []
    top_results = []

    with open(WRITE_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        text = line.split('\t')
        word = text[0]
        count = text[-1][:-1]
        top_results.append((word, count))

    top_results = sorted(top_results, key=lambda x: int(x[1]), reverse=True)[:10]
    print_results(top_results)

def print_results(results):
    # Clear the file first
    with open(WRITE_FILE, 'w') as f:
        f.write("")

    # Then write to the file
    for r in results:
        s = r[0] + " " + r[1]
        print s

if __name__ == '__main__':
    CommonTitles.run()
    get_top_10()
