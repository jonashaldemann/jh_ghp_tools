# Get started

## Clone this repository

```bash
git clone https://github.com/jonashaldemann/jh_ghp_tools.git
```

## Install for development

```bash
cd jh_ghp_tools
conda env create -f environment.yml
conda activate jh_ghp
pip install -e .
```

## Install to Rhino 8 (Windows)

```bash
cd jh_ghp_tools
%USERPROFILE%\.rhinocode\py39-rh8\python.exe -m pip install --upgrade pip
%USERPROFILE%\.rhinocode\py39-rh8\python.exe -m pip install -e .
```

## Install to Rhino 8 (Mac)

```bash
cd jh_ghp_tools
~/.rhinocode/py39-rh8/python3.9 -m pip install --upgrade pip
~/.rhinocode/py39-rh8/python3.9 -m pip install -e .
```

## Use in Rhino 8

Start a `Python 3 Script` component

```python
import jh_ghp_tools as jh
```