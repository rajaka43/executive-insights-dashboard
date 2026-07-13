"""
Global Configuration & KPI Targets
Centralized settings for the Gamage Recruiters Executive Dashboard
"""

import os
from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database Configuration
DATABASE_CONFIG = {
    'encryption_enabled': True,
    'multi_tenant_mode': True,
    'connection_pool_size': 10,
    'timeout': 30
}

# Revenue Configuration (LKR - Sri Lankan Rupees)
REVENUE_CONFIG = {
    'currency': 'LKR',
    'currency_symbol': 'Rs.',
    'placement_base_fee': 250000,  # Base placement fee
    'placement_fee_range': (200000, 800000),  # Min-Max range
    'commission_rate': 0.15  # 15% commission on placements
}

# KPI Targets (Executive Benchmarks)
KPI_TARGETS = {
    'monthly_placements': 35,
    'monthly_revenue': 8750000,  # LKR 8.75M
    'avg_time_to_hire_days': 28,
    'active_pipeline_min': 120,
    'conversion_rate': 0.25,  # 25% screening to placement
    'client_satisfaction': 4.5  # out of 5
}

# Candidate Pipeline States
PIPELINE_STATES = [
    'Placed',
    'Interviewing',
    'Screening',
    'Rejected'
]

# Department Categories
DEPARTMENTS = [
    'Technology',
    'Finance',
    'Marketing',
    'Operations',
    'Human Resources',
    'Sales',
    'Legal',
    'Customer Service'
]

# Client Pool (Mock Recruitment Clients)
CLIENTS = [
    'Tech Innovations Lanka',
    'Ceylon Banking Group',
    'Digital Marketing Hub',
    'Global Logistics Pvt Ltd',
    'FinTech Solutions',
    'Healthcare Systems Inc',
    'Retail Giants LK',
    'Manufacturing Excellence',
    'Consulting Partners',
    'E-Commerce Leaders',
    'Insurance Corp',
    'Telecom Networks',
    'Energy Solutions',
    'Hospitality Group',
    'Education Institutions'
]

# UI Theme Configuration
UI_THEME = {
    'primary_color': '#1e3a5f',  # Dark Navy
    'secondary_color': '#4a6fa5',  # Slate Blue
    'accent_color': '#e63946',  # Red for alerts
    'success_color': '#06d6a0',  # Teal for positive metrics
    'background_color': '#f8f9fa',
    'card_background': '#ffffff',
    'text_primary': '#212529',
    'text_secondary': '#6c757d'
}

# Reporting Configuration
REPORT_CONFIG = {
    'weekly_report_day': 'Monday',
    'report_recipients': [
        'ceo@gamagerecruiters.lk',
        'cfo@gamagerecruiters.lk',
        'operations@gamagerecruiters.lk'
    ],
    'pdf_storage_path': BASE_DIR / 'reports' / 'generated',
    'email_enabled': False  # Set to True in production with SMTP config
}

# SMTP Configuration (Production)
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'use_tls': True
}

# Date Range Configuration
DATE_CONFIG = {
    'historical_months': 6,
    'forecast_months': 3
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'excellent_time_to_hire': 21,  # days
    'good_time_to_hire': 28,
    'poor_time_to_hire': 45,
    'high_revenue_placement': 600000,  # LKR
    'low_revenue_placement': 250000
}

# Data Generation Seeds (for reproducibility)
RANDOM_SEED = 42
SIMULATION_CONFIG = {
    'total_records': 1400,
    'date_range_months': 6,
    'placement_probability': 0.22,
    'interviewing_probability': 0.18,
    'screening_probability': 0.35,
    'rejected_probability': 0.25
}