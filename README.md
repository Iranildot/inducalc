# InduCalc

Inducalc is an application that helps chip designers, specially analog ones, draw inductors. This app is based on ASITIC (Analysis and Simulation of Inductors and
Transformers for Integrated Circuits) and looks like a Command-Line Interface.

## Features

The InduCalc app is a cli-like and users can type command with this structure: [COMMAND] [ARGUMENTS] [OPTIONS]

### Default features:

- Theme mode: Dark, Light and System;
- Autocompletion/hints;
- help function: give some piece of information about a given function;
- Helper mode: it help users to type/see arguments and options more easily;
- Clear command: clean up the text area;
- It has command history;

### Custom features:

- Create projects workspaces to handle techfiles and inductors params;
- Specify inductors params and then extract a .gds file;
- Create, import or export techfiles;

## Exemples section

List of few commands

Change to parent directory:
```
cd "../"
```
![cd](https://github.com/user-attachments/assets/c2b3932b-7725-4efd-bc46-44c93f3fc0a7)

List current directory files and folders:
```
ls "."
```
![ls](https://github.com/user-attachments/assets/107b26e5-674d-45ef-b568-dc32d57731ce)

Change theme mode to Light mode:
```
theme set --theme-mode="Light"
```
![thememode](https://github.com/user-attachments/assets/a62ec209-fa6f-4eeb-9151-ff31a2a12f40)

Turning off helper mode:
```
helper --off
```
![helper](https://github.com/user-attachments/assets/948a87b1-c376-413c-93b2-5e0bd4863ace)

Clear the text area:
```
clear
```
![clear](https://github.com/user-attachments/assets/098ffc8a-6949-4fd5-90e8-de43419d1872)


