
"""
example.py

This is an example module for purpose of
testing sphinx documentation generation 🆗
"""


class ExampleClass:
    """
    An example class

    Attributes:
        name (str): instance name
    """

    def __init__(self, name: str):
        self.name = name

    def greet(self):
        print(f"Hello {self.name}! 🙋‍♂️")
