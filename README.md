# Categorize Files
Create a categorized image of a messy directory. Contained files are classified
according to their suffix or MIME type.

## Parameters
There are two essential parameters: classification criterion and a file system
operation used to create the categorized files.

### Classification Criterion

### Operation

### Image Structure
```
input
├── dir1
│   ├── file.py
│   └── file.pyc
├── dir2
│   ├── file.py
│   └── file.pyc
└── dir3
    ├── file.py
    └── file.pyc
flat_name
├── py
│   ├── file.py
│   ├── file.py.1
│   └── file.py.2
└── pyc
    ├── file.pyc
    ├── file.pyc.1
    └── file.pyc.2
flat_path
├── py
│   ├── dir1_file.py
│   ├── dir2_file.py
│   └── dir3_file.py
└── pyc
    ├── dir1_file.pyc
    ├── dir2_file.pyc
    └── dir3_file.pyc
nested
├── py
│   ├── dir1
│   │   └── file.py
│   ├── dir2
│   │   └── file.py
│   └── dir3
│       └── file.py
└── pyc
    ├── dir1
    │   └── file.pyc
    ├── dir2
    │   └── file.pyc
    └── dir3
        └── file.pyc
```
