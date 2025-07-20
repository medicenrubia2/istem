#!/usr/bin/env python3
"""
Comprehensive Backend Testing for ISTEM Platform
Tests all backend APIs systematically with focus on high-priority tasks
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://d40130b3-1745-460f-8546-d4a362ec3007.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class IStemBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.test_results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "course_management": {"passed": 0, "failed": 0, "details": []},
            "dashboard": {"passed": 0, "failed": 0, "details": []},
            "progress_tracking": {"passed": 0, "failed": 0, "details": []},
            "enrollment": {"passed": 0, "failed": 0, "details": []},
            "meetings": {"passed": 0, "failed": 0, "details": []},
            "lessons": {"passed": 0, "failed": 0, "details": []}
        }
        self.test_data = {
            "student_user": None,
            "instructor_user": None,
            "course_id": None,
            "lesson_id": None,
            "meeting_id": None
        }

    def log_result(self, category: str, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        if passed:
            self.test_results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results[category]["failed"] += 1
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results[category]["details"].append(result)
        print(result)

    def make_request(self, method: str, endpoint: str, data: Dict = None, auth_required: bool = False) -> tuple:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if auth_required and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            try:
                return response.status_code < 400, response.json()
            except:
                return response.status_code < 400, {"text": response.text}
                
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    def test_authentication_system(self):
        """Test user authentication system - HIGH PRIORITY"""
        print("\n🔐 Testing Authentication System...")
        
        # Test 1: User Registration (Student)
        student_data = {
            "email": "maria.gonzalez@estudiante.com",
            "password": "EstudianteSeguro123!",
            "name": "María González",
            "role": "student"
        }
        
        success, response = self.make_request("POST", "/auth/register", student_data)
        if success and "access_token" in response:
            self.test_data["student_user"] = response["user"]
            self.log_result("authentication", "Student Registration", True, f"User ID: {response['user']['id']}")
        else:
            self.log_result("authentication", "Student Registration", False, str(response))

        # Test 2: User Registration (Instructor)
        instructor_data = {
            "email": "prof.rodriguez@instructor.com",
            "password": "ProfesorSeguro123!",
            "name": "Prof. Carlos Rodríguez",
            "role": "instructor"
        }
        
        success, response = self.make_request("POST", "/auth/register", instructor_data)
        if success and "access_token" in response:
            self.test_data["instructor_user"] = response["user"]
            instructor_token = response["access_token"]
            self.log_result("authentication", "Instructor Registration", True, f"User ID: {response['user']['id']}")
        else:
            self.log_result("authentication", "Instructor Registration", False, str(response))

        # Test 3: User Login (Valid Credentials)
        login_data = {
            "email": "maria.gonzalez@estudiante.com",
            "password": "EstudianteSeguro123!"
        }
        
        success, response = self.make_request("POST", "/auth/login", login_data)
        if success and "access_token" in response:
            self.auth_token = response["access_token"]
            self.log_result("authentication", "Valid Login", True, "JWT token received")
        else:
            self.log_result("authentication", "Valid Login", False, str(response))

        # Test 4: User Login (Invalid Credentials)
        invalid_login = {
            "email": "maria.gonzalez@estudiante.com",
            "password": "ContraseñaIncorrecta"
        }
        
        success, response = self.make_request("POST", "/auth/login", invalid_login)
        if not success and response.get("detail") == "Invalid email or password":
            self.log_result("authentication", "Invalid Login Rejection", True, "Correctly rejected invalid credentials")
        else:
            self.log_result("authentication", "Invalid Login Rejection", False, "Should reject invalid credentials")

        # Test 5: JWT Token Authentication
        if self.auth_token:
            success, response = self.make_request("GET", "/auth/me", auth_required=True)
            if success and "email" in response:
                self.log_result("authentication", "JWT Token Authentication", True, f"User: {response['name']}")
            else:
                self.log_result("authentication", "JWT Token Authentication", False, str(response))

        # Test 6: Duplicate Email Registration
        success, response = self.make_request("POST", "/auth/register", student_data)
        if not success and "already registered" in str(response).lower():
            self.log_result("authentication", "Duplicate Email Prevention", True, "Correctly prevents duplicate registration")
        else:
            self.log_result("authentication", "Duplicate Email Prevention", False, "Should prevent duplicate emails")

    def test_course_management_system(self):
        """Test course management system - HIGH PRIORITY"""
        print("\n📚 Testing Course Management System...")
        
        # First, login as instructor to create courses
        if self.test_data["instructor_user"]:
            instructor_login = {
                "email": "prof.rodriguez@instructor.com",
                "password": "ProfesorSeguro123!"
            }
            success, response = self.make_request("POST", "/auth/login", instructor_login)
            if success:
                instructor_token = response["access_token"]
                original_token = self.auth_token
                self.auth_token = instructor_token

                # Test 1: Course Creation (Instructor)
                course_data = {
                    "title": "Introducción a la Programación Python",
                    "description": "Curso completo de Python desde cero hasta nivel intermedio",
                    "thumbnail": "https://example.com/python-course.jpg",
                    "duration_hours": 40,
                    "level": "Beginner",
                    "price": 99.99
                }
                
                success, response = self.make_request("POST", "/courses", course_data, auth_required=True)
                if success and "id" in response:
                    self.test_data["course_id"] = response["id"]
                    self.log_result("course_management", "Course Creation by Instructor", True, f"Course ID: {response['id']}")
                else:
                    self.log_result("course_management", "Course Creation by Instructor", False, str(response))

                # Restore student token
                self.auth_token = original_token

        # Test 2: Get All Courses (Public)
        success, response = self.make_request("GET", "/courses")
        if success and isinstance(response, list):
            self.log_result("course_management", "Get All Courses", True, f"Found {len(response)} courses")
            if not self.test_data["course_id"] and len(response) > 0:
                self.test_data["course_id"] = response[0]["id"]
        else:
            self.log_result("course_management", "Get All Courses", False, str(response))

        # Test 3: Get Specific Course
        if self.test_data["course_id"]:
            success, response = self.make_request("GET", f"/courses/{self.test_data['course_id']}")
            if success and "title" in response:
                self.log_result("course_management", "Get Specific Course", True, f"Course: {response['title']}")
            else:
                self.log_result("course_management", "Get Specific Course", False, str(response))

        # Test 4: Course Creation by Student (Should Fail)
        if self.auth_token:
            course_data = {
                "title": "Unauthorized Course",
                "description": "This should fail",
                "duration_hours": 10,
                "level": "Beginner"
            }
            success, response = self.make_request("POST", "/courses", course_data, auth_required=True)
            if not success and "403" in str(response) or "Only instructors" in str(response):
                self.log_result("course_management", "Student Course Creation Prevention", True, "Correctly prevents student course creation")
            else:
                self.log_result("course_management", "Student Course Creation Prevention", False, "Should prevent students from creating courses")

    def test_enrollment_system(self):
        """Test course enrollment system"""
        print("\n📝 Testing Enrollment System...")
        
        if not self.auth_token or not self.test_data["course_id"]:
            self.log_result("enrollment", "Enrollment Tests", False, "Missing auth token or course ID")
            return

        # Test 1: Course Enrollment
        success, response = self.make_request("POST", f"/enrollments/{self.test_data['course_id']}", auth_required=True)
        if success and "Successfully enrolled" in str(response):
            self.log_result("enrollment", "Course Enrollment", True, "Successfully enrolled in course")
        else:
            self.log_result("enrollment", "Course Enrollment", False, str(response))

        # Test 2: Duplicate Enrollment Prevention
        success, response = self.make_request("POST", f"/enrollments/{self.test_data['course_id']}", auth_required=True)
        if not success and "Already enrolled" in str(response):
            self.log_result("enrollment", "Duplicate Enrollment Prevention", True, "Correctly prevents duplicate enrollment")
        else:
            self.log_result("enrollment", "Duplicate Enrollment Prevention", False, "Should prevent duplicate enrollment")

        # Test 3: Get My Courses
        success, response = self.make_request("GET", "/my-courses", auth_required=True)
        if success and isinstance(response, list) and len(response) > 0:
            self.log_result("enrollment", "Get My Courses", True, f"Found {len(response)} enrolled courses")
        else:
            self.log_result("enrollment", "Get My Courses", False, str(response))

    def test_student_dashboard_api(self):
        """Test student dashboard API - HIGH PRIORITY"""
        print("\n📊 Testing Student Dashboard API...")
        
        if not self.auth_token:
            self.log_result("dashboard", "Dashboard Tests", False, "Missing auth token")
            return

        # Test 1: Dashboard Data Retrieval
        success, response = self.make_request("GET", "/dashboard", auth_required=True)
        if success and "user" in response:
            required_fields = ["user", "total_courses", "recent_courses", "upcoming_meetings"]
            all_fields_present = all(field in response for field in required_fields)
            
            if all_fields_present:
                self.log_result("dashboard", "Dashboard Data Structure", True, 
                               f"Total courses: {response['total_courses']}, Recent: {len(response['recent_courses'])}")
            else:
                missing = [f for f in required_fields if f not in response]
                self.log_result("dashboard", "Dashboard Data Structure", False, f"Missing fields: {missing}")
        else:
            self.log_result("dashboard", "Dashboard Data Structure", False, str(response))

        # Test 2: Dashboard Authentication Required
        original_token = self.auth_token
        self.auth_token = None
        success, response = self.make_request("GET", "/dashboard", auth_required=False)
        if not success:
            self.log_result("dashboard", "Dashboard Authentication Required", True, "Correctly requires authentication")
        else:
            self.log_result("dashboard", "Dashboard Authentication Required", False, "Should require authentication")
        self.auth_token = original_token

    def test_progress_tracking_system(self):
        """Test progress tracking system - HIGH PRIORITY"""
        print("\n📈 Testing Progress Tracking System...")
        
        if not self.auth_token or not self.test_data["course_id"]:
            self.log_result("progress_tracking", "Progress Tests", False, "Missing auth token or course ID")
            return

        # First, get course lessons to have a lesson to mark complete
        success, response = self.make_request("GET", f"/courses/{self.test_data['course_id']}/lessons", auth_required=True)
        if success and isinstance(response, list) and len(response) > 0:
            lesson_id = response[0]["id"]
            self.test_data["lesson_id"] = lesson_id
            self.log_result("progress_tracking", "Get Course Lessons", True, f"Found {len(response)} lessons")
            
            # Test 1: Mark Lesson Complete
            success, response = self.make_request("POST", f"/progress/{lesson_id}", auth_required=True)
            if success and "progress_percentage" in response:
                self.log_result("progress_tracking", "Mark Lesson Complete", True, 
                               f"Progress: {response['progress_percentage']}%")
            else:
                self.log_result("progress_tracking", "Mark Lesson Complete", False, str(response))

            # Test 2: Get Course Progress
            success, response = self.make_request("GET", f"/courses/{self.test_data['course_id']}/progress", auth_required=True)
            if success and "progress" in response and "enrollment" in response:
                self.log_result("progress_tracking", "Get Course Progress", True, 
                               f"Progress entries: {len(response['progress'])}")
            else:
                self.log_result("progress_tracking", "Get Course Progress", False, str(response))
        else:
            self.log_result("progress_tracking", "Get Course Lessons", False, "No lessons found or access denied")

    def test_virtual_meetings_system(self):
        """Test virtual meetings system - MEDIUM PRIORITY"""
        print("\n🎥 Testing Virtual Meetings System...")
        
        if not self.test_data["course_id"]:
            self.log_result("meetings", "Meeting Tests", False, "Missing course ID")
            return

        # Test as instructor first
        if self.test_data["instructor_user"]:
            instructor_login = {
                "email": "prof.rodriguez@instructor.com",
                "password": "ProfesorSeguro123!"
            }
            success, response = self.make_request("POST", "/auth/login", instructor_login)
            if success:
                instructor_token = response["access_token"]
                original_token = self.auth_token
                self.auth_token = instructor_token

                # Test 1: Create Meeting (Instructor)
                meeting_data = {
                    "course_id": self.test_data["course_id"],
                    "title": "Sesión de Introducción a Python",
                    "description": "Primera clase del curso de Python",
                    "scheduled_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "duration_minutes": 90,
                    "meeting_url": "https://zoom.us/j/123456789",
                    "max_participants": 30
                }
                
                success, response = self.make_request("POST", f"/courses/{self.test_data['course_id']}/meetings", 
                                                    meeting_data, auth_required=True)
                if success and "id" in response:
                    self.test_data["meeting_id"] = response["id"]
                    self.log_result("meetings", "Meeting Creation by Instructor", True, f"Meeting ID: {response['id']}")
                else:
                    self.log_result("meetings", "Meeting Creation by Instructor", False, str(response))

                # Restore student token
                self.auth_token = original_token

        # Test 2: Get Course Meetings (Student)
        if self.auth_token and self.test_data["course_id"]:
            success, response = self.make_request("GET", f"/courses/{self.test_data['course_id']}/meetings", auth_required=True)
            if success and isinstance(response, list):
                self.log_result("meetings", "Get Course Meetings", True, f"Found {len(response)} meetings")
            else:
                self.log_result("meetings", "Get Course Meetings", False, str(response))

    def test_lesson_management(self):
        """Test lesson management system"""
        print("\n📖 Testing Lesson Management System...")
        
        if not self.test_data["course_id"]:
            self.log_result("lessons", "Lesson Tests", False, "Missing course ID")
            return

        # Test as instructor
        if self.test_data["instructor_user"]:
            instructor_login = {
                "email": "prof.rodriguez@instructor.com",
                "password": "ProfesorSeguro123!"
            }
            success, response = self.make_request("POST", "/auth/login", instructor_login)
            if success:
                instructor_token = response["access_token"]
                original_token = self.auth_token
                self.auth_token = instructor_token

                # Test 1: Create Lesson (Instructor)
                lesson_data = {
                    "title": "Variables y Tipos de Datos",
                    "description": "Introducción a variables y tipos de datos en Python",
                    "content": "En esta lección aprenderemos sobre variables...",
                    "lesson_type": "text",
                    "duration_minutes": 30,
                    "order": 1
                }
                
                success, response = self.make_request("POST", f"/courses/{self.test_data['course_id']}/lessons", 
                                                    lesson_data, auth_required=True)
                if success and "id" in response:
                    self.test_data["lesson_id"] = response["id"]
                    self.log_result("lessons", "Lesson Creation by Instructor", True, f"Lesson ID: {response['id']}")
                else:
                    self.log_result("lessons", "Lesson Creation by Instructor", False, str(response))

                # Restore student token
                self.auth_token = original_token

    def run_all_tests(self):
        """Run all backend tests in priority order"""
        print("🚀 Starting ISTEM Backend Comprehensive Testing")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # High Priority Tests
        self.test_authentication_system()
        self.test_course_management_system()
        self.test_enrollment_system()
        self.test_student_dashboard_api()
        self.test_progress_tracking_system()
        
        # Medium Priority Tests
        self.test_virtual_meetings_system()
        self.test_lesson_management()
        
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅" if failed == 0 else "❌" if passed == 0 else "⚠️"
            print(f"\n{status} {category.upper().replace('_', ' ')}: {passed} passed, {failed} failed")
            
            for detail in results["details"]:
                print(f"  {detail}")
        
        print(f"\n🎯 OVERALL RESULTS: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! Backend is working correctly.")
        elif total_failed <= 3:
            print("⚠️  Minor issues found. Core functionality working.")
        else:
            print("❌ Significant issues found. Backend needs attention.")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = IStemBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)