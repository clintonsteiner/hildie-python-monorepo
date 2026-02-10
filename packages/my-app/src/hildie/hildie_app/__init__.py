"""An application that uses the shared library."""

__version__ = "0.1.0"

from hildie.hildie_library import add, multiply


def process_numbers(numbers: list[int]) -> dict[str, int]:
    """Process a list of numbers using library functions.

    Args:
        numbers: List of integers to process

    Returns:
        Dictionary with sum and product of all numbers
    """
    if not numbers:
        return {"sum": 0, "product": 0}

    total = 0
    for num in numbers:
        total = add(total, num)

    product = 1
    for num in numbers:
        product = multiply(product, num)

    return {"sum": total, "product": product}
