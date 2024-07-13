# Bun Version Manager

Bun Version Manager (BVM) is a Python script designed to manage different versions of the .bun package manager on Unix-like systems. It allows you to add, delete, switch between, and list installed .bun versions conveniently from the command line.

## Features
* Add Version: Download and install a specific version of .bun into a designated directory.
* Delete Version: Remove a previously installed .bun version.
* Switch Version: Set a specific .bun version as the active version.
* List Versions: Display all downloaded .bun versions.
## Requirements
* Python 3.x
* requests and beautifulsoup4 library
* Unix-like operating system (Linux, macOS)
## Installation

Clone the repository or download the script directly.
```bash
git clone https://github.com/KPCOFGS/bvm.git
cd bvm
```
## Usage
**Commands:**
* add <version>: Adds the specified .bun version to the system. For example, 1.1.1.
```bash
python bvm.py add 1.1.1
```
* delete <version>: Deletes the specified .bun version from the system.
```bash
python bvm.py delete 1.1.1
```
* switch <version>: Switches the active .bun version to the specified version.
```bash
python bvm.py switch 1.1.1
```
* list: Lists all downloaded .bun versions.
```bash
python bvm.py list
```
## Configuration
* By default, BVM stores versions in ~/bvm/. Ensure this directory is writable and accessible.
## Shell Configuration

BVM modifies shell configurations to manage environment variables related to .bun versions. Ensure your shell configuration file (~/.bashrc, ~/.zshrc, or ~/.config/fish/config.fish) is correctly configured after installation.

## License
This project is licensed under The Unlicense license - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
* Special thanks to the [Bun](https://github.com/oven-sh/bun) team for their amazing project.
* Inspired by the need to manage multiple .bun versions efficiently on Unix-like systems.
