Collaborative App with Django Backend
Overview
This project is a collaborative application built with Django, featuring group management, email verification via OTP, and a modern, responsive UI. It is designed to be hosted on GitHub and leverages a robust Django backend. Additionally, user data (personal) is securely fetched through an API hosted on PythonAnywhere.

Features
Group Management: Create and manage groups for collaborative work.

Email Verification: Users must verify their email using a One-Time Password (OTP).

Awesome UI: A clean, responsive, and modern user interface.

Django Backend: Built with Django for a powerful and scalable backend.

External API Integration: User personal data is retrieved from an external API hosted on PythonAnywhere.

Installation
Prerequisites
Python 3.x

Django

Additional packages:

django-otp

pyotp
Usage
Email Verification
When a user registers, an OTP is sent to their email. The user must input this OTP to verify their email address and activate their account.

Group Management
Users can create and manage groups. Each group can contain multiple members. Future updates can include group-specific permissions, tasks, chat features, and more.

Fetching User Data via API
User personal data (e.g., name, email, phone number, etc.) is fetched through a secure API hosted on PythonAnywhere. This external API allows real-time access to up-to-date personal user details upon registration or profile view.
License
This project is licensed under the MIT License.

Acknowledgments
Django OTP for OTP-based verification.

Tutorials on implementing OTP verification in Django.

PythonAnywhere for API hosting.
