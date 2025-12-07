"""
Naming convention utilities
"""

import re


def to_snake_case(name: str) -> str:
    """
    Convert string to snake_case.

    Examples:
        "Customer" -> "customer"
        "CustomerOrder" -> "customer_order"
        "customer-order" -> "customer_order"
    """
    # Replace hyphens with underscores
    name = name.replace("-", "_")

    # Insert underscore before uppercase letters
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    return name


def to_pascal_case(name: str) -> str:
    """
    Convert string to PascalCase.

    Examples:
        "customer" -> "Customer"
        "customer_order" -> "CustomerOrder"
        "customer-order" -> "CustomerOrder"
    """
    # Split on underscores or hyphens
    words = re.split(r"[_\-]", name)

    # Capitalize each word
    return "".join(word.capitalize() for word in words)


def to_kebab_case(name: str) -> str:
    """
    Convert string to kebab-case.

    Examples:
        "Customer" -> "customer"
        "CustomerOrder" -> "customer-order"
        "customer_order" -> "customer-order"
    """
    # Replace underscores with hyphens
    name = name.replace("_", "-")

    # Insert hyphen before uppercase letters
    name = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()

    return name


def to_camel_case(name: str) -> str:
    """
    Convert string to camelCase.

    Examples:
        "customer" -> "customer"
        "customer_order" -> "customerOrder"
        "CustomerOrder" -> "customerOrder"
    """
    pascal = to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if pascal else ""
