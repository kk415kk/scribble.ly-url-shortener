"""Convert user visits from separate lines to the same line, so they can be
processed by MapReduce/mrjob.

This program takes a CSV data file and outputs a new CSV data file with the
user ID appended to each Vote/Visit.  Run like so:

    python combine_all_info.py data/anonymous-msweb.data > data/all_info_msweb.data
"""
    
import csv
import fileinput
from sys import stdout


def csv_readline(line):
    """Given a sting CSV line, return a list of strings."""
    for row in csv.reader([line]):
        return row


def main():
    """This function iterates through an input file linearly, keeping track of
    the current user.  When we see a Vote/Visit line, we append the current
    user to the cell.  Then we write all lines out again (updated or not).
    """

    csv_writer = csv.writer(stdout)
    current_user = None
    vroot_to_title_urls = {}

    for line in fileinput.input():
        cell = csv_readline(line)
        if cell[0] == 'A':
            vroot_to_title_urls[cell[1]] = (cell[3], cell[4])
        elif cell[0] == 'C':
            ###
            # FILL IN by replacing below:
            current_user = cell[1]
            continue
            # What should we update when we see a new 'C' row?
            ##/
        elif cell[0] == 'V':
            ###
            # FILL IN by replacing below:
            cell.append(current_user)
            extra_info = vroot_to_title_urls.get(cell[1], (None, None))
            cell.append(extra_info[0])
            cell.append(extra_info[1])
            # What should we update when we see a new 'V' row?
            ##/

        csv_writer.writerow(cell)


if __name__ == '__main__':
    main()
