# sentryx-api 

## Description
This project provides a python fastapi interface to access data from sentryyx.io.

## Prerequisites
- Python 3.x
- `pip` (Python package installer)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/jcarter62/sentryx-api.git
cd sentryx-api
```

### 2. Create a Python Virtual Environment
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
- On Windows:
  ```bash
  .\venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 4. Install Required Packages
```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Create a `.env` file in the root directory of the project and add the following environment variables:
```
APIURL=https://api.sentryx.io/v1-wm/sites/
COMPANYID=sentryx-company-id-here
USERNAME=userid@domain.com
APIKEY=put-your-api-key-here

TITLE=Sentryx API
CONTACT_NAME=John Doe
CONTACT_EMAIL=jd@go.com

SQLSERVER=sql-svr
INSTANCE=sql-instance
DATABASE=sql-db
UID=sql-user
PASSWORD=sql-password

AMI_CODE=TC0041

```
There is a sample.env file available as a template in the project.

### 6. Run the Application
```bash
uvicorn main:app
```

## Usage
Visit the url 'http://...:8000/docs' to see the API documentation.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
