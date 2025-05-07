import os
from IPython import get_ipython


def is_running_in_jupyter():
    try:
        get_ipython()
        return True
    except NameError:
        return False


if is_running_in_jupyter():
    print("Running in a Jupyter Notebook (.ipynb)")
else:
    print("Running as a Python script (.py)")
