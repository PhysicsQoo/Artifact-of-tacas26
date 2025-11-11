# QUPRS Artifact-of-tacas26
## 1. Introduction
This artifact accompanies the TACAS’26 paper "Equivalence Checking of Quantum Circuits via Path‑Sum and Weighted Model Counting". It provides the code, benchmark inputs, and experiment scripts needed to reproduce the paper’s results (Tables 1–3 and Figure 3). The package is intended to validate correctness and enable reproducible experiments; exact runtimes may vary with hardware and environment.

## 2. Download, installation, and testing

- Full reproduction: run the experiment scripts described in the README to regenerate data of Tables 1–3 and Figure 3. Results should match the paper’s correctness outcomes; measured runtimes may differ across machines.
- Notes: slower machines tend to produce more timeouts; machines with limited RAM may incur more out-of-memory failures. Verify logs and error messages for troubleshooting.
### 2.1 Download
1. Docker: https://docs.docker.com/get-started/get-docker/
2. Docker image as the artifact: tacas26.tar
3. https://doi.org/10.5281/zenodo.xxxxxxx
### 2.2 Installation and Setup
1. Install Docker as usual.
2. Load the image into Docker.
$ docker load -i tacas26.tar
3. Create and run a new container from an image. (Notice that each new
container is an isolated environment stemming from the image.)
$ docker run -it tacas26
After running this command, you will enter the container automatically.

### Testing
1. Run $pytest$

## 3. Run the table results
...