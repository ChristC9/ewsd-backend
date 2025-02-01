# **EWSD Project - Backend**  

## **Prerequisites**  
Ensure you have the following installed before proceeding:  
- **Python** ≥ 3.10  
- **Pip** (Python package manager)  
- **Docker & Docker Compose** (for database containerization)  

## **Database Setup**  

### **Setting Up the Database Locally**  
1. **Start PostgreSQL using Docker Compose**  
   ```sh
   docker compose up -d
   ```  
   > This runs PostgreSQL in a container in detached mode (`-d`).  

2. **Initialize the Database with Alembic**  
   ```sh
   alembic init alembic
   alembic revision --autogenerate -m "Initial database setup"
   alembic upgrade head
   ```  
   > This sets up database migrations using **Alembic**.  

3. **Copy `env.py`**  
    Please copy `resources/env.py` to `alembic/env.py`.  
    
## **Running the Application**  
To start the backend application, run:  
```sh
python main.py
```  