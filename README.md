# Artifact for TACAS'26: Equivalence Checking of Quantum Circuits via Path-Sum and Weighted Model Counting

## 1. Introduction
This artifact accompanies the paper **"Equivalence Checking of Quantum Circuits via Path-Sum and Weighted Model Counting"** submitted to TACAS 2026. It contains the [QuPRS](https://github.com/PhysicsQoo/QuPRS) source code, benchmark suites, and experimental scripts necessary to reproduce the empirical results presented in the paper (specifically Tables 2 and 3, and Figure 3). The primary objective of this artifact is to validate the correctness of the proposed methodology and facilitate the reproducibility of the experimental evaluation. While the functional correctness of the results is expected to match the paper, exact execution times may vary depending on the underlying hardware and system environment.

## 2. Setup and Installation

We provide a Docker image to ensure a consistent execution environment. The artifact can be deployed using a pre-built image from Docker Hub.

### 2.1 Prerequisites
Ensure that Docker is installed and the daemon is running. Installation instructions can be found in the [official Docker documentation](https://docs.docker.com/get-started/get-docker/).

### 2.2 Obtaining the Artifact

####  Pull from Docker Hub 

```bash
docker pull physicsqoo/tacas26
```
The source code building this artifact is from this [Repository](https://github.com/PhysicsQoo/Artifact-of-tacas26).

**⚠️ Important Note:** This artifact is optimized for Linux (amd64). Running it on Apple Silicon (M1/M2/M3) via Docker Desktop may trigger a crash (`rosetta error: mmap_anonymous_rw mmap failed`) due to incompatibilities with Rosetta 2 emulation.



### 2.3 Execution
Launch an interactive container instance using the image obtained above:

```bash
docker run -it physicsqoo/tacas26
```
This command initializes an isolated shell environment with all dependencies pre-configured.

### 2.4 Verification
To verify the installation and ensure the tool functions correctly, execute the unit test suite:
- **Estimated Time**: < 1 minute
```bash
pytest
```
If all tests pass, the tool is correctly installed.
## 3. Experimental Evaluation

The following steps describe how to reproduce the experimental data reported in the paper.

<!-- ### 3.1 Overview & Time Estimates
The reproduction is divided into three parts. The estimated times below are based on an Azure Standard E8ads v5 instance (8 vCPUs, 64 GiB RAM).

| Script | Corresponds to | Estimated Time | Complexity|
| :--- | :--- | :--- |  :--- | 
| `python table_Feynman.py` | Figure 3(a) | ~30 mins | Low|
| `python table_MQT.py` | Table 2, Fig 3(b), Table 3(a) | ~2 hours | Medium|
| `python table_MQT_Random_Rotation.py` | Table 3(b) | ~3 hours | High (Many timeouts)|
     -->
### 3.1 Reproduction Steps
Navigate to the experiments directory within the container:
```bash
cd experiments/
```
Execute the reproduction scripts corresponding to the specific tables and figures:
```bash
# 1. Reproduces data for Table 2, Figure 3(b), and Table 3(a) 
python table_MQT.py

# 2. Reproduces data for Table 3(b) 
python table_MQT_Random_Rotation.py

# 3. Reproduces data for Figure 3(a) 
python table_Feynman.py

```

### 3.3 Results Analysis & Export
Upon completion, the generated data will be stored in the `Results` directory in CSV format with timestamps (e.g., `Table_MQT_NOYYYYMMDDHHMMSS.csv`).

**Exporting Results to Host**: To copy the results from the container to your local machine for analysis, open a new terminal and run:
```bash
# 1. Find your Container ID
docker ps

# 2. Copy the Results folder (replace <CONTAINER_ID> with your actual ID)
docker cp <CONTAINER_ID>:/app/Results/ ./Local_Results/
```

## 4. Experimental Setup & Performance Baseline
**Baseline Hardware (Paper Results):**
All results reported in the paper were conducted on the following environment:
* **Instance Type:** Microsoft Azure Standard E8ads v5
* **CPU:** 8 vCPUs (AMD EPYC™ 7763v, 3rd Gen Milan)
* **Memory:** 64 GiB
* **OS:** Linux Ubuntu

**Reproducibility Expectations:**

* **Correctness (Strict Match):**
    The logical outcomes (e.g., equivalence/non-equivalence verdicts) are deterministic and should **strictly match** the results reported in the paper, regardless of the hardware.

* **Memory Usage & OOMs:**
    Full reproduction requires significant memory. If running on a machine with limited RAM (< 16GB), **Out-of-Memory (OOM) errors** on memory-intensive benchmarks are expected. This reflects hardware constraints, not a defect in the tool.

* **Runtimes & Timeouts:**
    Absolute execution times will deviate from the published results due to CPU differences and **virtualization overhead** (especially on Docker for macOS/Windows). Slower machines may experience increased timeouts on hard instances.