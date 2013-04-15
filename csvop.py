#!/usr/bin/env python
"""
A script for performing high-level CSV file operations.
"""
__author__ = "Michael Brooks"
__copyright__ = "Copyright 2013, Michael Brooks"
__license__ = "MIT"

import csv
import argparse
import os
import itertools

def col_reference(header, name=None, index=None):
    """Get the index of a column given a name or index
    
    >>> col_reference(['a', 'b', 'c'], None, 2)
    (None, 2)
    >>> col_reference(['a', 'b', 'c'], 'a', None)
    ('a', 0)
    >>> col_reference(['a', 'b', 'c'], 'b', 2)
    ('b', 1)
    """
    if name is not None:            
        index = header.index(name)
    else:
        index = index
        
    return name, index

def map_list(val_list):
    """Create a dictionary from list values to list indices.
    
    >>> m = map_list(['a', 'b', 'c'])
    >>> m['a']
    0
    >>> m['b']
    1
    >>> m['c']
    2
    >>> len(m)
    3
    """
    return {col: i for i, col in enumerate(val_list)}

## http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation/
override_confirm = False
def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.
    """
    
    if override_confirm:
        return True
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False
    
def write_csv(iterator, filename, header=None, generator=None):
    """Go through each row of the iterator writing to the given filename.
    
    If header is supplied, it is inserted prior to processing the rows.
    
    If a generator is supplied, it is used to process each row before output.
    """
    if os.path.isfile(filename):
        if not confirm("Overwrite %s?" %(filename)):
            return

    rowsWritten = 0
    colCount = 0
    with open(filename, 'wb') as outfile:
        writer = csv.writer(outfile)
        
        if header is not None:
            if generator is not None:
                header = generator(rowsWritten, header)

            colCount = len(header)
            writer.writerow(header)
            rowsWritten += 1
        
        for row in iterator:
            if generator is not None:
                row = generator(rowsWritten, row)
            
            if not colCount:
                colCount = len(row)
                
            writer.writerow(row)
            rowsWritten += 1
            
    print 'Wrote %d rows and %d columns to %s' %(rowsWritten, colCount, filename)
    
def addcolumn(args):
    """Add a column with an optional name and default value at a specific index"""
    with open(args.input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        # need first row for indexing
        header = reader.next()
        
        # figure out where we are adding the column
        index = len(header)
        if args.index is not None:
            index = args.index
        
        # what goes in the cells?
        cellval = ''
        if args.default is not None:
            cellval = args.default
        
        # what goes in the header? by default same as cells
        colname = cellval
        if args.name is not None:
            colname = args.name
        
        print 'Adding column "%s" at index %d with default value "%s"' %(colname, index, cellval)
        
        def output(rowNum, row):
            if rowNum == 0:
                # it is the header
                row.insert(index, colname)
            else:
                row.insert(index, cellval)
            return row
        
        write_csv(reader, args.output, header=header, generator=output)
            
def dropcolumn(args):
    """Remove a column with a given name or index"""
    with open(args.input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        header = reader.next()
        name, index = col_reference(header, args.name, args.index)
        
        if name:
            print 'Dropping column "%s" at index %d' %(name, index)
        else:
            print 'Dropping column at index %d' %(index)
        
        def output(rowNum, row):
            row.pop(index)
            return row
        
        write_csv(reader, args.output, header=header, generator=output)

def merge(args):
    """Combine two tables by adjoining their rows in order"""
    with open(args.left, 'rbU') as left, open(args.right, 'rbU') as right:
        leftReader = csv.reader(left)
        rightReader = csv.reader(right)
        
        def output(rowNum, rows):
            leftRow = [] if rows[0] is None else rows[0]
            rightRow = [] if rows[1] is None else rows[1]
                
            leftRow.extend(rightRow)
            
            return leftRow
            
        iterator = itertools.izip(leftReader, rightReader)
        write_csv(iterator, args.output, generator=output)
        
def select(args):
    """Select a subset of the columns by index range"""
    with open(args.input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        header = reader.next()
        fromIndex = 0 if args.from_ is None else args.from_
        toIndex = len(header) if args.to is None else args.to
        
        print 'Selecting columns %d through %d' %(fromIndex, toIndex - 1)
        
        def output(rowNum, row):
            return row[fromIndex:toIndex]
            
        write_csv(reader, args.output, header=header, generator=output)
        
if __name__ == '__main__':
    # create the top-level parser
    parser = argparse.ArgumentParser(description="Perform operations on CSV files")
    parser.add_argument('--yes', action='store_true', help='Answer yes to all prompts')
    subparsers = parser.add_subparsers(metavar="COMMAND")
    
    # create the parser for the "addcolumn" command
    addcolumn_parser = subparsers.add_parser('addcolumn', help='insert a column')
    addcolumn_parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    addcolumn_parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    addcolumn_parser.add_argument('--index', '-i', type=int, help='The index to insert the column (last by default)', required=False)
    addcolumn_parser.add_argument('--name', '-n', help='The name of the column to add (none by default)', required=False)
    addcolumn_parser.add_argument('--default', '-d', help='The default cell value', required=False)
    addcolumn_parser.set_defaults(func=addcolumn)

    # create the parser for the "dropcolumn" command
    dropcolumn_parser = subparsers.add_parser('dropcolumn', help='remove a column')
    dropcolumn_parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    dropcolumn_parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    dropcolumn_group = dropcolumn_parser.add_mutually_exclusive_group(required=True)
    dropcolumn_group.add_argument('--name', '-n', help='The name of the column to remove')
    dropcolumn_group.add_argument('--index', '-i', type=int, help='The position of the column to remove (0-indexed)')
    dropcolumn_parser.set_defaults(func=dropcolumn)

    merge_parser = subparsers.add_parser('merge', help='vertically merge two tables')
    merge_parser.add_argument('left', metavar="LEFT_INPUT_CSV", help='The left input csv table')
    merge_parser.add_argument('right', metavar="RIGHT_INPUT_CSV", help='A right input csv table')
    merge_parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    merge_parser.add_argument('--stop-shorter', action='store_true', help='Stop whenever the shorter file ends', required=False)
    merge_parser.set_defaults(func=merge)
    
    select_parser = subparsers.add_parser('select', help='select columns from a table, by index')
    select_parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    select_parser.add_argument('output', metavar="RIGHT_OUTPUT_CSV", help='A csv file to write the right columns to')
    select_parser.add_argument('--from', dest="from_", metavar="FROM_INDEX", type=int, help='The column to start with (default 0)')
    select_parser.add_argument('--to', metavar="TO_INDEX", type=int, help='The column to end with, inclusive (default last)')
    select_parser.set_defaults(func=select)
    
    args = parser.parse_args()
    
    if args.yes:
        override_confirm = True
    
    args.func(args)
