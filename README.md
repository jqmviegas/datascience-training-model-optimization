# Data Science Training - Model Optimization

### Creating conda environment

    conda create --name ds python=3.7 
    conda activate ds
    pip install -r requirements.txt

### Updating requirements file

    pip freeze > requirements.txt

### Folder structure

The directory structure of your new project looks like this (please adjust the structure and its description to best fit your project): 

```
├── README.md          <- The top-level README.
│
├── database
│   ├── raw_data.csv   <- Original data to simulate the system.
│   └── database.csv   <- Data to simulate the application database.
│
├── notebooks          <- Jupyter notebooks for exploratory analysis.
│
├── docs               <- Resources on Data Science and Data Mining.
│
├── requirements.txt   <- Environmnet package requirements.
││
├── simulator.py       <- Module to simulate the system in "real-time".
│
├── modeling.py        <- Module with functions to train, run and evaluate models.
││
└── frontend.py        <- Front-end application.
```

