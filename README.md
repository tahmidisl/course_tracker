# Waterloo Course Tracker

This tool helps you monitor course availability at the University of Waterloo using the Waterloo Open API.

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Get your API key from the [Waterloo Open Data API]([https://openapi.data.uwaterloo.ca/](https://uwaterloo.atlassian.net/wiki/spaces/UWAPI/pages/34025641600/Getting+Started+-+OpenAPI))

## Usage

Run the script:
```bash
python course_tracker.py
```

The script will:
1. Ask for your API key
2. Prompt for the course information:
   - Subject code (e.g., CS)
   - Catalog number (e.g., 135)
   - Term (e.g., 1255 for Spring 2025)
3. Check the course availability immediately and then every 2 minutes
4. Notify you when a spot becomes available

Press Ctrl+C to stop the script.

- Term Codes, Section Numbers and Classes for each term can be found on [class](https://classes.uwaterloo.ca/under.html)


