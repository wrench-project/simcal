[![Build][build-badge]][build-link]
[![License: LGPL v3][license-badge]](LICENSE)

# About
Simcal is a simulation calibration framework for calibrating arbitrary simulators using arbitrary optimization algorithms.

Simcal provides a `Simulator` wrapper that provides a standardized way to invoke an arbitrary simulator.  This wrapper takes a set of parameter values that instantiate the simulator's behavior, invokes the instantiated simulator one one or more input, and then returns a value that represents the simulation accuracy/quality that was achieved using these parameter values.  This value is typically based on some notion of loss when compared to some ground-truth data (the details of which are left to the implementer).

Simcal also provides a `Calibrator` class that can be used to calibrate a simulator using some optimization algorithm.  A `Calibrator` is expected to call a `Simulator` wrapper several times with different parameter values and return the parameter values that lead to the best results (lowest loss).  A calibrator is provided specifications that, for each `Parameter`, define a type, a value range, and  a distribution.

Additionally Simcal provides helpful utilities, such as an `Environment` for managing temporary files and command-line invocations, and a `Coordinator` for managing parallelism.


# Installation instructions

This package can be installed using `pip install .`.
Alternatively, you can set it manually up in a virtual environment using the `setup.sh` script.

# Example Usage
The `examples/` directory contains examples simulators and calibrators for these simulators. A complete walkthrough is provided in [examples/walkthrough/walkthrough.md](examples/walkthrough/walkthrough.md), and can be downloaded as an [interactive jupyter notebook](examples/walkthrough/walkthrough.ipynb).
