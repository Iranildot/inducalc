# InduCalc

Inducalc is an application that helps chip designers, specially analog ones, draw inductors. This app is based on ASITIC (Analysis and Simulation of Inductors and
Transformers for Integrated Circuits) and looks like a Command-Line Interface.

## Features

The InduCalc app is a cli-like and users can type command with this structure: [COMMAND] [ARGUMENTS] [OPTIONS]

### Default:

- Theme mode: Dark, Light and System;
- Autocompletion/hints;
- help function: give some piece of information about a given function;
- Helper mode: it help users to type/see arguments and options more easily;
- Clear command: clean up the text area;

### Custom:

- project: workspace to organize techfiles and inductor's params
  - delete: delete an existing project;
  - list: list project's names into current directory;
  - new: create a new project;
  - rename: rename a specific project name;
- inductor: fu
