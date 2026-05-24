Django Mdaad Service

A high-performance Django-based service designed for managing and reporting Iranian Rescue & Relief personnel performance.

## Setup Instructions

Clone the Repository

py -m venv venv
.\venv\Scripts\Activate.ps1


3. Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

Configure Environment Variables:
```
DEBUG=False
SECRET_KEY=<your-secret-key>
BALE_BOT_API_KEY=<your-bale-bot-api-key>
```

```cmd
python manage.py migrate
python manage.py collectstatic
```

Run the Application:
`python manage.py runserver`


### Key Implementation Details
- **User Persistence**: We use `user.id` as the permanent unique identifier for all personnel records, ensuring data consistency across the service. This requires changing API service. removes the need for auth to get personnel reports.
- **Audit Logging**: Integrated `django-simple-history` to track all model changes, providing a full audit trail for performance reporting.