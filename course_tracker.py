import requests
import json
import time
from datetime import datetime
import schedule
import threading
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv('WATERLOO_API_KEY')
if not API_KEY:
    print("Error: WATERLOO_API_KEY environment variable not set")
    print("Please create a .env file with your API key or set it in your environment")
    print("Example .env file content:")
    print("WATERLOO_API_KEY=your_api_key_here")
    sys.exit(1)

class CourseTracker:
    def __init__(self, api_key, term):
        self.api_key = api_key
        self.term = term
        self.base_url = "https://openapi.data.uwaterloo.ca/v3"
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        self.is_monitoring = False
        self.monitor_thread = None

    def get_course_info(self, subject, catalog_number, term):
        # Remove any spaces from subject code
        subject = subject.strip()
        endpoint = f"{self.base_url}/Courses/{term}/{subject}/{catalog_number}"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # print("\nCourse Info Response:")
            # print(json.dumps(data, indent=2))
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching course data: {e}")
            return None

    def get_class_schedule(self, subject, catalog_number, term):
        subject = subject.strip()
        endpoint = f"{self.base_url}/ClassSchedules/{term}/{subject}/{catalog_number}"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # print("\nClass Schedule Response:")
            # print(json.dumps(data, indent=2))
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching class schedule: {e}")
            return None
    def check_availability(self, subject, catalog_number, term, section_numbers=None):
        schedule_data = self.get_class_schedule(subject, catalog_number, term)
        if not schedule_data:
            print("No schedule data received")
            return False
        try:
            # print(f"\nLooking for sections: {section_numbers if section_numbers else 'All sections'}")
            # Check each class section for availability
            for section in schedule_data:
                section_number = section.get('classSection', 0)
                # print(f"\nFound section: {section_number}")
                # Skip if we're only checking specific sections and this isn't one of them
                if section_numbers and section_number not in section_numbers:
                    # print(f"Skipping section {section_number} - not in monitored sections")
                    continue
                # print(f"Checking section {section_number}:")
                # print(json.dumps(section, indent=2))
                capacity = section.get('maxEnrollmentCapacity', 0)
                enrolled = section.get('enrolledStudents', 0)
                # print(f"Section {section_number} - Capacity: {capacity}, Enrolled: {enrolled}")
                if enrolled < capacity:
                    print(f"Found available space in section {section_number}!")
                    return True
            if section_numbers:
                print(f"\nNo available spaces found in monitored sections: {', '.join(map(str, section_numbers))}")
            else:
                print("\nNo available spaces found in any section")
            return False
        except Exception as e:
            print(f"Error processing class schedule data: {e}")
            return False

    def get_course_details(self, subject, catalog_number, term):
        course_data = self.get_course_info(subject, catalog_number, term)
        if not course_data:
            return None

        try:
            # Course info 
            return {
                'title': course_data.get('title', 'Unknown'),
                'description': course_data.get('description', 'No description available'),
                'requirements': course_data.get('requirementsDescription', 'No requirements listed')
            }
        except Exception as e:
            print(f"Error processing course details: {e}")
            return None

    def stop_monitoring(self):
        self.is_monitoring = False
        print("\nStopped monitoring.")

def get_section_numbers():
    while True:
        choice = input("\nDo you want to monitor specific sections? (yes/no): ").lower()
        if choice in ['yes', 'y']:
            sections = input("Enter section numbers (comma-separated, e.g., 1,2): ").strip()
            try:
                formatted_sections = [int(s.strip()) for s in sections.split(',')]
                print(f"Monitoring sections: {', '.join(map(str, formatted_sections))}")
                return formatted_sections
            except ValueError:
                print("Invalid input. Please enter numbers only (e.g., 1,2,3)")
                continue
        elif choice in ['no', 'n']:
            return None
        else:
            print("Please enter 'yes' or 'no'")

def check_for_quit():
    while True:
        if input().lower() == 'q':
            return True
        time.sleep(0.1)
def monitor_course(tracker, subject, catalog_number, term, section_numbers):
    def check_course():
        if not tracker.is_monitoring:
            return
        if tracker.check_availability(subject, catalog_number, term, section_numbers):
            section_info = f" in sections {', '.join(map(str, section_numbers))}" if section_numbers else ""
            print(f"\n[{datetime.now()}] Space available in {subject} {catalog_number}{section_info}!")
        else:
            section_info = f" in sections {', '.join(map(str, section_numbers))}" if section_numbers else ""
            print(f"\n[{datetime.now()}] No space available in {subject} {catalog_number}{section_info}")

    check_course()
    schedule.clear()
    schedule.every(2).minutes.do(check_course)
    
    section_info = f" (sections {', '.join(map(str, section_numbers))})" if section_numbers else ""
    print(f"\nMonitoring {subject} {catalog_number}{section_info} for term {term}...")
    print("Press 'q' and Enter to stop monitoring and return to main menu")
    quit_thread = threading.Thread(target=check_for_quit)
    quit_thread.daemon = True
    quit_thread.start()
    
    while tracker.is_monitoring:
        schedule.run_pending()
        time.sleep(1)
        if not quit_thread.is_alive():
            tracker.stop_monitoring()
            break
def main_menu(tracker):
    while True:
        print("\n=== Course Tracker Menu ===")
        print("1. Start monitoring a course")
        print("2. Change term")
        print("3. Exit")
        choice = input("\nEnter your choice (1-3): ")
        if choice == "1":
            # Get course information from user
            subject = input("Enter subject code (e.g., CS): ").upper()
            catalog_number = input("Enter catalog number (e.g., 135): ")
            # Get section numbers to monitor
            section_numbers = get_section_numbers()
            # Start monitoring
            tracker.is_monitoring = True
            tracker.monitor_thread = threading.Thread(
                target=monitor_course,
                args=(tracker, subject, catalog_number, tracker.term, section_numbers)
            )
            tracker.monitor_thread.start()
            tracker.monitor_thread.join()
        elif choice == "2":
            new_term = input("Enter new term code (e.g., 1255): ")
            tracker.term = new_term
            print(f"Term updated to {new_term}")   
        elif choice == "3":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    term = input("Enter term code (e.g., 1255): ")
    tracker = CourseTracker(API_KEY, term)
    main_menu(tracker)