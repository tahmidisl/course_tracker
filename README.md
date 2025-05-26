# Waterloo Course Tracker

This tool helps you monitor course availability at the University of Waterloo using the Waterloo Open API.

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Get your API key from the [Waterloo Open Data API](https://openapi.data.uwaterloo.ca/)

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
   - Term (e.g., 1235 for Winter 2023)
3. Check the course availability immediately and then every 5 minutes
4. Notify you when a spot becomes available

Press Ctrl+C to stop the script.

## Notes

- The term code format is: [Year][Term]
  - 1: Winter
  - 5: Spring
  - 9: Fall
  - Example: 1235 means Winter 2023

- The script will continue running until you stop it with Ctrl+C
- It checks for availability every 5 minutes to avoid overwhelming the API 