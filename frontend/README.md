# frontend

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### backend setup

cd backend

### Create Virtual Environment & Activate

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

### Install Dependencies
 Install Dependencies

 #run server 
 flask run / python app.py


### Background task 

redis-server
celery -A celery_worker.celery worker --loglevel=info
### Reminders 
cd quizz-backend
source env/bin/activate
flask shell
>>> from tasks import send_daily_reminders
>>> send_daily_reminders.delay()
from tasks import send_monthly_activity_report
send_monthly_activity_report.delay()

# Check caching
redis-cli
KEYS *