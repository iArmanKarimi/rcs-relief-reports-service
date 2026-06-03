# Iran's Rescue & Relief Service (Django)
Internal Django service for:
- 📊 Importing monthly employee performance reports (Excel)
- 📱 Importing and validating staff contacts
- 🤖 Serving data to Bale bot

## ⚙️ Setup
1️⃣ Clone the project
git clone <repo-url>

cd django-mdaad-service
2️⃣ Create virtual environment
python -m venv venv

source venv/bin/activate   # mac/linux

venv\\Scripts\\activate      # windows
3️⃣ Install dependencies
pip install -r requirements.txt

🔐 Environment Variables
This project uses django-environ.
All sensitive values must be stored in a .env file.
 

Create .env in project root:
DEBUG=True

SECRET_KEY=your-secret-key

BALE_BOT_API_KEY=your-bale-bot-token

ALLOWED_HOSTS=localhost,127.0.0.1
⚠️.env is ignored by Git.
Use .env.example as a template.

## 🗄️ Database
Default database:
SQLite (db.sqlite3)
Run migrations:
python manage.py migrate
Create superuser:
python manage.py createsuperuser

## 🚀 Run Development Server
python manage.py runserver
Admin panel:
http://127.0.0.1:8000/admin/


 

## 📊 Excel Import
#### ✅ Employee Reports Import
- Reads Excel file (first sheet)
- Skips invalid rows
- Normalizes:
- national_id (zero-padding to 10 digits)
- time values (HH:MM)
- Deletes previous reports before inserting new ones (inside atomic
transaction)
- Uses bulk insert for performance
- Logs:
- deleted rows
- prepared rows
- inserted rows
- skipped rows

✅ Staff Contacts Import
Validates:
- national_id → 10 digits
- phone_number → 11 digits (e.g., 0912xxxxxxx)
Skips invalid rows and logs skipped row numbers.
🤖 API & Bale Bot Integration
The backend exposes API endpoints used by the Bale bot to:
- Authenticate users by phone
- Fetch performance reports by phone number
 

Notes
- 	get_report_by_phone extracts phone from request.GET
- 	require_api_key decorator forwards *args and **kwargs
- Bale bot message editing requires capturing message_id from the initial
sendMessage response
Ensure BALE_BOT_API_KEY is correctly set in .env.
🔒 Security Notes
- No secrets are stored in version control.
- All sensitive values must be defined in .env.
- Production deployments must set:
DEBUG=False

✅ Production Checklist
- [ ] Set DEBUG=False
- [ ] Set secure SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Use HTTPS in production
- [ ] Run collectstatic
- [ ] Verify environment variables are set on server
👨‍💻 Maintainer
Internal project.
