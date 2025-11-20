# QUPRS Artifact-of-tacas26
## 1. Introduction
This artifact accompanies the TACAS’26 paper "Equivalence Checking of Quantum Circuits via Path‑Sum and Weighted Model Counting". It provides the code, benchmark inputs, and experiment scripts needed to reproduce the paper’s results (Tables 1–3 and Figure 3). The package is intended to validate correctness and enable reproducible experiments; exact runtimes may vary with hardware and environment.

## 2. Download, installation, and testing

- Full reproduction: run the experiment scripts described in the README to regenerate data of Tables 1–3 and Figure 3. Results should match the paper’s correctness outcomes; measured runtimes may differ across machines.
- Notes: slower machines tend to produce more timeouts; machines with limited RAM may incur more out-of-memory failures. Verify logs and error messages for troubleshooting.
### 2.1 Download and Install Docker
1. Docker: https://docs.docker.com/get-started/get-docker/ 
2. Install Docker as usual.
### 2.2 Get Docker Image and Run Container

There are two methods to obtain the Docker image and run the container:

#### Method 1: Download Pre-built Image (Recommended for Reproducibility)
1. Download the Docker image from Zenodo:
   ```bash
   wget https://zenodo.org/record/xxxxxxx/files/tacas26.tar?download=1 -O tacas26.tar
   ```
2. Load the image into Docker:
   ```bash
   docker load -i tacas26.tar
   ```

#### Method 2: Build Image from Dockerfile (For Development or Customization)
1. Clone the repository:
   ```bash
   git clone git@github.com/PhysicsQoo/Artifact-of-tacas26.git
   cd Artifact-of-tacas26
   ```
2. Build the Docker image from the Dockerfile:
   ```bash
   docker build -t tacas26 .
   ```

#### Run the Container (Common Step for Both Methods)
After obtaining the image using either method, create and run a new container:
```bash
docker run -it tacas26
```
Upon executing this command, you will automatically enter the container's shell environment. Each new container provides an isolated environment derived from the image.

#### Testing

To run the unit tests:

```bash
pytest
```

## 3. Generating Table Results

To reproduce the data for Tables 1-3 and Figure 3 from the paper:

1.  Navigate to the experiments directory:
    ```bash
    cd experiments/
    ```
2.  Run the experiment scripts:
    ```bash
    python table_MQT.py            # Generates data for Table 2, Figure 3(b), Table 3(a)
    python table_Feynman.py        # Generates data for Figure 3(a)
    python table_MQT_Random_Rotation.py # Generates data for Table 3(b)
    ```
3.  The results will be saved in the `Results` directory, located one level up from the `experiments` directory:
    ```bash
    cd ../Results/
    ```
    The output files are named dynamically, incorporating the table type and a timestamp (e.g., `Table_MQT_NOYYYYMMDDHHMMSS.csv`).
