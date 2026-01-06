# Artifact for TACAS'26: Equivalence Checking of Quantum Circuits via Path-Sum and Weighted Model Counting

## 1. Introduction
This artifact accompanies the paper **"Equivalence Checking of Quantum Circuits via Path-Sum and Weighted Model Counting"** submitted to TACAS 2026. It contains the source code, benchmark suites, and experimental scripts necessary to reproduce the empirical results presented in the paper (specifically Tables 2 and 3, and Figure 3). The primary objective of this artifact is to validate the correctness of the proposed methodology and facilitate the reproducibility of the experimental evaluation. While the functional correctness of the results is expected to match the paper, exact execution times may vary depending on the underlying hardware and system environment.

## 2. Setup and Installation

We provide a Docker image to ensure a consistent execution environment. The artifact can be deployed using a pre-built image from Docker Hub or Zenodo (recommended for reproducibility), or by building the image locally from the source.

### 2.1 Prerequisites
Ensure that Docker is installed and the daemon is running. Installation instructions can be found in the [official Docker documentation](https://docs.docker.com/get-started/get-docker/).

### 2.2 Obtaining the Artifact
We provide three methods to obtain the artifact. **Option A is recommended** for most reviewers due to download speed.

#### Option A: Pull from Docker Hub (Recommended for Review)
This is the fastest way to get the environment running.
```bash
docker pull physicsqoo/tacas26
docker tag physicsqoo/tacas26 tacas26
```

#### Option B: Load Pre-built Image
This image is hosted on Zenodo (DOI: 10.5281/zenodo.18158735) and is cryptographically guaranteed to match the submitted version. Use this if strict archival verification is required or if Docker Hub is inaccessible.
```bash
wget "https://zenodo.org/records/18158735/files/tacas26.tar.gz?download=1" -O tacas26.tar.gz
docker load -i tacas26.tar.gz
```

#### Option C: Build from Source (Linux x86_64 Only)
**⚠️ Important Note:** This artifact is designed for **Linux (x86_64/amd64)** environments. While Docker Desktop on macOS (Apple Silicon) allows emulation (via Rosetta/QEMU), building this artifact locally on macOS often fails or stalls due to emulation overheads during dependency solving.

```bash
git clone https://github.com/PhysicsQoo/Artifact-of-tacas26.git
cd Artifact-of-tacas26
docker build --platform linux/amd64 -t tacas26 .
```

### 2.3 Execution
Launch an interactive container instance using the image obtained above:
```bash
docker run -it tacas26
```
This command initializes an isolated shell environment with all dependencies pre-configured.

### 2.4 Verification
To verify the installation and ensure the tool functions correctly, execute the unit test suite:
```bash
pytest
```

## 3. Experimental Evaluation

The following steps describe how to reproduce the experimental data reported in the paper.

### 3.1 Reproduction Steps
1.  Navigate to the experiments directory within the container:
    ```bash
    cd experiments/
    ```
2.  Execute the reproduction scripts corresponding to the specific tables and figures:
    ```bash
    # Reproduces data for Table 2, Figure 3(b), and Table 3(a)
    python table_MQT.py
    
    # Reproduces data for Figure 3(a)
    python table_Feynman.py
    
    # Reproduces data for Table 3(b)
    python table_MQT_Random_Rotation.py
    ```

### 3.2 Results Analysis
Upon completion, the generated data will be stored in the `Results` directory:
```bash
cd ../Results/
```
Output files are generated in CSV format with timestamps (e.g., `Table_MQT_NOYYYYMMDDHHMMSS.csv`).

### 4. Experimental Setup & Performance Baseline
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