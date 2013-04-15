Python CSV Operations
=====

csvop is a python script that defines several common
high-level operations for CSV (comma-separated value) files,
like adding and removing columns, splitting, and merging.

This library was written so that a few simple but important
transformations could be performed on CSV files without resorting
to Excel, which is not always respectful of data format and character
encoding. Unlike Excel, this library leaves all of the data 
as it found it, as much as possible.

```bash
# Create output.csv from input.csv, with column 3 removed.
# Columns are always 0-indexed.
csvop.py dropcolumn input.csv output.csv -i 3

# Create output.csv from columns 3 through 7 of input.csv.
csvop.py select input.csv output.csv --from 3 --to 7
```

Commands read and write in a stream rather than a batch, so 
separate input and output files must be specified.

If output would overwrite an existing file, it will be confirmed.
If you would like to override the confirmation (i.e. for use
in a script) you can add the `--yes` flag before the command:

```bash
csvop.py --yes addcolumn input.csv output.csv --name "Total" --default 0
```

For detailed help, use the `--help` flag. For help on individual commands, specify which command:
```bash
csvop.py addcolumn --help
```

Operations
-----

Each operation has different arguments and options.

### Add a column

Use `addcolumn` to add a column to a table. By default, the column 
will have no name, no default value, and is added as the last column.

Examples:
```bash
# Add a "Total" column filled with zeros at the end of the table
csvop.py addcolumn input.csv output.csv --name "Total" --default 0

# Insert a completely empty column at position 3 (0-indexed)
csvop.py addcolumn input.csv output.csv --index 3
```

### Remove a column

Use `dropcolumn` to remove a column from a table. Either a column
name or a column index must be specified.

Examples:
```bash
# Remove the column called "Total"
csvop.py dropcolumn input.csv output.csv --name "Total"

# Remove the column at position 3 (0-indexed)
csvop.py dropcolumn input.csv output.csv --index 3
```

### Merge two tables

Use `merge` to combine two tables vertically, in a simple 
row-by-row join-like operation. This command requires a pair
of input CSV files, one to be placed on the left and one on the right.

By default, the output will have as many rows as the longer file. 
Add the `--stop-shorter` flag to stop writing when the shorter file runs 
out of rows.

No matching of id values is performed, so make sure that rows correspond in both
input files.

Examples:
```bash
# Merge a table of phone numbers with a table of addresses
csvop.py merge phones.csv addresses.csv combined.csv
```

### Select columns

Use `select` to choose a range of columns from the input file
that will be included in the output file. Ranges
are specified by index. By default, the starting index is 0
and the stopping index is the final column in the input file.

Examples:
```bash
# Select all but the first row from the input file
csvop.py select input.csv output.csv --from 1

# Select columns 4-7 from the input file
csvop.py select input.csv output.csv --from 4 --to 7
```

License
-----

This code is open sourced under the MIT License.
