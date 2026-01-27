# Requirements Document

## Introduction

The Skill Gap Analyzer is a full-stack web application that helps students and professionals identify skill gaps for specific job roles. The system analyzes user skills against a dataset of job roles to provide personalized recommendations and gap analysis reports.

## Glossary

- **System**: The Skill Gap Analyzer web application
- **User**: Students or professionals using the application
- **Skill_Dataset**: Collection of job roles and their required skills stored in MongoDB
- **User_Profile**: Individual user account with stored skills and analysis history
- **Role_Matcher**: Component that matches user skills against job role requirements
- **Resume_Parser**: Component that extracts skills from uploaded resume files
- **Skill_Validator**: Component that cleans and validates extracted skills
- **Report_Generator**: Component that creates exportable skill gap reports
- **Auth_System**: JWT-based authentication and session management system

## Requirements

### Requirement 1: User Authentication System

**User Story:** As a user, I want to create an account and securely log in, so that I can access personalized skill gap analysis.

#### Acceptance Criteria

1. WHEN a user provides valid signup information (name, email, password), THE Auth_System SHALL create a new user account with hashed password
2. WHEN a user provides valid login credentials, THE Auth_System SHALL generate a JWT token and establish a session
3. WHEN a user provides invalid credentials, THE Auth_System SHALL reject the login attempt and return an error message
4. WHEN a JWT token expires, THE Auth_System SHALL require re-authentication
5. THE Auth_System SHALL store user profiles securely in MongoDB with password hashing

### Requirement 2: User Profile Management

**User Story:** As a user, I want to view and update my profile information, so that I can maintain accurate personal data for analysis.

#### Acceptance Criteria

1. WHEN a user accesses their profile, THE System SHALL display current profile information including name, email, and stored skills
2. WHEN a user updates profile information, THE System SHALL validate and save changes to MongoDB
3. WHEN a user uploads a resume, THE System SHALL store the file path in the user profile
4. THE System SHALL track skill sources (manual entry vs resume extraction) in the user profile
5. WHEN profile updates occur, THE System SHALL maintain data integrity and update timestamps

### Requirement 3: Skill Gap Education Interface

**User Story:** As a visitor, I want to understand what skill gaps are and how the system helps, so that I can make an informed decision to use the application.

#### Acceptance Criteria

1. WHEN a visitor accesses the landing page, THE System SHALL display educational content about skill gaps and career development
2. WHEN educational content is displayed, THE System SHALL include clear explanations of how the system benefits users
3. WHEN a visitor wants to proceed, THE System SHALL provide prominent call-to-action buttons for login and signup
4. THE System SHALL present information in a student-friendly, accessible format

### Requirement 4: Manual Skill Entry System

**User Story:** As a user, I want to manually enter my skills using an intuitive interface, so that I can build my skill profile accurately.

#### Acceptance Criteria

1. WHEN a user accesses skill entry, THE System SHALL provide a searchable dropdown populated with all Skill_Dataset skills
2. WHEN a user searches for skills, THE System SHALL filter and display matching skills from the dataset
3. WHEN a user selects skills, THE System SHALL support multi-select functionality and display selected skills
4. WHERE a skill is not in the dataset, THE System SHALL allow users to add custom skills
5. WHEN a user wants to remove skills, THE System SHALL provide removal functionality for selected skills
6. WHEN skill entry is complete, THE System SHALL save skills to MongoDB with manual entry source tracking

### Requirement 5: Resume Upload and Parsing System

**User Story:** As a user, I want to upload my resume and have skills automatically extracted, so that I can quickly populate my skill profile.

#### Acceptance Criteria

1. WHEN a user uploads a resume file, THE Resume_Parser SHALL support PDF, DOCX, and TXT formats
2. WHEN parsing resumes, THE Resume_Parser SHALL extract skills only from "Skills" or "Technical Skills" sections
3. WHEN parsing resumes, THE Resume_Parser SHALL extract experience keywords (Internship, Training, Full-time, Project)
4. WHEN skills are extracted, THE Skill_Validator SHALL filter extracted skills against the Skill_Dataset
5. WHEN extraction is complete, THE System SHALL present extracted skills for user validation and editing
6. IF parsing fails or no skills are found, THEN THE System SHALL provide clear feedback and fallback to manual entry

### Requirement 6: Skill Cleaning and Validation System

**User Story:** As a user, I want my skills to be cleaned and validated automatically, so that my profile contains accurate, standardized skill data.

#### Acceptance Criteria

1. WHEN skills are processed, THE Skill_Validator SHALL remove duplicate skills from the user's skill list
2. WHEN skills are processed, THE Skill_Validator SHALL normalize skill names using standard mappings (js → javascript)
3. WHEN validation is complete, THE System SHALL provide a user interface to review and remove incorrect skills
4. WHEN users identify missing skills, THE System SHALL allow manual addition of skills not detected during parsing
5. THE Skill_Validator SHALL maintain data quality by ensuring consistent skill naming conventions

### Requirement 7: Experience Detection and Weighting System

**User Story:** As a user, I want the system to detect my experience level and weight recommendations accordingly, so that I receive appropriate role suggestions.

#### Acceptance Criteria

1. WHEN analyzing resumes, THE System SHALL detect experience level indicators (Internship, Fresher, Experienced)
2. WHEN experience is detected, THE Role_Matcher SHALL weight role recommendations based on experience level
3. WHEN experience data is determined, THE System SHALL store experience information in the User_Profile
4. THE System SHALL use experience weighting to prioritize suitable roles over aspirational roles

### Requirement 8: Role Matching Engine

**User Story:** As a user, I want to see which job roles match my skills and by what percentage, so that I can identify suitable career opportunities.

#### Acceptance Criteria

1. WHEN role matching is requested, THE Role_Matcher SHALL compare user skills against all roles in the Skill_Dataset
2. WHEN calculating matches, THE Role_Matcher SHALL compute match percentages based on skill overlap
3. WHEN matches are calculated, THE System SHALL provide the top 5 most suitable roles ranked by match percentage
4. WHEN displaying matches, THE System SHALL distinguish between essential skill matches and overall skill matches
5. WHEN presenting results, THE System SHALL use a star rating system (1-5 stars) to indicate match quality

### Requirement 9: Skill Importance Analysis System

**User Story:** As a user, I want to understand which skills are common across companies versus role-specific, so that I can prioritize my learning effectively.

#### Acceptance Criteria

1. WHEN analyzing skills, THE System SHALL identify common company skills that appear across many roles
2. WHEN analyzing skills, THE System SHALL identify role-specific booster skills unique to particular roles
3. WHEN calculating importance, THE System SHALL use TF-IDF style analysis to determine skill significance
4. WHEN presenting analysis, THE System SHALL clearly distinguish between common and role-specific skills

### Requirement 10: Grouped Skill Display System

**User Story:** As a user, I want to see missing skills organized by categories, so that I can understand my skill gaps in a structured way.

#### Acceptance Criteria

1. WHEN displaying skill gaps, THE System SHALL group missing skills by categories (Programming, DevOps, ML, etc.)
2. WHEN presenting grouped skills, THE System SHALL use clear, organized formatting suitable for students
3. WHEN skill gaps are shown, THE System SHALL provide easy-to-understand visualizations of missing competencies
4. THE System SHALL present skill gap information in a way that facilitates learning prioritization

### Requirement 11: Role Override Feature

**User Story:** As a user, I want to analyze different roles beyond my top matches, so that I can explore various career paths.

#### Acceptance Criteria

1. WHEN users want to explore roles, THE System SHALL provide a dropdown selection for role switching
2. WHEN a different role is selected, THE System SHALL perform instant gap analysis for the selected role
3. WHEN role override is used, THE System SHALL maintain the same analysis quality as automatic matching
4. THE System SHALL allow users to analyze any role in the Skill_Dataset regardless of their current match percentage

### Requirement 12: Report Generation System

**User Story:** As a user, I want to export my skill gap analysis in various formats, so that I can share results or use them for planning.

#### Acceptance Criteria

1. WHEN report generation is requested, THE Report_Generator SHALL create skill gap reports in TXT and PDF formats
2. WHEN exporting missing skills, THE Report_Generator SHALL generate CSV files with missing skills data
3. WHEN exporting matched skills, THE Report_Generator SHALL create downloadable lists of matched skills
4. WHEN reports are generated, THE System SHALL ensure all exports contain accurate, up-to-date analysis data

### Requirement 13: Database Storage and Management

**User Story:** As a system administrator, I want all data to be stored reliably in MongoDB, so that user data and analysis history are preserved.

#### Acceptance Criteria

1. WHEN users are created, THE System SHALL store user profiles securely in MongoDB collections
2. WHEN skills are entered or extracted, THE System SHALL persist skill data with source tracking
3. WHEN analyses are performed, THE System SHALL store analysis history for future reference
4. WHEN the system initializes, THE System SHALL maintain the Skill_Dataset with roles and required skills
5. THE System SHALL ensure data consistency and integrity across all MongoDB operations