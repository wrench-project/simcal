[![Build][build-badge]][build-link]
[![License: LGPL v3][license-badge]](LICENSE)

# About
Simcal is a simulation calibration framework for calibrating arbitrary simulators using arbitrary optimization algorithms.

Simcal provides a `Simulator` wrapper that provides a standardized way for a calibrator to call an arbitrary simulator.  This wrapper takes a parameter to run the simulator with, and then returns a value representing the quality of that set of parameters.  Generally this is based on the loss compared to some Ground-truth data, but the details are left to the implementer.

Simcal also provides a `Calibrator` class that can be used to implement a calibration algorithm.  This Calibrator is expected to call the provided `Simulator` several times with different parameter values and return the parameters with the best simulator quality (lowest loss).  Calibrators are expected to use the provided Parameter to determine the range and distribution for each parameter to provide to the `Simulator`.

Additionally simcal provides helpful utilities for parallelizing the calibration process such as an `Environment` for managing temporary files and a `Coordinator` for managing parallelism.


# Installation instructions
This package can be installed using `pip install .`.
Alternatively, you can set it manually up in a virtual environment using the `setup.sh` script.

# Example Usage
The examples directory contains some examples of how to use the framework.  For a more in-dept walkthrough see [examples/walkthrough/walkthrough.md](examples/walkthrough/walkthrough.md) or download the [interactive jupyter notebook](examples/walkthrough/walkthrough.ipynb).
