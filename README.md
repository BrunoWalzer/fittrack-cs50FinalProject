# FitTrack - Gym Workout Tracker

#### Video Demo: (https://youtu.be/ajc5LW1e0vM)

## Description

FitTrack is a comprehensive full-stack web application designed to help gym enthusiasts track their workouts, monitor progress, and maintain consistency with their fitness goals. Built from the ground up using Flask, SQLite, HTML, CSS, and JavaScript, this application demonstrates modern web development practices while solving a real-world problem.

As someone who regularly goes to the gym, I found myself frustrated with overly complex fitness apps filled with features I never used, or apps that required expensive subscriptions. I wanted a simple, straightforward tool to track my workouts and visualize my progress over time. FitTrack addresses this need by focusing on the essentials: creating workout programs, logging exercises with sets, reps, and weight, and maintaining a visual record of training consistency.

## Features

### 🔐 User Authentication
- **Secure Registration & Login**: Users create accounts with email and password
- **Password Hashing**: All passwords are hashed using Werkzeug's security functions before storage
- **Session Management**: Flask sessions keep users logged in securely across requests
- **Data Isolation**: Each user can only access their own workout data

### 🏋️ Workout Management
- **Create Multiple Programs**: Users can create different workout programs (Push Day, Pull Day, Leg Day, etc.)
- **Add Exercises**: Each workout program contains multiple exercises
- **Muscle Group Classification**: Exercises are organized by muscle groups (Chest, Back, Shoulders, Biceps, Triceps, Legs, Abs)
- **Edit & Delete**: Full control over workout programs and exercises

### 📝 Training Sessions
- **Historical Data Display**: When starting a workout, the app shows your previous performance (last sets, reps, and weight used)
- **Progressive Overload**: Seeing previous records helps users progressively increase their training load
- **Quick Data Entry**: Input fields are pre-populated with last workout's values for convenience
- **Automatic Saving**: All workout data is saved with timestamps for accurate tracking

### 📊 Progress Tracking
- **Training Calendar**: Visual calendar showing which days you trained and which you missed
- **Monthly Statistics**: Dashboard displays the number of workouts completed in the current month
- **Detailed History**: Complete history page showing all past workouts with expandable details
- **Exercise Progression**: Dedicated page for each exercise showing all records, max weight, and average weight
- **Interactive Visualization**: Click any trained day on the calendar to see complete workout details

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with a red and white color scheme
- **Responsive Layout**: Fully responsive design that works on desktop, tablet, and mobile devices
- **Intuitive Navigation**: Easy-to-use interface with clear call-to-action buttons
- **Smooth Animations**: Subtle hover effects and transitions enhance user experience
- **Modal Dialogs**: Clean modal popups for workout details and confirmations

## Technology Stack

### Backend
- **Flask**: Python web framework for routing and server-side logic
- **SQLite**: Lightweight relational database for data persistence
- **Werkzeug**: For password hashing and security utilities
- **Python datetime**: For handling dates and timestamps

### Frontend
- **HTML5**: Semantic markup for structure
- **CSS3**: Modern styling with Grid and Flexbox layouts
- **Vanilla JavaScript**: Client-side interactivity without frameworks
- **Fetch API**: Asynchronous data loading for calendar details

### Database Schema
The application uses five related tables:

- **users**: Stores user accounts (id, name, email, password_hash)
- **workouts**: Workout programs linked to users (id, user_id, name)
- **exercises**: Individual exercises in each workout (id, workout_id, name, muscle_group)
- **records**: Training records with performance data (id, exercise_id, date, sets, reps, weight)
- **training_days**: Days when workouts were completed (id, user_id, date, workout_id, completed)

## Project Structure

```
fittrack/
├── app.py                      # Main Flask application
├── database.db                 # SQLite database (auto-generated)
├── requirements.txt            # Python dependencies
├── static/
│   ├── style.css              # Complete CSS styling
│   └── script.js              # Client-side JavaScript
└── templates/
    ├── base.html              # Base template with navigation
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── dashboard.html         # Main dashboard with calendar
    ├── workout_new.html       # Create new workout
    ├── workout_detail.html    # View/edit workout exercises
    ├── train.html             # Log workout session
    ├── history.html           # Complete workout history
    └── exercise_history.html  # Individual exercise progression
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
```bash
git clone [your-repository-url]
cd fittrack
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the application**
```
Open your browser and navigate to: http://localhost:5000
```

The database will be created automatically on first run.

## Usage Guide

### Getting Started
1. **Register an account**: Create a new account with your name, email, and password
2. **Login**: Sign in with your credentials
3. **Create a workout program**: Click "New Workout" and give it a name (e.g., "Workout A - Push")
4. **Add exercises**: Add exercises to your workout, specifying the muscle group for each

### Logging a Workout
1. **Start training**: Click "Train Now" on any workout card
2. **Review previous data**: See your last performance for each exercise
3. **Enter current data**: Input today's sets, reps, and weight
4. **Complete workout**: Submit to save all data

### Tracking Progress
1. **Calendar view**: See at a glance which days you trained
2. **Click trained days**: View complete details of any past workout
3. **History page**: Browse all workouts with expandable details
4. **Exercise history**: Click "View History" on any exercise to see progression over time

## Design Decisions

### Why Flask?
I chose Flask for its simplicity and flexibility. It's lightweight yet powerful enough to handle user authentication, database operations, and RESTful API endpoints. Flask's decorator-based routing makes the code readable and maintainable.

### Why SQLite?
SQLite is perfect for this application because:
- No separate server setup required
- Ideal for single-user or small-scale deployment
- Excellent performance for this use case
- Entire database in a single file for easy backup
- Built-in support in Python

### Why Show Previous Records?
Progressive overload is a fundamental principle in strength training. By showing users their previous performance, the app makes it easy to ensure they're consistently challenging themselves and making progress.

### Why Calendar Visualization?
Consistency is key in fitness. The calendar provides immediate visual feedback about training frequency, which can be a powerful motivator. Seeing a streak of trained days encourages users to maintain their routine.

### Database Relationships
The database uses proper foreign keys to maintain referential integrity:
- One user has many workouts
- One workout has many exercises
- One exercise has many records
- Cascading deletes prevent orphaned data

### Security Considerations
- **Password Hashing**: Passwords are never stored in plain text
- **Session-based Auth**: Secure session management with Flask
- **User Data Isolation**: Database queries always filter by user_id
- **Input Validation**: Server-side validation for all user inputs

## Key Features Explained

### Interactive Calendar
The calendar is dynamically generated using JavaScript. It:
- Displays one month at a time with navigation arrows
- Highlights the current day
- Shows trained days in red with gradient effects
- Loads workout details asynchronously when a day is clicked
- Handles different month lengths and leap years correctly

### Exercise History Tracking
Each exercise maintains a complete history of all performances:
- Date of each workout
- Sets, reps, and weight used
- Calculated total volume (sets × reps × weight)
- Statistical summaries (max weight, average weight, total workouts)

### Collapsible History
The history page uses JavaScript to create expandable workout entries:
- Cleaner initial view without overwhelming information
- Click to expand and see all exercise details
- Maintains the same visual design as the calendar modal
- Smooth CSS transitions for better UX

## Technical Highlights

### Backend Architecture
- RESTful API design with clear endpoint structure
- Separation of concerns (routing, database, logic)
- Efficient database queries with proper JOINs
- Error handling and validation
- Session management for user state

### Frontend Implementation
- Vanilla JavaScript (no framework dependencies)
- Dynamic DOM manipulation for calendar generation
- Asynchronous data fetching with error handling
- CSS Grid for responsive layouts
- CSS custom properties for consistent theming

### Database Operations
- Five interconnected tables with foreign key relationships
- Proper indexing on frequently queried columns
- Transaction safety for multi-step operations
- Cascading deletes for data integrity
- Date-based queries for historical data

## Future Enhancements

While the current version is fully functional, potential improvements could include:
- **Progress Charts**: Visual graphs showing weight progression over time
- **Body Metrics**: Track weight, body fat percentage, and measurements
- **Workout Templates**: Pre-made programs for different goals
- **Rest Timer**: Built-in countdown timer for rest periods
- **Exercise Library**: Searchable database of exercises with instructions
- **Export Data**: Download workout history as CSV or PDF
- **Social Features**: Share progress with friends or coaches

## Challenges & Solutions

### Challenge 1: Calendar Date Handling
**Problem**: JavaScript Date objects can be tricky with timezones and string formatting.
**Solution**: Consistently use ISO date strings (YYYY-MM-DD) and add 'T00:00:00' when creating Date objects to avoid timezone issues.

### Challenge 2: Responsive Design
**Problem**: Making the calendar grid work on all screen sizes.
**Solution**: Used CSS Grid with responsive breakpoints, adjusted font sizes and spacing for mobile devices, and implemented flexible layouts.

### Challenge 3: Displaying Historical Data
**Problem**: Efficiently showing previous workout data when training.
**Solution**: Created a SQL query that fetches the last 3 records per exercise and passes them to the template, pre-populating form fields with the most recent values.

### Challenge 4: Modal Interactions
**Problem**: Loading detailed workout information without page reload.
**Solution**: Implemented a REST API endpoint that returns JSON data, which is fetched asynchronously and rendered in a modal dialog.

## Learning Outcomes

Through building FitTrack, I gained experience with:
- Full-stack web development (frontend + backend + database)
- RESTful API design and implementation
- User authentication and session management
- Database design with proper relationships
- Responsive web design principles
- Asynchronous JavaScript programming
- Security best practices (password hashing, input validation)
- Git version control and project organization

## Credits

This project was created as the final project for CS50x - Introduction to Computer Science.

**Developer**: Bruno De Negri Walzer
**Course**: CS50x 2025
**Institution**: Harvard University

## License

This project is open source and available for educational purposes.

---

**Note**: This application is designed for personal use. For production deployment, additional security measures and scalability considerations would be necessary.
