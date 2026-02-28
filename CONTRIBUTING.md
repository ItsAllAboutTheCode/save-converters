# Contributing to save-converters


## Adding new converters

To register a new converter the following steps can be performed:  

1. Create a new python module that implements the save conversion between formats.
1. Add a `def add_commands(parser: argparse.ArgumentParser)` method within the converter to register a subparser to invoke the converter command.
1. Inside the `add_commands` method use the `parser.set_defaults(func=<name-of-function-to-perform-conversion>)` to register a hook function that performs the save conversion.
1. Add the absolute module path to the new python module in [save_convert/__init__.py](save_convert/__init__.py) file to the `converter_modules` dictionary.  
   Ex. `converter_modules["game_name"]: "save_convert.path.to.module",`

### Ex. Trails of Cold Steel 1 - Save Converter
An example of setting up a converter can be found in the [trails_of_cold_steel_i_save_converter.py](./save_convert/trails_of/cold_steel_i/trails_of_cold_steel_i_save_converter.py) script.

## Running git repo

The save converter python script can be run directly from a local repo.  

```bash
git clone https://github.com/ItsAllAboutTheCode/save-converters.git
cd save-converters
python save_converter.py
```

## Set up your development environment

Development environment requirements require [Python 3.14+](https://docs.python.org/3/whatsnew/3.14.html#pep-784-zstandard-support-in-the-standard-library) for access to the Zstandard module.  

The recommended way to setup the dev environment is to setup a virtual environment and then install the required python dependencies.  
That can be done using either `uv`:
```bash
uv sync --all-extras
. .venv/bin/activate
```
Or by using `pip`
```bash
python -m venv .venv # Create virtual environment
. .venv/bin/activate
pip install --group dev -e .
```

## Formatting your code
The code can be formatted using `ruff`.  
The project development dependencies come with the `hatch` build tool which can delegate to the `ruff` tool.  

### Format code
Cod can be formated using the following command
- `ruff format` - Only formats the code
- `hatch env run -e lint lint` - Formats the code, have ruff fix any auto-fixable problems and runs unit test

## Writing tests
Unit Test can be added to the [tests](./tests) subdirectory withn this repo.  
It is recommend to add at a test for any new save converter.  

## Running tests
Test can be run using either of the following commands:
- `hatch env run -e lint lint`
- or  `python -m unittest discover tests`

## Building PyInstaller executable

The project can build a native executable for Linux, MacOS or Windows that includes all the necessary dependencies to run in a standalone fashion.  
In this case python, the user does not need python installed to run.  
The `hatch` build tool can be invoked to perform a PyInstaller build.

### Through uv
```bash
uv run hatch build -t custom
```

### Using hatch directly
The hatch build tool must be installed in path or within the activated virtualenv.  
```bash
hatch build -t custom
```

## Project Configuration files
The project uses a [pyproject.toml](./pyproject.toml) file for configuration.  
That file is responsible for specifying python dependencies, hatch build tools and dependencies, linting options and project metadata.
