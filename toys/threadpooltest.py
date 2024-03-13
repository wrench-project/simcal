import concurrent.futures
import subprocess
import threading
futures=[]

def run_command(command):
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	if process.returncode != 0:
		print(f"Error executing command '{command}': {stderr.decode()}")
	else:
		print(f"Command '{command}' executed successfully")

# Define the commands to execute
commands = ["sleep 1", "sleep 2", "sleep 3", "sleep 4", "sleep 1", "sleep 2", "sleep 3", "sleep 4", "sleep 1", "sleep 2", "sleep 3", "sleep 4", "sleep 1", "sleep 2", "sleep 3", "sleep 4"]

# Create a ThreadPoolExecutor with 	 threads
handles=[]
pool_size=8
pool_full=threading.Condition()
managementLock=threading.Lock()
ready=[]
def foo(arg):
	with managementLock:
		cache = [handle for handle in handles if handle.done()]
		##print(cache)
		for handle in cache:
			ready.append(handle)
			handles.remove(handle)
		with pool_full:
			pool_full.notify()
def safeLen(array):
	with managementLock:
		return len(array)
def allocate(cmd):
	
	while safeLen(handles) >= pool_size:	
		with pool_full:	
			pool_full.wait()
	handle = executor.submit(run_command, cmd)
	handle.add_done_callback(foo)
	with managementLock:
		handles.append(handle)
	return handle
	
def collect():
	global ready
	ret = []
	with managementLock:
		#print(ready)
		#print(handles)
		for handle in ready:
			ret.append(handle.result())
		ready = []
	return ret
with concurrent.futures.ThreadPoolExecutor(max_workers=	pool_size) as executor:
	# Submit each command to be executed in parallel
	
	for command in commands:
		allocate(command)
		print("collecting")
		collect()
