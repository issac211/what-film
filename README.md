# What-Film

What-Film is a web application that allows users to search for movies, view detailed information retrieved from the OMDb API, and manage a personal list of favorite films.
The project also includes user registration, authentication, and profile management features.

## Overview

What-Film is built with Python using the Flask framework for the web server. It leverages SQLAlchemy as an ORM to interact with a PostgreSQL database and communicates with the OMDb API to fetch movie data.
The application provides a simple and intuitive interface for users to search for movies by title, view detailed information about each movie, and manage their list of favorites. Additionally, users can create an account,
log in, change their password, or delete their profile.


## Features
- **Movie Search:** 
  - Search for movies by title using the OMDb API.
  - View movie details such as title, year, poster, genre, ratings, plot, and more.
- **User Management:**
  - User registration and login with basic validations.
  - Change password and delete user functionality.
- **Favorites:** 
  - Add movies to your favorites list.
  - View and manage favorite movies with pagination.
- **Top Movies:**
  - View a list of top movies based on the number of users who have favorited them.
- **Session Management:** 
  - Persistent user sessions using Flask sessions.
- **Security Considerations:**
  - Password validations and restrictions to ensure basic security.
  - Utilizes environment variables to store sensitive data such as API keys and database URLs.

## Technology Stack
- **Programming Language:** Python
- **Web Framework:** Flask
- **Templating Engine:** Jinja2 (with `.j2` templates)
- **Database:** PostgreSQL (accessed via SQLAlchemy)
- **APIs:** OMDb API for retrieving movie information
- **HTTP Protocols:** Utilizes HTTP/HTTPS for API communication
- **ORM:** SQLAlchemy for database operations
- **Front-End:** HTML/CSS for rendering pages and providing a user-friendly interface

## Project Structure
A brief overview of the key components:
- `app.py`: Main application file that contains routes, database models, and business logic.
- **Templates:** Located in the templates folder (e.g., `index.j2`, `login.j2`, `search.j2`) for rendering views.
- **Static Files:** (if any) CSS, JavaScript, and images used for styling and enhancing the user experience.
- `requirements.txt`: Lists all the Python dependencies needed to run the project.
