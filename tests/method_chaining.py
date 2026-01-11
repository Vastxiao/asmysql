"""
Method chaining example in Python

This example demonstrates how to implement method chaining in Python.
Method chaining is a technique that allows multiple method calls on the same object
to be chained together, improving code readability and reducing intermediate variables.
"""

from typing import Any, Dict, List


class QueryBuilder:
    """
    A simple example of method chaining for building SQL queries.
    Each method returns self to enable chaining.
    """

    def __init__(self):
        self._query_parts: List[str] = []
        self._params: List[Any] = []
        self._table: str = ""
        self._conditions: List[str] = []
        self._order_by: str = ""
        self._limit_count: int = 0

    def select(self, *columns: str) -> "QueryBuilder":
        """
        Add SELECT clause to the query

        Args:
            *columns: Column names to select

        Returns:
            QueryBuilder: Returns self for chaining
        """
        if columns:
            columns_str = ", ".join(columns)
        else:
            columns_str = "*"
        self._query_parts.append(f"SELECT {columns_str}")
        return self

    def from_table(self, table: str) -> "QueryBuilder":
        """
        Add FROM clause to the query

        Args:
            table: Table name

        Returns:
            QueryBuilder: Returns self for chaining
        """
        self._table = table
        self._query_parts.append(f"FROM {table}")
        return self

    def where(self, condition: str, *params) -> "QueryBuilder":
        """
        Add WHERE clause to the query

        Args:
            condition: Condition string with placeholders
            *params: Parameters to substitute in condition

        Returns:
            QueryBuilder: Returns self for chaining
        """
        self._conditions.append(condition)
        self._params.extend(params)
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        """
        Add ORDER BY clause to the query

        Args:
            column: Column to order by
            direction: Sort direction (ASC or DESC)

        Returns:
            QueryBuilder: Returns self for chaining
        """
        self._order_by = f"ORDER BY {column} {direction}"
        return self

    def limit(self, count: int) -> "QueryBuilder":
        """
        Add LIMIT clause to the query

        Args:
            count: Maximum number of rows to return

        Returns:
            QueryBuilder: Returns self for chaining
        """
        self._limit_count = count
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the final query and parameters

        Returns:
            Dict[str, Any]: Dictionary containing query string and parameters
        """
        query_parts = self._query_parts.copy()

        if self._conditions:
            where_clause = " AND ".join(f"({cond})" for cond in self._conditions)
            query_parts.append(f"WHERE {where_clause}")

        if self._order_by:
            query_parts.append(self._order_by)

        if self._limit_count > 0:
            query_parts.append(f"LIMIT {self._limit_count}")

        query = " ".join(query_parts)
        return {"query": query, "params": self._params.copy()}

    def __str__(self) -> str:
        """
        String representation of the built query
        """
        result = self.build()
        return f"Query: {result['query']}\nParams: {result['params']}"


class FluentCalculator:
    """
    A calculator that supports method chaining for mathematical operations
    """

    def __init__(self, initial_value: float = 0):
        self._value = initial_value

    def add(self, number: float) -> "FluentCalculator":
        """
        Add a number to the current value

        Args:
            number: Number to add

        Returns:
            FluentCalculator: Returns self for chaining
        """
        self._value += number
        return self

    def subtract(self, number: float) -> "FluentCalculator":
        """
        Subtract a number from the current value

        Args:
            number: Number to subtract

        Returns:
            FluentCalculator: Returns self for chaining
        """
        self._value -= number
        return self

    def multiply(self, number: float) -> "FluentCalculator":
        """
        Multiply the current value by a number

        Args:
            number: Number to multiply by

        Returns:
            FluentCalculator: Returns self for chaining
        """
        self._value *= number
        return self

    def divide(self, number: float) -> "FluentCalculator":
        """
        Divide the current value by a number

        Args:
            number: Number to divide by

        Returns:
            FluentCalculator: Returns self for chaining

        Raises:
            ZeroDivisionError: If attempting to divide by zero
        """
        if number == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        self._value /= number
        return self

    @property
    def result(self) -> float:
        """
        Get the current result

        Returns:
            float: Current calculated value
        """
        return self._value

    def reset(self, value: float = 0) -> "FluentCalculator":
        """
        Reset the calculator to a new value

        Args:
            value: New initial value

        Returns:
            FluentCalculator: Returns self for chaining
        """
        self._value = value
        return self

    def __str__(self) -> str:
        return f"Result: {self._value}"


# Example usage
if __name__ == "__main__":
    # Example 1: Query Builder
    print("=== Query Builder Example ===")
    query_builder = QueryBuilder()

    # Chaining method calls to build a query
    result = (
        query_builder.select("id", "name", "email")
        .from_table("users")
        .where("age > %s", 18)
        .where("status = %s", "active")
        .order_by("name")
        .limit(10)
        .build()
    )

    print("Built query:")
    print(result["query"])
    print("Parameters:", result["params"])
    print()

    # Alternative way to build the same query
    print("=== Alternative Query Building ===")
    query_builder2 = QueryBuilder()
    query_builder2.select("id", "name", "email")
    query_builder2.from_table("users")
    query_builder2.where("age > %s", 18)
    query_builder2.where("status = %s", "active")
    query_builder2.order_by("name")
    query_builder2.limit(10)

    print(query_builder2)
    print()

    # Example 2: Fluent Calculator
    print("=== Fluent Calculator Example ===")
    calc = FluentCalculator(10)

    # Chaining mathematical operations
    result = calc.add(5).multiply(2).subtract(3).divide(2).result
    print(f"((10 + 5) * 2 - 3) / 2 = {result}")

    # Another calculation
    calc.reset(100).subtract(20).divide(4).add(5)
    print(f"((100 - 20) / 4) + 5 = {calc.result}")
    print(calc)
