"""
Library for manipulating data structures.
"""


def inverse_stack(stack, remove_function_name) -> list:
    """
    Helper function to inverse a stack.

    :param stack: stack
    :param remove_function_name: function name to remove top item
    :return: inverted stack
    """
    inverted_stack = list()
    while len(stack) > 0:
        inverted_stack.append(getattr(stack, remove_function_name)())
    return inverted_stack
