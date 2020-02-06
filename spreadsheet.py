import csv
import re
import sys

CELL_ERROR = '#ERR'
OPERATORS = ['+', '-', '*', '/']

def main(argv):
    try:
        input_file_path = argv[0]
    except IndexError:
        print 'usage: spreadsheet.py <inputfile>'
        sys.exit()

    data = []

    # read input
    with open(input_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            data.append(row)

    # evaluate and print output
    for row, row_data in enumerate(data, start=1):
        results = []
        for i in range(0, len(row_data)):
            col = chr(ord('a') + i) # map 0, 1, 2,... to 'a', 'b', 'c',...
            cell_ref = '{}{}'.format(col, row)
            try:
                result = evaluate_cell(data, cell_ref)
                # Slight hack to match output format of '1' vs '1.0'
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                result = str(result)
            except Exception as e:
                # raise e
                result = CELL_ERROR
            results.append(result)
        print ','.join(results)


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
def evaluate_cell(data, ref):
    # type: (Dict[Dict[str]], str) -> float

    stack = []
    expression = get_cell(data, ref)
    tokens = expression.lower().split() # split() splits on whitespace by default
    for token in tokens:
        if token in OPERATORS:
            operand2 = stack.pop()
            operand1 = stack.pop()
            # Note: for this problem, we are only handling a few binary operators
            stack.append(evaluate_operation(operand1, operand2, token))
        elif token == ref:
            raise Exception('Self-referential cell found')
        else:
            stack.append(evaluate_operand(data, token))

    if len(stack) == 1:
        result = stack.pop()
        # print('{} = {}'.format(expression, result))
        return result

    raise Exception('Invalid expression in cell: {}'.format(ref))


def get_cell(data, ref):
    # type: (Dict[Dict[str]], str) -> str

    '''
    Assumes that cell references are one or more letters followed by one or more digits
    '''
    matches = re.match(r"^([^\W\d_-]+)(\d+)$", ref)
    if matches:
        col = ord(matches.group(1).lower()) - ord('a')
        row = int(matches.group(2)) - 1
        return data[row][col]

    raise Exception("Invalid cell reference")

def evaluate_operand(data, operand):
    # type: (Dict[Dict[str]], str) -> float

    '''
    Assumes operands are either a number or a cell reference
    '''

    # Naive regex to match "numerical" inputs like:
    # positive/negative whole/decimal numbers OR exponentials
    # e.g. 1, -1, 0.9, -1.1, -1.0E+1
    if re.match(r"-?\d+", operand):
        return float(operand)

    # probably a cell reference
    return evaluate_cell(data, operand)


def evaluate_operation(operand1, operand2, operator):
    # type: (float, float, str) -> float

    if operator == '+':
        return operand1 + operand2
    if operator == '-':
        return operand1 - operand2
    if operator == '*':
        return operand1 * operand2
    if operator == '/':
        return operand1 / operand2
    raise Exception('Invalid operator found')


if __name__ == "__main__":
   main(sys.argv[1:])