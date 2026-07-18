# Student Database Management System — Web Version

A Flask web app for managing student records, courses, and enrollments —
built on the same normalized MySQL schema as the CLI version.

## Features
- Add, view, edit, delete students
- Search students by name
- View course catalog
- Enroll students in courses, update/remove grades
- Clean registry-style UI (navy/amber, serif headers)

## Project Structure
```
student_db_web/
├── app.py              # Flask routes
├── crud.py             # Database operations (same logic as CLI version)
├── db.py               # DB connection (auto-detects Railway env vars)
├── schema.sql           # Database schema + seed data
├── requirements.txt
├── Procfile             # Tells Railway how to run the app
├── .gitignore
├── templates/           # HTML pages
└── static/style.css     # Styling
```

---

## Run Locally First (test before deploying)

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Make sure your local MySQL is running and has the schema
```
mysql -u root -p < schema.sql
```

### 3. Update db.py if your local password differs
Open `db.py`, check the default password matches your local MySQL root password.

### 4. Run the app
```
python app.py
```
Open your browser to **http://localhost:5000**

---

## Deploy to Railway (get a live link)

### 1. Push this folder to GitHub
```
git init
git add .
git commit -m "Student Database Management System - Web version"
git remote add origin https://github.com/gokulrajangamuthu-dotcom/student-db-web.git
git branch -M main
git push -u origin main
```

### 2. Create a Railway project
1. Go to https://railway.app and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `student-db-web` repository

### 3. Add a MySQL database
1. In your Railway project, click **"+ New"** → **"Database"** → **"Add MySQL"**
2. Railway automatically creates the database and injects connection
   variables (`MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`,
   `MYSQLPORT`) into your app's environment — `db.py` is already written
   to read these automatically.

### 4. Load the schema into Railway's MySQL
1. Click on the MySQL service in Railway → **"Connect"** tab
2. Copy the connection command shown (or the individual host/user/password/port)
3. From your computer, run:
```
mysql -h <RAILWAY_HOST> -u <RAILWAY_USER> -p -P <RAILWAY_PORT> <RAILWAY_DATABASE> < schema.sql
```
(Use the values Railway shows you — enter the password when prompted.)

### 5. Set environment variables on your app service
Railway usually auto-links database variables to your app service. If not:
1. Click your **app service** (not the database) → **"Variables"** tab
2. Add a reference to each MySQL variable, or copy the values manually
3. Also add: `SECRET_KEY` = any random string (e.g. `gokul-secret-2026`)

### 6. Deploy
Railway auto-deploys on every `git push`. Once the build finishes, click
**"Settings" → "Generate Domain"** on your app service to get a public URL
like `student-db-web-production.up.railway.app`.

### 7. Test it
Open the generated URL — you should see the same UI you tested locally, now
live for anyone to view.

---

## Notes
- Free Railway usage has monthly credit limits — fine for a portfolio demo,
  but the app may sleep/stop if credits run out.
- Never commit real passwords to GitHub — `db.py` uses environment variables
  specifically so your Railway credentials stay private.
