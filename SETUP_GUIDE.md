# Setup Guide - Dashboard Monitoring Pembiayaan Petani Tebu KUR

## Quick Start Guide

### 1. Installation

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

#### Step-by-Step Installation

1. **Create a Virtual Environment** (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. **Install Required Packages**
```bash
pip install -r requirements.txt
```

3. **Run the Dashboard**
```bash
streamlit run sugarcane_finance_dashboard.py
```

4. **Access the Dashboard**
- Open your browser
- Navigate to: http://localhost:8501

### 2. Configuration

#### Database Configuration (config.py)
Create a file named `config.py` in the same directory:

```python
# config.py
import os

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'kur_database'),
    'user': os.getenv('DB_USER', 'your_username'),
    'password': os.getenv('DB_PASSWORD', 'your_password')
}

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'sender_email': os.getenv('SENDER_EMAIL', 'your_email@company.com'),
    'sender_password': os.getenv('SENDER_PASSWORD', 'your_password'),
    'recipient_list': ['manager@company.com', 'director@company.com']
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    'npl_rate_high': 5.0,  # NPL > 5% triggers high alert
    'npl_rate_target': 3.0,  # NPL target < 3%
    'collection_rate_min': 90.0,  # Minimum collection rate
    'payment_due_days': 30,  # Alert for payments due in 30 days
    'price_fluctuation': 10.0  # Price change > 10% triggers alert
}

# Business Rules
BUSINESS_RULES = {
    'max_loan_amount': 500000000,  # 500 million Rupiah
    'min_collateral_coverage': 120,  # 120% collateral coverage
    'max_npr_regional': 5.0,  # Maximum NPL per region
    'target_annual_disbursement': 15000000000000  # 15 Trillion target
}

# Regional Configuration
REGIONS = [
    'Jawa Timur',
    'Jawa Tengah', 
    'Lampung',
    'Sumatera Selatan',
    'Sulawesi Selatan',
    'Sumatera Utara',
    'Bali',
    'Nusa Tenggara Barat'
]

# Loan Types
LOAN_TYPES = ['KUR', 'KUR Khusus']

# Planting Seasons
PLANTING_SEASONS = [
    'Musim Tanam 1 (Jan-Jun)',
    'Musim Tanam 2 (Jul-Des)'
]

# Banks
PARTNER_BANKS = [
    'BRI',
    'BNI',
    'Bank Mandiri',
    'BTN',
    'Bank Syariah Indonesia'
]
```

#### Environment Variables (.env)
Create a `.env` file for sensitive information:

```bash
# .env
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=kur_database
DB_USER=your_username
DB_PASSWORD=your_secure_password

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=notifications@company.com
SENDER_PASSWORD=your_email_password

# API Keys (if needed)
WEATHER_API_KEY=your_weather_api_key
PRICE_API_KEY=your_price_api_key
```

### 3. Database Setup

#### PostgreSQL Example Schema
```sql
-- Create main loans table
CREATE TABLE loans (
    loan_id VARCHAR(50) PRIMARY KEY,
    borrower_id VARCHAR(50) NOT NULL,
    loan_type VARCHAR(20) NOT NULL,  -- 'KUR' or 'KUR Khusus'
    disbursement_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    disbursed_amount DECIMAL(15,2) NOT NULL,
    outstanding_balance DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2),
    region VARCHAR(100),
    bank VARCHAR(50),
    status VARCHAR(20),  -- 'Active', 'Closed', 'Default'
    collectibility_category INT,  -- 1-5 (1=Lancar, 5=Macet)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create borrowers table
CREATE TABLE borrowers (
    borrower_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    id_number VARCHAR(20) UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    region VARCHAR(100),
    farmer_group VARCHAR(200),
    experience_years INT,
    land_area_ha DECIMAL(10,2),
    land_ownership VARCHAR(20),  -- 'Own', 'Rent', 'Mixed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create payments table
CREATE TABLE payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    loan_id VARCHAR(50) REFERENCES loans(loan_id),
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(15,2) NOT NULL,
    principal_amount DECIMAL(15,2),
    interest_amount DECIMAL(15,2),
    late_days INT DEFAULT 0,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create productivity table
CREATE TABLE productivity (
    productivity_id VARCHAR(50) PRIMARY KEY,
    borrower_id VARCHAR(50) REFERENCES borrowers(borrower_id),
    harvest_date DATE,
    land_area_ha DECIMAL(10,2),
    harvest_amount_ton DECIMAL(10,2),
    productivity_ton_per_ha DECIMAL(10,2),
    market_price_per_kg DECIMAL(10,2),
    total_revenue DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create alerts table
CREATE TABLE alerts (
    alert_id VARCHAR(50) PRIMARY KEY,
    alert_type VARCHAR(50),
    priority VARCHAR(20),  -- 'High', 'Medium', 'Low'
    loan_id VARCHAR(50) REFERENCES loans(loan_id),
    message TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_loans_disbursement_date ON loans(disbursement_date);
CREATE INDEX idx_loans_region ON loans(region);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_payments_loan_id ON payments(loan_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
```

### 4. Data Integration

#### Option A: Direct Database Connection
Modify the dashboard to connect to your database:

```python
import psycopg2
import pandas as pd
from config import DB_CONFIG

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_portfolio_data():
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
        SELECT 
            DATE_TRUNC('month', disbursement_date) as bulan,
            loan_type,
            SUM(CASE WHEN status = 'Active' THEN disbursed_amount ELSE 0 END) as disbursed,
            SUM(outstanding_balance) as outstanding
        FROM loans
        WHERE disbursement_date >= DATE_TRUNC('year', CURRENT_DATE)
        GROUP BY bulan, loan_type
        ORDER BY bulan
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    return df
```

#### Option B: CSV Import
```python
@st.cache_data
def load_portfolio_data():
    df = pd.read_csv('data/portfolio_data.csv')
    df['Bulan'] = pd.to_datetime(df['Bulan'])
    return df
```

#### Option C: API Integration
```python
import requests

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_portfolio_data():
    response = requests.get(
        'https://your-api.com/loans/portfolio',
        headers={'Authorization': f'Bearer {API_TOKEN}'}
    )
    
    data = response.json()
    df = pd.DataFrame(data)
    return df
```

### 5. Deployment Options

#### Option 1: Streamlit Cloud (Recommended for Quick Start)
1. Push code to GitHub
2. Visit https://share.streamlit.io
3. Connect your GitHub repository
4. Deploy with one click
5. Add secrets in the dashboard settings

#### Option 2: Docker Deployment
Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "sugarcane_finance_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t kur-dashboard .
docker run -p 8501:8501 kur-dashboard
```

#### Option 3: Linux Server Deployment
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx

# Setup application
git clone your-repo
cd your-repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/kur-dashboard.service
```

Systemd service file:
```ini
[Unit]
Description=KUR Dashboard
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/app/venv/bin"
ExecStart=/path/to/app/venv/bin/streamlit run sugarcane_finance_dashboard.py

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable kur-dashboard
sudo systemctl start kur-dashboard
```

### 6. Security Best Practices

#### Authentication (Optional)
Add user authentication:

```python
import streamlit_authenticator as stauth

# In your dashboard
names = ['Admin User', 'Manager', 'Analyst']
usernames = ['admin', 'manager', 'analyst']
passwords = ['xxx', 'xxx', 'xxx']  # Use hashed passwords

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    'kur_dashboard', 'auth_key', cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show dashboard
    st.write(f'Welcome *{name}*')
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

#### Data Encryption
```python
from cryptography.fernet import Fernet

# Generate key (do this once and store securely)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt sensitive data
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

# Decrypt when needed
def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data).decode()
```

### 7. Testing

Create test file `test_dashboard.py`:

```python
import pytest
import pandas as pd
from sugarcane_finance_dashboard import generate_sample_data

def test_data_generation():
    portfolio, regional, aging, segment = generate_sample_data()
    
    assert not portfolio.empty
    assert not regional.empty
    assert len(regional) > 0
    
def test_npl_calculation():
    # Add your NPL calculation tests
    pass

def test_data_validation():
    # Add your data validation tests
    pass
```

Run tests:
```bash
pytest test_dashboard.py
```

### 8. Maintenance

#### Regular Tasks:
1. **Daily:**
   - Monitor dashboard performance
   - Check for alert triggers
   - Verify data synchronization

2. **Weekly:**
   - Review NPL trends
   - Update regional performance
   - Check system logs

3. **Monthly:**
   - Generate compliance reports
   - Update thresholds if needed
   - Review user feedback

4. **Quarterly:**
   - System security audit
   - Performance optimization
   - Feature updates

### 9. Troubleshooting

#### Common Issues:

**Problem: Dashboard loads slowly**
Solution:
```python
# Increase cache time
@st.cache_data(ttl=7200)  # 2 hours

# Optimize queries
# Use pagination for large datasets
# Implement lazy loading
```

**Problem: Database connection errors**
Solution:
```python
# Add connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@host/db',
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

**Problem: Memory issues**
Solution:
```python
# Process data in chunks
chunksize = 10000
for chunk in pd.read_sql(query, conn, chunksize=chunksize):
    process_chunk(chunk)
```

### 10. Support

For additional help:
- Email: support@your-company.com
- Documentation: https://your-docs-site.com
- Issue Tracker: https://github.com/your-repo/issues

### 11. License & Credits

This dashboard template is designed for LPP Agro Nusantara's Digital Transformation Team.

For questions or customization requests, contact the development team.
