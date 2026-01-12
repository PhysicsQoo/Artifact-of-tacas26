
import csv, os, re, time, signal, subprocess, psutil

from datetime import datetime
from tqdm import tqdm
from multiprocessing import Process, Queue
from qiskit import qasm2

from datetime import datetime
from QuPRS.interface.load_qiskit import load_circuit
from QuPRS import check_equivalence
def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")  
signal.signal(signal.SIGALRM, timeout_handler)

timeout = 200
tolerance = 1e-10
output_file_path = '../Results/'
output_file_name = 'Table_Feynman_'+datetime.now().strftime("NO%Y%m%d%H%M%S")+'.csv'
output_file = os.path.join(output_file_path, output_file_name)
if not os.path.exists(output_file_path):
    os.makedirs(output_file_path)
tools_switch = {
    'RR': True,
    'feynver': True, #feynman
}
fieldnames = ["Benchmark_Name",'q','G','G2']
for tool in tools_switch.keys():
    if tools_switch[tool]:
        fieldnames.append(tool+'_time')
        fieldnames.append(tool+'_result')

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

path1 = "../benchmarks/Feynman/"
path2 = "../benchmarks/Feynman/h,y,z,t,tdg,cx/"


files =os.listdir(path1)
files = list(filter(lambda x: x.endswith('.qasm'), files))

def natural_key(filename):
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', filename)]

files = sorted(files, key=natural_key)
progress_bar = tqdm(files)
for file in progress_bar:
    results = {}

    circuit1 = load_circuit(path1+file)
    circuit2 = load_circuit(path2+file)
    file_name = file.replace('.qasm', '')
    results["Benchmark_Name"] = file_name
    results["q"] = circuit1.num_qubits
    results["G"] = len(circuit1.data)
    results["G2"] = len(circuit2.data)
    
    '''QuPRS part'''
    if tools_switch['RR']:
        progress_bar.set_description(f'RR ({file_name})')
        QuPRS_result = check_equivalence(circuit1, circuit2, method = "reduction_rules", strategy='Proportional', timeout=timeout)

        if tools_switch['RR']:
            results["RR_time"] = QuPRS_result.pathsum_time
            if QuPRS_result.to_DIMACS_time is None:
                results["RR_result"] = QuPRS_result.equivalent
            else:
                results["RR_result"] = "unknown"

    qasm2.dump(circuit1, 'circuit1.qasm')
    qasm2.dump(circuit2, 'circuit2.qasm')
    circuit1 = 'circuit1.qasm'
    circuit2 = 'circuit2.qasm'
    def safe_verify(func, circuit1, circuit2, timeout):
        start_time = time.time()
        queue = Queue()
        process = Process(target=func, args=(queue, circuit1, circuit2))
        worker_pid = process.pid
        process.start()
        process.join(timeout)
        if process.is_alive():
            try:
                parent = psutil.Process(worker_pid)
                # Get all descendant processes (recursive=True)
                children = parent.children(recursive=True)
                
                progress_bar.set_description(f"Found children of PID {worker_pid}: {[child.pid for child in children]}")

                # 1. Try to gracefully terminate descendant processes (e.g., gpmc)
                for child in children:
                    try:
                        progress_bar.set_description(f"Attempting to terminate child process PID: {child.pid} (Name: {child.name()})")
                        child.terminate() # Send SIGTERM
                    except psutil.NoSuchProcess:
                        progress_bar.set_description(f"Child process PID: {child.pid} already terminated.")
                    except Exception as e:
                        progress_bar.set_description(f"Error terminating child process PID: {child.pid}: {e}")
                
                # Wait for descendant processes to exit
                gone, alive = psutil.wait_procs(children, timeout=3) # Wait 3 seconds
                
                # 2. Force kill any remaining alive descendant processes
                for p in alive:
                    try:
                        progress_bar.set_description(f"Child process PID: {p.pid} (Name: {p.name()}) did not terminate gracefully, killing.")
                        p.kill() # Send SIGKILL
                    except psutil.NoSuchProcess:
                        progress_bar.set_description(f"Child process PID: {p.pid} was already terminated before kill.")
                    except Exception as e:
                        progress_bar.set_description(f"Error killing child process PID: {p.pid}: {e}")

                # 3. Terminate the main worker process (qk_verify_process)
                progress_bar.set_description(f"Attempting to terminate main worker process PID: {worker_pid}")
                process.terminate() # Send SIGTERM to worker process
                process.join(timeout=5) # Wait for worker process to exit

                if process.is_alive():
                    progress_bar.set_description(f"Main worker process PID: {worker_pid} did not terminate after SIGTERM, killing.")
                    process.kill() # Python 3.7+, send SIGKILL
                    process.join() # Wait for it to fully exit
                
                progress_bar.set_description(f"Worker process PID: {worker_pid} and its children have been handled after timeout.")

            except psutil.NoSuchProcess:
                # worker_pid may have already exited before we try to handle it with psutil
                progress_bar.set_description(f"Worker process PID: {worker_pid} already terminated before advanced cleanup.")
                # Ensure multiprocessing.Process object is cleaned up
                if process.is_alive(): # Double check, just in case
                    process.kill()
                process.join() # Ensure join is called
            except Exception as e:
                progress_bar.set_description(f"An error occurred during termination of PID {worker_pid} or its children: {e}")
                # As a last resort, if worker process is still alive, kill it
                if process.is_alive():
                    progress_bar.set_description(f"Fallback: Forcibly killing worker process PID: {worker_pid}")
                    process.kill()
                    process.join()
            
            return "Timeout", f">{timeout}" 
        result = queue.get() if not queue.empty() else "no result"
        process.join()
        process_time = round(time.time() - start_time, 3)
        return result, process_time
    
    '''feymann part'''
    if tools_switch['feynver']:
        from QuPRS.interface.qasm2qc import convert_qasm_to_qc
        progress_bar.set_description(f'feynver ({file_name})')        

        qc_file = file.replace('.qasm', '.qc')
        circuit1_qc = path1+qc_file
        circuit2_qc = path2+qc_file

        def feynver_verify_process(queue, circuit1, circuit2):
            try:
                process = subprocess.run(['./feynver', circuit1, circuit2], capture_output=True, text=True)
                queue.put(process.stdout)
            except Exception as e:
                queue.put(str(e))
        feynver_result, feynver_time = safe_verify(feynver_verify_process, circuit1_qc, circuit2_qc, timeout=timeout)
        if feynver_result.startswith("Equal"):
            results["feynver_result"] = 'equivalent'
        elif feynver_result.startswith("Not equal"):
            results["feynver_result"] = 'not_equivalent'
        else:
            results["feynver_result"] = feynver_result
        results["feynver_time"] = feynver_time 


    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(results)
print('All benchmarks completed.')
