# Installation Guide

## Install from PyPI

```bash
pip install asmysql
```

## Install from Source

```bash
git clone https://github.com/vastxiao/asmysql.git
cd asmysql
pip install .
```

## Requirements

- Python >= 3.9
- aiomysql[rsa] >= 0.3.2

## Verify Installation

After installation, you can verify the installation by trying to import the main classes:

```python
from asmysql import Engine, AsMysql
print("Installation successful!")
```

