from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '5b14be2a364745a89a95b50f3575f2b419db8bb1ef395d7b548fd5a7ca85e1df')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
