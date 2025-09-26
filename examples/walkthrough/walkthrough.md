# Simcal
Simcal is a simulation calibration framework designed to calibrate arbitrary simulators.  The simulator itself is defined outside of simcal and can be anything.  For the purposes of this walkthrough, we will assume the simulator is some other program that can be invoked from the command line and outputs a value.

Simcal provides a Simulation wrapper that must be implemented to call this simulator.  This wrapper must return a scalar value representing the loss of the calibration.  It is helpful (but not required) for the loss to be implemented as it own seperate function.

The sklearn.metrics package provides many useful error functions that can be used as the loss function.  For this example, we will use `mean_squared_error`.


```python
from sklearn.metrics import mean_squared_error as sklearn_mean_squared_error
import simcal as sc
```

# Ground-Truth data
Simcal has no expectation for your ground-truth data.  It doesn't even assume it exists (some simulators can use some out-of-band source to quantify accuracy).

However, for most simulators, ground-truth data is needed for calibration.  We recommend this data be stored in a well-structured directory of multiple scenarios and contain both the required arguments for the simulator to run a scenario and the expected output of a scenario.

Example Dir:
* ground_truth
	+ single_machine
		- 10_tasks_0_data.json
		- 10_tasks_10_data.json
		- 10_tasks_100_data.json
		- 100_tasks_0_data.json
		- 100_tasks_10_data.json
		- 100_tasks_100_data.json
	+ two_machine
		- ...
	+ four_machine
		- ...

Example 10_tasks_100_data.json:
```json
{
	"makespan":10s,
	"tasks":10,
	"data":100
}
```
This organized data is then loaded into a well structured data structure

Example:
```json
{
	"single_machine":{
		"10_tasks_0_data":{
			"makespan":10s,
			"tasks":10,
			"data":0
		},...
	},
	"two_machine":{
		...
	},
	"four_machine":{
		...
	}
}
```
we assume `ground_truth_loader(path)` produces such a structure



```python
ground_truth=ground_truth_loader("path/to/ground_truth")
```

# Simulator
Simcal provides an abstract `Simulator` class to extend for creating the wrapper.  The `run` method of this wrapper must have the signature  `run(self, env, args)` and return a scalar value.  The ``__call__`` method is reserved.  Otherwise the implementation of this class is up to the user.  For this example, we will define a simulator that takes the path to the simulator, a reference ground-truth dataset, and a functor to evaluate the loss.  The `run` function will run all scenarios given in `ground_truth`, and then compute the loss over them.  The `run` function will be provided, in the `args` parameter, with a dictionary of formated parameter values to use.



```python
class ExampleSimulator(sc.Simulator):
    def __init__(self, simulator_path, ground_truth, loss):
        self.simulator_path = simulator_path
        self.ground_truth = ground_truth
        self.loss = loss
    # Assume args is
    # {
    #     "network_speed":ParameterValue,
    #     "cpu_speed":ParameterValue
    # }
    def run(self, env, args):
        result=[]
        makespans=[]
        for machine_count in self.ground_truth:
            for scenario in self.ground_truth[machine_count]:
                gtdata = self.ground_truth[machine_count][scenario]
                std_out, std_err, exit_code = env.bash(self.simulator_path,
                                                       "--tasks",gtdata["tasks"],
                                                       "--data",gtdata["data"], 
                                                       "--network",args["network_speed"],
                                                       "--cpu",args["cpu_speed"])
                if std_err: # This if is not required, but is helpful for debugging simulators, beware of printing large outputs
                    print(gtdata, std_out, std_err, exit_code)
                    raise Exception(f"Error running simulator") # any normal exception raised in the run function will cause the calibration process to stop
                resutls.add(float(std_dout))
                makespans.add(parse_united_float(gtdata["makespan"]))
        return self.loss(makespan,results)

simulator = ExampleSimulator("path/to/simulator",ground_truth,sklearn_mean_squared_error) 
# the simulator may be manually called
loss = simulator({"network_speed":"100Mbps", "cpu_speed":"1Gflops"})
```

`env` provides an environment unique to each invocation of `run`.  It provides many useful features such as temporary file and directory handling, as well as a bash function.  If your simulator requires input files for some of its arguments `open_file=env.tmp_file()` will create a temporary file to write it to, and if your simulator produces functions as outputs `env.tmp_dir()` will make a temporary folder for `env.bash` to use as a cwd.

# Parameter Values
Parameter Values are given to the `run` function in various formats depending on how they are configured.  Most often, they are provided as numeric values with a format in a `sc.parameter.Value`.  These support arithmetic options as if they were numbers, but will automatically attach a unit when cast to a string, jsonified, or passed to `env.bash`.  They can be used to access the base parameter distribution they originate from, if required, allowing them to carry additional metadata.


```python
parameter=sc.parameter.Value("%.1fMbps",10.0,None)# For demonstration purposes, we manually create a parameter value with a unit of Mbps, value 10, and no base parameter
print(parameter) # 10.0Mbps

parameter *= 10
print(parameter) # 100.0Mbps

print(float(parameter)) # 100.0

parameter.value = 5
print(parameter) # 5.0Mbps
```

    10.0Mbps
    100.0Mbps
    100.0
    5.0Mbps
    

# Calibrator
Simcal provides a standard calibration wrapper for various optimization algorithms to implement.
How this wrapper is instantiated is up to the algorithm implementer, but each has a 
`calibrate(self, simulator, early_stopping_loss = None, iterations = None, timelimit = None, coordinator = None)` method to compute a calibration and `add_param(self, parameter_name, parameter)` method to add parameters.

Currently Simcal provides implementations for Gradient descent, 4 Skopt baysian optimization implementations, random search, grid search, genetic algorithms, and a do-nothing "debug".


```python
random_seed=0 # Optimizers that use randomness can be seeded for reproducible results
calibrator = sc.calibrators.Debug()
calibrator = sc.calibrators.Grid()
calibrator = sc.calibrators.Random(seed=random_seed)
calibrator = sc.calibrators.ScikitOptimizer(1000,"GP",seed=random_seed) # Skopt takes a number of random samples to use before starting its Bayesian optimizer
calibrator = sc.calibrators.ScikitOptimizer(1000,"GBRT",seed=random_seed)
calibrator = sc.calibrators.ScikitOptimizer(1000,"ET",seed=random_seed)
calibrator = sc.calibrators.ScikitOptimizer(1000,"RF",seed=random_seed)
calibrator = sc.calibrators.GeneticAlgorithm(100, # Generation size
                                             10,  # Number of Breeders in each generation
                                             .50, # gene cross over rate
                                             .01, # gene mutation rate
                                             fitness_noise = None, # noise to be added to fitness, may be function (epsilon)
                                             annealing = None, # should annealing be done.  can be True for default anealing or a function (delta)
                                             seed=random_seed, 
                                             elites=0) # Number of elite members of each generation to preserve into next generation
calibrator = sc.calibrators.GradientDescent(0.1, # initial step size for calculating gradient 
                                            1,   # stop exploring if loss does not improve by at least this much each iteration
                                           early_reject_loss = None) # if the random start has a worse loss than this parameter, dont bother searching it
# the optimal value for Epsilon and delta depend on the loss and parameter ranges
```

# Parameters
To calibrate the parameters of a simulator, the parameters to calibrate and the range of values for each must be specified to the calibrator.
The `add_param(name,parameter)` function allows for adding a parameter to a calibrator.  Each parameter must have a unique name.

Simcal supports several types of parameters

* `Categorical`
Categorical parameters are sets of strings with no order.

* `Ordered`
Abstract Parameter with an order.

* `Ordinal`
Ordinal parameters are discrete sets of numeric values with order.

* `Linear`
Linear parameters are a range of values with a linear distribution, may be integer or float.

* `Exponential`
Linear parameters are a range of values with a exponential distribution, may be integer or float.

All Parameters allow for metadata to better inform the simulator how to use them.

All Parameters support a formatting string to add a unit (see Parameter Value). This can be set with `.format("formating string")`

All ordered parameters are derived from an internal range between 0 and 1 so that a step of 0.01 is "the same" for all parameters.  If you wish for one parameter to have a different step size, this internal range may be changed by setting `parameter.range_start` and `parameter.range_end`


```python
categorical = sc.parameter.Categorical(["Option 1","Option A","Option Alpha"]) 
ordinal = sc.parameter.Ordinal([1,5,10])
linear = sc.parameter.Linear(0, 20).format("%.2f") # float range from 0-20 
linear_integer = sc.parameter.Linear(0, 20, integer=True) # integer range from 0-20 
exponential = sc.parameter.Exponential(0, 20).format("%.2f") # float exponential range from 1-1048576 
exponential_integer = sc.parameter.Exponential(0, 20, integer=True) # integer exponential range from 1-1048576 

print(linear.from_normalized(0.25)) # 5.00
print(linear_integer.from_normalized(0.25)) # 5 
print(exponential.from_normalized(0.25)) # 32.00
print(exponential_integer.from_normalized(0.25)) #32

print(linear.from_normalized(0.75)) # 15.00
print(linear_integer.from_normalized(0.75)) # 15
print(exponential.from_normalized(0.75)) # 32768.00
print(exponential_integer.from_normalized(0.75)) #32768
```

    5.00
    5
    32.00
    32
    15.00
    15
    32768.00
    32768
    


```python
calibrator.add_param("network_speed",sc.parameter.Exponential(0, 20).format("%.2fbps")) 
calibrator.add_param("cpu_speed",sc.parameter.Exponential(0, 20).format("%.2fflops")) 
```

Once the calibration algorithm has been instantiated, the simulator created, and the parameters added, then the calibrator can be ran using the `calibrate` method.  This method will return the best calibration found and the corresponding loss value.  Additionally, a history of best calibrations is tracked and stored in the `calibrator.timeline` array. 


```python
calibration, loss = calibrator.calibrate(simulator, timelimit=120) # Calibrate the simulator for 2 minutes
calibrator.timeline

```

# Coordinators
To improve calibraton performance, Simcal also provides a Coordinator wrapper for parallel and distributed calibration.  Currently only the trivial default coordinator and a ThreadPool have been implemented.  This allows for optimization algorithms to use multiple CPU cores on the same machine.  A Coordinator can be passed to `calibrator.calibrate` if desired.



```python
coordinator = sc.coordinators.ThreadPool(pool_size=4)

calibration, loss = calibrator.calibrate(simulator, timelimit=120, coordinator=coordinator) # Calibrate the simulator for 2 minutes using 4 cores
```
