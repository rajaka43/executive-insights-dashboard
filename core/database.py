"""
Data Layer - Mock Database & Recruitment Data Simulator
Provides encrypted, multi-tenant simulation data for testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

from config.settings import CLIENTS, DEPARTMENTS, PIPELINE_STATES, SIMULATION_CONFIG, RANDOM_SEED

class MockDatabase:
    """
    In-memory simulated database with deterministic data generation
    """
    def __init__(self):
        self._data = self._generate_mock_data()

    def _generate_mock_data(self) -> pd.DataFrame:
        np.random.seed(RANDOM_SEED)
        total_records = SIMULATION_CONFIG['total_records']
        
        # Generate random dates over the last X months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=SIMULATION_CONFIG['date_range_months'] * 30)
        
        date_pool = [start_date + timedelta(days=int(i)) for i in np.random.randint(0, SIMULATION_CONFIG['date_range_months'] * 30, total_records)]
        
        # Probabilities
        status_choices = PIPELINE_STATES
        status_probs = [
            SIMULATION_CONFIG['placement_probability'],
            SIMULATION_CONFIG['interviewing_probability'],
            SIMULATION_CONFIG['screening_probability'],
            SIMULATION_CONFIG['rejected_probability']
        ]
        
        statuses = np.random.choice(status_choices, size=total_records, p=status_probs)
        clients = np.random.choice(CLIENTS, size=total_records)
        departments = np.random.choice(DEPARTMENTS, size=total_records)
        
        # Industry/role matching mock
        days_in_pipeline = np.random.randint(5, 60, total_records)
        
        # Revenues (only for Placed)
        revenue = []
        for status in statuses:
            if status == 'Placed':
                revenue.append(float(np.random.randint(250000, 750000)))
            else:
                revenue.append(0.0)
                
        df = pd.DataFrame({
            'candidate_id': [f"CAN_{1000+i}" for i in range(total_records)],
            'client': clients,
            'department': departments,
            'status': statuses,
            'days_in_pipeline': days_in_pipeline,
            'revenue_lkr': revenue,
            'application_date': [d.strftime('%Y-%m-%d') for d in date_pool]
        })
        
        return df

    def fetch_recruitment_data(self, start_date=None, end_date=None, force_refresh=False) -> pd.DataFrame:
        """
        Fetch filtered data from mock database with support for force refresh
        """
        df = self._data.copy()
        df['application_date'] = pd.to_datetime(df['application_date'])
        
        if start_date:
            df = df[df['application_date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['application_date'] <= pd.to_datetime(end_date)]
            
        return df
        
# Singleton Database instance wrapper
_db_instance = None

def get_database() -> MockDatabase:
    """
    Returns the centralized database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = MockDatabase()
    return _db_instance

