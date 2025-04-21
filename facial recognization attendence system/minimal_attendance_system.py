# Minimal Facial Recognition Attendance System
# Requires only OpenCV

import cv2
import os
import time
from datetime import datetime
import csv

class MinimalAttendanceSystem:
    def __init__(self):
        # Create directories
        self.data_dir = "FaceData"
        self.attendance_file = "Attendance.csv"
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"Created directory: {self.data_dir}")
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create attendance file if needed
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time"])
                print(f"Created attendance file: {self.attendance_file}")
    
    def add_face(self):
        """Capture and save face images for a new person"""
        name = input("Enter person's name: ")
        if not name or name.strip() == "":
            print("Name cannot be empty")
            return
        
        # Create folder for this person
        person_dir = os.path.join(self.data_dir, name.replace(" ", "_"))
        if not os.path.exists(person_dir):
            os.makedirs(person_dir)
        
        # Start camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        count = 0
        max_samples = 1  # Changed to capture only one sample
        
        print(f"Capturing {max_samples} image. Position your face in frame.")
        print("Press 'q' to quit early.")
        
        while count < max_samples:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Display the frame
            cv2.putText(frame, f"Samples: {count}/{max_samples}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            cv2.imshow('Face Capture', frame)
            
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            
            # Save image when space is pressed
            if key == ord(' ') and len(faces) > 0:
                img_path = os.path.join(person_dir, f"face_{count}.jpg")
                cv2.imwrite(img_path, frame)
                print(f"Saved image {count+1}/{max_samples}")
                count += 1
                time.sleep(0.5)  # Prevent multiple captures
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"Captured {count} images for {name}")
    
    def mark_attendance(self, name):
        """Mark attendance in the CSV file"""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        # Check if already marked today
        already_marked = False
        if os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row[0] == name and row[1] == date_str:
                        already_marked = True
                        break
        
        if not already_marked:
            with open(self.attendance_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, date_str, time_str])
            print(f"Marked attendance for {name}")
            return True
        return False
    
    def manual_attendance(self):
        """Let user manually select a person to mark attendance"""
        # Get list of people
        people = []
        for item in os.listdir(self.data_dir):
            item_path = os.path.join(self.data_dir, item)
            if os.path.isdir(item_path):
                people.append(item.replace("_", " "))
        
        if not people:
            print("No people registered in the system.")
            return
        
        # Display list of people
        print("\nRegistered People:")
        for i, person in enumerate(people, 1):
            print(f"{i}. {person}")
        
        try:
            selection = int(input("\nEnter number of person to mark attendance: "))
            if 1 <= selection <= len(people):
                name = people[selection-1]
                self.mark_attendance(name)
            else:
                print("Invalid selection")
        except ValueError:
            print("Please enter a number")
    
    def automated_attendance(self):
        """Use face detection to mark attendance (simplified approach)"""
        print("Starting camera for attendance...")
        print("This is a simplified version - just click on a person's name when you see them")
        print("Press 'q' to quit")
        
        # Get list of people
        people = []
        for item in os.listdir(self.data_dir):
            item_path = os.path.join(self.data_dir, item)
            if os.path.isdir(item_path):
                people.append(item.replace("_", " "))
        
        if not people:
            print("No people registered in the system.")
            return
        
        # Start camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Create buttons for marking attendance
        button_height = 30
        button_spacing = 10
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Display frame
            height, width = frame.shape[:1]
            
            # Draw buttons for each person
            for i, name in enumerate(people):
                y_pos = button_spacing + i * (button_height + button_spacing)
                cv2.rectangle(frame, (10, y_pos), (200, y_pos + button_height), (0, 255, 0), -1)
                cv2.putText(frame, name, (15, y_pos + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Display instructions
            cv2.putText(frame, "Click on name to mark attendance", (10, height - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Detect faces (basic detection for visual feedback)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            cv2.imshow('Attendance System', frame)
            
            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            # Check for mouse clicks
            def mouse_callback(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    for i, name in enumerate(people):
                        y_pos = button_spacing + i * (button_height + button_spacing)
                        if 10 <= x <= 200 and y_pos <= y <= y_pos + button_height:
                            self.mark_attendance(name)
            
            cv2.setMouseCallback('Attendance System', mouse_callback)
        
        cap.release()
        cv2.destroyAllWindows()
    
    def view_attendance(self):
        """View attendance records"""
        if not os.path.exists(self.attendance_file):
            print("No attendance records found.")
            return
        
        print("\n----- Attendance Records -----")
        with open(self.attendance_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(" | ".join(row))

def main():
    system = MinimalAttendanceSystem()
    
    while True:
        print("\n=====  Attendance System =====")
        print("1. Register new person")
        print("2. Mark attendance manually")
        print("3. Start camera-based attendance")
        print("4. View attendance records")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            system.add_face()
        elif choice == '2':
            system.manual_attendance()
        elif choice == '3':
            system.automated_attendance()
        elif choice == '4':
            system.view_attendance()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
