"""Configuration pour MongoDB"""
from typing import Dict, Any
import os

def get_mongodb_config() -> Dict[str, Any]:
    """Retourne la configuration MongoDB"""
    return {
        'mongodb': {
            'auth': {
                'enabled': True,
                'mechanism': 'SCRAM-SHA-256',
                'source': 'admin',
                'credentials': {
                    'username': os.getenv('MONGODB_USERNAME', 'test_user'),
                    'password': os.getenv('MONGODB_PASSWORD', 'test_password')
                }
            },
            'connection': {
                'host': os.getenv('MONGODB_HOST', 'localhost'),
                'port': int(os.getenv('MONGODB_PORT', '27018')),
                'database': os.getenv('MONGODB_DATABASE', 'chatbot_db')
            }
        }
    }