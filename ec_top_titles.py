"""
To run:

    python ec_top_titles.py data/all_info_msweb.data

To store output:

    python ec_top_titles.py data/all_info_msweb.data > results/ec_top_titles.out
"""

from mrjob.job import MRJob
from combine_user_visits import csv_readline
WRITE_FILE = "results/ec_top_titles.out"

class TopTitlesEC(MRJob):

    def mapper(self, line_no, line):
        cell = csv_readline(line)
        if cell[0] == 'V':
            yield cell[4], 1

    def reducer(self, title, visit_counts):
        total = sum(visit_counts)
        yield title, total 

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

    top_results = sorted(top_results[:10], key=lambda x: int(x[1]), reverse=True)
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
    TopTitlesEC.run()
    get_top_10()
