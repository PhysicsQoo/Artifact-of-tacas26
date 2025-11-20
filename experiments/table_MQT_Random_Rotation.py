
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
output_file_name = 'Table_MQT_Random_Rotation_'+datetime.now().strftime("NO%Y%m%d%H%M%S")+'.csv'
output_file = os.path.join(output_file_path, output_file_name)
if not os.path.exists(output_file_path):
    os.makedirs(output_file_path)
tools_switch = {
    'Hybrid': True, #QuPRS
    'RR': False,
    'WMC': True,
    'qcec': True, #qcec
    'qk': True, #quokka_sharp
}
fieldnames = ["Benchmark_Name",'q','G','G2']
for tool in tools_switch.keys():
    if tools_switch[tool]:
        fieldnames.append(tool+'_time')
        fieldnames.append(tool+'_result')

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

path1 = "../benchmarks/MQTBench/"
path2 = "../benchmarks/MQTBench/h,ry,rz,cx/"

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
    if tools_switch['Hybrid'] or tools_switch['RR']:
        progress_bar.set_description(f'Hybrid ({file_name})')

        QuPRS_result = check_equivalence(circuit1, circuit2, method = "hybrid", strategy='Proportional', timeout=timeout)

        results["Hybrid_time"] = QuPRS_result.verification_time
        results["Hybrid_result"] = QuPRS_result.equivalent
        if tools_switch['RR']:
            results["RR_time"] = QuPRS_result.pathsum_time
            if QuPRS_result.to_DIMACS_time is None:
                results["RR_result"] = QuPRS_result.equivalent
            else:
                results["RR_result"] = "unknown"
    if tools_switch['WMC']:
        progress_bar.set_description(f'WMC ({file_name})')
        QuPRS_result = check_equivalence(circuit1, circuit2, method = "wmc_only", strategy='Proportional', timeout=timeout)
        results["WMC_time"] = QuPRS_result.verification_time
        results["WMC_result"] = QuPRS_result.equivalent

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
    

    '''qcec part''' 
    if tools_switch['qcec']:
        from mqt import qcec
        def qcec_verify_process(queue, circuit1, circuit2):
            try:
                result = qcec.verify(circuit1, circuit2).equivalence.__str__()
                queue.put(result)
            except Exception as e:
                queue.put(str(e))

        # Example usage
        progress_bar.set_description(f'qcec ({file_name})')
        qcec_result, qcec_time = safe_verify(qcec_verify_process, circuit1, circuit2, timeout=timeout)
        if qcec_result == 'equivalent':
            results["qcec_result"] = 'equivalent'
        elif qcec_result == 'equivalent_up_to_global_phase':
            results["qcec_result"] = 'equivalent*'
        elif qcec_result == 'not_equivalent':
            results["qcec_result"] = 'not_equivalent'
        else:
            results["qcec_result"] = qcec_result
        results["qcec_time"] = qcec_time

    '''quokka_sharp part'''
    if tools_switch['qk']:
        os.environ['QUOKKA_CONFIG'] = "./config.json"
        import quokka_sharp as qk
        
        def qk_verify_process(queue, circuit1, circuit2):
            basis = "comp"
            try:
                # Parse the circuit
                circuit1 = qk.encoding.QASMparser(circuit1, True)
                # Parse another circuit
                circuit2 = qk.encoding.QASMparser(circuit2, True)
                # Get (circuit1)^dagger(circuit2)
                circuit2.dagger()
                circuit1.append(circuit2)
                # Get CNF for the merged circuit (for computational base instaed of cliffordt, use `computational_basis = True`)
                cnf = qk.encoding.QASM2CNF(circuit1, computational_basis = (basis == "comp"))
                # "id" or "2n"
                res = qk.CheckEquivalence(cnf, check = "cyclic" if (basis == "comp") else "linear", N = 1 if (basis == "comp") else 4)
                queue.put(res)
            except FileNotFoundError:
                res = "FILE_NOT_FOUND"
                queue.put(res)
            except Exception as e:
                queue.put(str(e))

        # Example usage
        progress_bar.set_description(f'quokka_sharp ({file_name})')
        qk_result, qk_time = safe_verify(qk_verify_process, circuit1, circuit2, timeout=timeout)
        if qk_result == True:
            results["qk_result"] = 'equivalent*'
        elif qk_result == False:
            results["qk_result"] = 'not_equivalent'
        else:
            results["qk_result"] = qk_result
        results["qk_time"] = qk_time

    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(results)
print('All benchmarks completed.')
