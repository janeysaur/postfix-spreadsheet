import csv
import re
import sys

CELL_ERROR = '#ERR'
OPERATORS = ['+', '-', '*', '/']

class SpreadsheetException(Exception):
    pass

def main(argv):
    try:
        input_file_path = argv[0]
    except IndexError:
        print('usage: spreadsheet.py <input_file>')
        sys.exit()

    # read input
    data = []
    with open(input_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            data.append(row)

    # Hidden "option" for debugging purposes
    include_reason = len(argv) > 1 and argv[1] == '-v'
    results = evaluate_spreadsheet(data, include_reason)
    output_csv(results)


def output_csv(data):
    # type: (Dict[Dict[str]]) -> None
    for row in data:
        print(','.join(row))


def evaluate_spreadsheet(data, include_reason=False):
    # type: (Dict[Dict[str]]) -> Dict[Dict[str]]

    def value_to_string(value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value)) # to format 1.0 as '1'
        return str(value)

    evaluated_data = []
    for row_index, row_data in enumerate(data, start=0):
        evaluated_row = []
        for col_index, expression in enumerate(row_data, start=0):
            cell_ref = map_location_to_cell_ref(row_index, col_index)
            try:
                value = evaluate_postfix_expression(data, expression, [cell_ref])
                evaluated_row.append(value_to_string(value))
            except SpreadsheetException as e:
                evaluated_row.append(
                    '{} ({})'.format(CELL_ERROR, e.message) if include_reason else CELL_ERROR
                )
        evaluated_data.append(evaluated_row)

    return evaluated_data


def map_location_to_cell_ref(row_index, col_index):
    # type: (int, int) -> str

    # map [0, 1, 2, ...] => [a, b, c, ...]
    col_letter = chr(ord('a') + col_index)

    # map [0, 1, 2, ...] => [1, 2, 3, ...]
    row_number = row_index + 1

    return '{}{}'.format(col_letter, row_number)


'''
Adapted from https://en.wikipedia.org/wiki/Reverse_Polish_notation#Postfix_evaluation_algorithm

    for each token in the postfix expression:
        if token is an operator:
            operand_2 <= pop from the stack
            operand_1 <= pop from the stack
            result <= evaluate token with operand_1 and operand_2
            push result back onto the stack
        else if token is an operand:
            push token onto the stack
    result <= pop from the stack
'''
def evaluate_postfix_expression(data, expression, cell_references):
    # type: (Dict[Dict[str]], str, List[str]) -> float

    stack = []
    tokens = expression.lower().split() # split() splits on whitespace by default
    for token in tokens:
        if token in OPERATORS:
            try:
                operand2 = stack.pop()
                operand1 = stack.pop()
            except IndexError:
                raise SpreadsheetException('Invalid expression: not enough operands for operator')

            # Note: for this problem, we are only handling a few binary operators
            stack.append(evaluate_operation(operand1, operand2, token))
        else:
            stack.append(evaluate_operand(data, token, cell_references))

    if len(stack) == 1:
        result = stack.pop()
        return result

    raise SpreadsheetException('Invalid expression')


def evaluate_operation(operand1, operand2, operator):
    # type: (float, float, str) -> float

    if operator == '+':
        return operand1 + operand2
    if operator == '-':
        return operand1 - operand2
    if operator == '*':
        return operand1 * operand2
    if operator == '/':
        try:
            return operand1 / operand2
        except ZeroDivisionError:
            raise SpreadsheetException('Division by zero')

    raise SpreadsheetException('Invalid operator found')


def evaluate_operand(data, operand, cell_references):
    # type: (Dict[Dict[str]], str, List[str]) -> float

    '''
    Assumes operands are either a number or a cell reference
    '''

    # Check if this might be a circular reference
    if operand in cell_references:
        raise SpreadsheetException(
            'Circular reference found: {}'.format(' => '.join(cell_references + [operand]))
        )

    # Naive regex to match "numerical" inputs like:
    # positive/negative whole/decimal numbers OR exponentials
    # e.g. 1, -1, 0.9, -1.1, -1.0E+1
    if re.match(r"-?\d+", operand):
        return float(operand)

    # else should be a cell reference
    (row_index, col_index) = map_cell_ref_to_location(operand)
    try:
        expression = data[row_index][col_index]
    except IndexError:
        raise SpreadsheetException('Reference to empty cell')

    return evaluate_postfix_expression(data, expression, cell_references + [operand])


def map_cell_ref_to_location(cell_ref):
     # type: (str) -> (int, int)

    '''
    Cell references follow LETTER NUMBER notation
    '''

    matches = re.match(r"^([a-z]+)([1-9][0-9]*)$", cell_ref.lower())
    if matches:
        row_index = int(matches.group(2)) - 1

        if len(matches.group(1)) > 1:
            # TODO: handle columns past Z, e.g. as in Excel/Sheets where:
            # * AA => column 27
            # * AB => column 28
            raise SpreadsheetException('Not implemented: Non-single letter cell references')

        col_index = ord(matches.group(1)) - ord('a')
        return (row_index, col_index)

    raise SpreadsheetException("Invalid cell reference")


if __name__ == "__main__":
   main(sys.argv[1:])