# con-sched-grid

This set of scripts will ingest a schedule listing (exported, for example, from https://github.com/olszowka/Zambia) and export HTML files containing a schedule
grid formatted as tables.

*Requires* Python 3. I am not making the feeblest attempt at continuing to be backwards-compatible with Python 2.

To run, execute the main script using Python 3, i.e.:
`python3 main.py`
Currently the path to the input file is hard-coded as `example-data/pocketprogram.csv` and no command-line switches are supported. (To be improved in future
enhancements.) 
The script will create a set of HTML files in the current directory, containing the output. *On a Macintosh*, the script will cause these to be opened with your
default browser.

Note: At this point, if you wish to print the result (as opposed to *just* viewing in a browser), use Chrome. I'm using the non-standard CSS attribute
`-webkit-print-color-adjust: exact; ` and I've only tried this in Chrome.
