"""CLI interface for the monorepo application."""

import click

from hildie.hildie_library import add, multiply


@click.group()
def cli():
    """A CLI tool for mathematical operations."""


@cli.command()
@click.argument("a", type=int)
@click.argument("b", type=int)
def add_numbers(a, b):
    """Add two numbers together."""
    result = add(a, b)
    click.echo(f"{a} + {b} = {result}")


@cli.command()
@click.argument("a", type=int)
@click.argument("b", type=int)
def multiply_numbers(a, b):
    """Multiply two numbers together."""
    result = multiply(a, b)
    click.echo(f"{a} x {b} = {result}")


@cli.command()
@click.argument("numbers", type=int, nargs=-1, required=True)
def sum_all(numbers):
    """Sum all provided numbers."""
    result = 0
    for num in numbers:
        result = add(result, num)
    click.echo(f"Sum: {result}")


@cli.command()
@click.argument("numbers", type=int, nargs=-1, required=True)
def multiply_all(numbers):
    """Multiply all provided numbers together."""
    result = 1
    for num in numbers:
        result = multiply(result, num)
    click.echo(f"Product: {result}")


if __name__ == "__main__":
    cli()
