# Stork

System for automated data and pipeline migration. Stork automates the process of data and pipeline migration to database and cloud environments in three steps:

1. Pipeline Analysis
2. Data Transfer
3. Pipeline Rewrite

In this repository, we provide the code for our VLDB submission, together with short example use cases.

## Stages

We describe the three stages, and provide a running example in the end.

### Pipeline Analysis
The pipeline analysis stage is done by traversing the abstract syntax tree of a given pipeline. Stork generates essential metadata regarding the location and format of the data. Next, Stork formats and migrates the data to a new destination in a hosted Database Management System, cloud storage service, or a local file system. 

### Data Transfer
Following the analysis, data is formatted and transfered to a designated open data storage: database management system, cloud object storage, or a file system. In the current implementation, Stork provides interfaces for Postgres, AWS S3, and the local file system. Each data interface is built as a separate service, allowing developers to extend Stork for new storage backends.

### Pipeline Rewrite
The original pipeline is rewritten to provide access to the new data. All data access are changed with adequate data paths, configuration verifications, and connectors. The output pipeline is an interoperable pipeline that does not depend on the original local data access. 

## Installation

To use Stork, copy the repository and install the necessary requirements in a virtual environment:

```
git clone git@github.com:hpides/stork.git && cd stork

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```
To verify the installation, run the empty initialization of Stork and check the output in **examples/logs/**:

```
python3 examples/stork-init.py
```

## Run Pipeline Analysis with Stork

To run an example pipeline with Stork, execute the Stork runner with the provided **example.py** pipeline. In order to generate a small dataset of 1MB, we run the **example.py** pipeline first:

```
python3 examples/pipelines/example.py
python3 examples/stork-runner.py --pipeline=examples/pipelines/example.py
```

The output log, the recognized datasets are written in the **examples/outputs** folder.

## Start a Postgres Instance

To set up Stork with a Postgres backend, we start a Postgres image with the following script:

```
bash scripts/run.sh
```
To run the Stork workflow:

```
python3 examples/stork-runner-pg --pipeline=examples/pipelines/example.py
```

## Stork with AWS S3
In order to use Stork with AWS S3 as data backend, an existing S3 configuration is required. 

Provide the config file containing the AWS access keys as an execution parameter:

```
python3 examples/stork-runner-s3.py --credentials=PATH_TO_AWS_CONFIG_FILE
```
## Generate Results from the Paper

To generate the paper plots, execute the following script:

```
cd generate-plots && bash generate-plots.sh
```





