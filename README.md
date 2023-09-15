
# Indieneer API

## Table of Contents
1. [Introduction](#introduction)
2. [Technology Stack](#technology-stack)
3. [Features](#features)
4. [Getting Started](#getting-started)
5. [Endpoints](#endpoints)
6. [Tests](#tests)
7. [Contributing](#contributing)
8. [License](#license)

## Introduction
Indieneer API provides a service for interacting with profiles, products, logins, health, and more. It serves as the backend for the Indieneer platform.

## Technology Stack
- [Python Flask Framework 2.3.3](https://flask.palletsprojects.com/en/2.0.x/)  -- Main framework
- [MongoDB](https://www.mongodb.com/) -- Main database
- [ElasticSearch (coming soon)](https://www.elastic.co/elasticsearch/) -- Search engine framework
- [unittest](https://docs.python.org/3/library/unittest.html) -- Default testing framework

## Features
- User Authentication
- Profile Management
- Product Listings
- Health Metrics
- Search Functionality (coming soon)

## Getting Started

### Prerequisites
1. Python 3.11.5 (or higher)
2. MongoDB Community Server

### Installation Steps
1. Make sure Python 3.11.5 (or higher) is installed on your machine:
    - Visit [Python Downloads](https://www.python.org/downloads/)
    - Download the latest version of Python and complete the installation
2. Clone the repository.
3. Install MongoDB on your machine:
    - Visit [MongoDB Community Server](https://www.mongodb.com/try/download/community)
    - Download and install MongoDB community server
4. Create a virtual environment and activate it.
5. Install all dependencies:  
    ```bash
    pip install -r requirements.txt
    ```
6. Copy the contents of `.env.example` into a `.env` file and define the variables (get them from someone from the Indieneer team).
7. Run the Flask server by executing the `app.py` file:
    ```bash
    python app.py
    ```

## Endpoints
You can look at our design docs and conventions that cover endpoint creation and management [here](https://www.notion.so/Endpoints-02c5f03a25484ad9b720e1385724c15d?pvs=4).

## Tests
Run the unittests by executing the following command in your terminal:
```bash
python -m unittest
```
