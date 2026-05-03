def perform_calculation(operation: str, op1: float, op2: float) -> float:
    operation = operation.lower().strip()
    if operation == "add":
        return op1 + op2
    elif operation == "subtract":
        return op1 - op2
    elif operation == "multiply":
        return op1 * op2
    elif operation == "divide":
        if op2 == 0:
            raise ValueError("Cannot divide by zero")
        return op1 / op2
    elif operation == "exponent":
        return op1 ** op2
    elif operation == "modulus":
        return op1 % op2
    else:
        raise ValueError(f"Unknown operation: {operation}")
