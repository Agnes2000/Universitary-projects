# Film Management Platform

A web-based information system developed to manage movies, actors, and directors, and to link them together in a relational structure.

The platform allows users to manage and query a movie database through an interactive web interface.  

## Features / Implemented

- **User roles:**  
  - **Administrator:** can add and manage movies, actors, and directors.  
  - **End users:** can search movies, view details, and see relationships between actors, directors, and films.  

- **CRUD operations:**  
  - Create, Read, Update, and Delete movies, actors, and directors.  
  - Link actors and directors to movies to maintain relational data.  

- **Interactive forms:**  
  - Forms for adding movies, actors, and directors.  
  - Forms for searching and filtering movies by actors, directors, or genres.  

- **Persistence layer:**  
  - Implemented with Spring Boot repositories.  
  - Model classes and service layer manage business logic and relational integrity.  

- **Presentation layer:**  
  - Web-based interface using Spring Boot.  
  - Covers at least 5 core use cases with different CRUD operations.  

## Objective / Goal

The goal of this project was to design and implement a modular **web-based platform** that allows administrators and users to manage movies and their relationships with actors and directors, demonstrating the integration of **backend logic, persistence, and user interface**.

## Technologies

- Spring Boot (Java)  
- Thymeleaf / Web templates  
- H2 and relational database (e.g., MySQL)  
- HTML, CSS, JavaScript for frontend forms  

## How to Run

1. Clone the repository.  
2. Import the project into your IDE (e.g., IntelliJ IDEA or Eclipse).  
3. Run the Spring Boot application (`main` class).  
4. Open a browser and navigate to `http://localhost:8080` to access the platform.  
