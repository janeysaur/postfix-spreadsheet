# Code structure
Simple-ish python script with a main method that parses the input csv file and then evaluates each cell in the "spreadsheet" and prints the output one row at a time

Algorithm for evaluating the postfix expressions is basically copied from wikipedia, with the only addition being the need to evaluate cell references.

All helper methods are pure functions.

# Limitations
* ~~This implementation assumes cell references are a single letter followed by a single number~~
* Does not detect circular references ...
* Doesn't store any previously calculated cell values / references
* Have taken some shortcuts here and there, and relied on throwing/catching of exceptions
instead of properly validating input data etc
* Haven't added much test data beyond the examples given; the first things that came to mind were divide by zero error and circular references. Pretty much trusting that the algorithm from wikipedia is correct.
