  

# File Change Monitoring and Message Broker Integration

## Overview

This project implements a **basic message broker** and integrates it with a **file monitoring system**. The purpose is to efficiently track changes to files, especially "important files," and maintain an audit log for all file changes. The project demonstrates key software engineering concepts like **publish-subscribe patterns**, **wildcard matching**, and **file system monitoring**.
  

## Requirements
 
To run this module, you'll need Python 3 and `virtualenv`. The required dependencies are listed in the `requirements.txt` file. 

## Setup Instructions

### 1. Create and Activate a Virtual Environment
 
First, create a virtual environment for your project if you don't have one already:

```bash

python3  -m  venv  venv

```

Activate the virtual environment:

  

```bash

source  venv/bin/activate

```

### 2. Install the Required Dependencies

 
With the virtual environment activated, install the dependencies listed in the `requirements.txt` file:

  

```bash

pip  install  -r  requirements.txt

```

### 3. Set Environment Variables

  

Ensure the following environment variable is set:

  

-  `FILE_SERVER_ROOT_PATH`: The root path of the file server where the directory to monitor exists.

  

You can set this environment variable as follows:

  

```bash

export  FILE_SERVER_ROOT_PATH="/path/to/your/file/server"

```

  

### 4. Run the Module

  

To start monitoring file changes and publishing them to the message broker, simply run the `monitor.py` script:

  

```bash

python  monitor.py

```

  

The script will monitor changes in the `important_stuff` directory (you can customize this directory in the code), publish changes to the message broker, and log file modifications for auditing.

  

### 5. Run Tests

  

To run the test cases for this module, use the following command:

  

```bash

python3  -m  unittest  discover  -s  tests

```

  

This will automatically discover and run all test cases in the `tests` directory.

  

### 6. Stopping the Monitor

  

To stop the monitor, press `Ctrl+C` in your terminal. The observer will stop, and the program will gracefully shut down.

  

---

  

## Files and Directories

  

-  `appp.py`: The main script that sets up file monitoring and message broker integration.

-  `file_change_audit.log`: The log file where file change events are recorded (if not specified, it defaults to the script's directory).

-  `requirements.txt`: The file containing all the required dependencies for the project.

## Dependencies

  

The following dependencies are used in this project:

-  `watchdog`: For monitoring file system changes.

-  `difflib`: For generating diffs of file changes.
  

---