[![Build][build-badge]][build-link]
[![License: LGPL v3][license-badge]](LICENSE)

# About
Simcal is a Simulation Calibration framework that provides a simple way to use multiple calibration algorithms on an arbitrary simulator.

Simcal provides a wrapper for arbitrary simulators so they may be used by arbitrary calibration algorithms.  Similarly it provides wrappers for calibrators so any optimization algorithm can be used as a calibrator.  These calibrators use a unified Parameter set.

It also provides some utilities to aid calibration such as a parallelism Coordinator wrapper and a simulation Environment.

# Installation instructions
This package can be installed using `pip install .`.
Alternatively, you can set it manually up in a virtual environment using the `setup.sh` script.

# Example Usage
The examples directory contains some examples of how to use the framework.  For a more in-dept walkthrough see [examples/walkthrough/walkthrough.html](examples/walkthrough/walkthrough.html) or download the [interactive jupyter notebook](examples/walkthrough/walkthrough.ipynb).
