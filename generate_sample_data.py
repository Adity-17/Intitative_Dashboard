import pandas as pd
import numpy as np
from datetime import datetime

# Sample data
data = {
    'Areas': ['Operations', 'Finance', 'HR', 'IT', 'Operations', 'Finance', 'HR', 'IT', 'Operations', 'Finance'] * 2,
    'Site Initiatives': [
        'Process Automation - Phase 1',
        'Cost Reduction Initiative',
        'Talent Development Program',
        'System Upgrade Project',
        'Waste Reduction Program',
        'Budget Optimization',
        'Recruitment Drive',
        'Cybersecurity Enhancement',
        'Energy Efficiency Program',
        'Financial Consolidation',
        'Skills Training',
        'Cloud Migration',
        'Production Optimization',
        'Expense Management',
        'Employee Retention',
        'Infrastructure Modernization',
        'Supply Chain Optimization',
        'Revenue Enhancement',
        'Workforce Planning',
        'Data Analytics Platform'
    ],
    'Description': [
        'Automation of manual processes to improve efficiency',
        'Reducing operational expenses',
        'Developing employee skills',
        'Upgrading legacy systems',
    ] * 5,
    'Possible Outcomes / Status': np.random.choice(
        ['Completed', 'In Progress', 'On Hold', 'Planning', 'Not Started'],
        20
    ),
    'Expected Savings': np.random.uniform(50000, 500000, 20),
    'ANK': np.random.choice([np.nan, 'Active', 'Planned'], 20),
    'MDP': np.random.choice([np.nan, 'Active', 'Planned'], 20),
    'TAR': np.random.choice([np.nan, 'Active', 'Planned'], 20),
    'Pithampur': np.random.choice([np.nan, 'Active', 'Planned'], 20),
    'External - 1': np.random.choice([np.nan, 'Active', 'Planned'], 20),
    'External - 2': np.random.choice([np.nan, 'Active', 'Planned'], 20),
    'Remarks': [f'Initiative {i}' for i in range(1, 21)]
}

df = pd.DataFrame(data)
df['Expected Savings'] = df['Expected Savings'].apply(lambda x: f'₹{x:,.0f}')

# Save to Excel
df.to_excel('sample_initiatives.xlsx', index=False, engine='openpyxl')
print("Sample data generated: sample_initiatives.xlsx")
