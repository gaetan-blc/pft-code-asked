
## Overview

This Python script automates the process of  capturing periodic screenshots during gameplay, and maintaining a log of captured events in a CSV manifest file. The script is tailored for a specific setup involving local services and a game emulator, but it can be adapted to other scenarios.

## Features

1. **Screenshot Capture**:
   - Takes periodic screenshots of a game’s video element during gameplay.
   - Saves screenshots in a structured directory with a CSV manifest file containing metadata.

4. **API Integration**:
   - Calls an API endpoint (`/gameStarted`) with the game URL once the game starts.

5. **Logging**:
   - Logs key events and debug information to the console.
   - Creates a manifest file (`manifest.csv`) for screenshot metadata.

## Script Workflow

1. Starts the game .
2. Captures screenshots of the gameplay video element at 1-second intervals for a defined duration (default: 5 minutes).
3. Logs screenshot metadata to a CSV file.
4. Calls an API to notify that the game has started.


## Setup and Requirements

### Prerequisites
- Python 3.x installed.

Install the required packages using:
```bash
pip install pillow requests

