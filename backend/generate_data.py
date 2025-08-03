import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_kansas_claims_data(years=10):
    """Generate realistic Kansas health claims data"""
    
    # All 105 Kansas counties with populations
    kansas_counties = {
        'Johnson': {'pop': 600000, 'type': 'urban', 'metro': 'Kansas City'},
        'Sedgwick': {'pop': 520000, 'type': 'urban', 'metro': 'Wichita'},
        'Shawnee': {'pop': 180000, 'type': 'urban', 'metro': 'Topeka'},
        'Wyandotte': {'pop': 165000, 'type': 'urban', 'metro': 'Kansas City'},
        'Douglas': {'pop': 120000, 'type': 'mixed', 'metro': 'Lawrence'},
        'Leavenworth': {'pop': 82000, 'type': 'mixed', 'metro': 'Kansas City'},
        'Butler': {'pop': 67000, 'type': 'mixed', 'metro': None},
        'Ford': {'pop': 34000, 'type': 'rural', 'metro': None},
        'Finney': {'pop': 36000, 'type': 'rural', 'metro': None},
        'Harvey': {'pop': 35000, 'type': 'rural', 'metro': None},
        'Riley': {'pop': 72000, 'type': 'mixed', 'metro': 'Manhattan'},
        'Reno': {'pop': 61000, 'type': 'mixed', 'metro': None},
        'Saline': {'pop': 54000, 'type': 'mixed', 'metro': None},
        'Crawford': {'pop': 38500, 'type': 'rural', 'metro': None},
        'Bourbon': {'pop': 14400, 'type': 'rural', 'metro': None},
        'Miami': {'pop': 34000, 'type': 'rural', 'metro': 'Kansas City'},
        'Franklin': {'pop': 25200, 'type': 'rural', 'metro': None},
        'Lyon': {'pop': 32000, 'type': 'rural', 'metro': None},
        'Coffey': {'pop': 8300, 'type': 'rural', 'metro': None},
        'Anderson': {'pop': 7800, 'type': 'rural', 'metro': None},
        'Cherokee': {'pop': 20000, 'type': 'rural', 'metro': None},
        'Labette': {'pop': 20000, 'type': 'rural', 'metro': None},
        'Montgomery': {'pop': 31500, 'type': 'rural', 'metro': None},
        'Wilson': {'pop': 8700, 'type': 'rural', 'metro': None},
        'Neosho': {'pop': 16000, 'type': 'rural', 'metro': None},
        'Allen': {'pop': 12500, 'type': 'rural', 'metro': None},
        'Woodson': {'pop': 3100, 'type': 'rural', 'metro': None},
        'Greenwood': {'pop': 6200, 'type': 'rural', 'metro': None},
        'Elk': {'pop': 2500, 'type': 'rural', 'metro': None},
        'Chautauqua': {'pop': 3500, 'type': 'rural', 'metro': None},
        'Cowley': {'pop': 34500, 'type': 'rural', 'metro': None},
        'Sumner': {'pop': 22800, 'type': 'rural', 'metro': None},
        'Harper': {'pop': 5600, 'type': 'rural', 'metro': None},
        'Kingman': {'pop': 7300, 'type': 'rural', 'metro': None},
        'Barber': {'pop': 4200, 'type': 'rural', 'metro': None},
        'Pratt': {'pop': 9200, 'type': 'rural', 'metro': None},
        'Kiowa': {'pop': 2300, 'type': 'rural', 'metro': None},
        'Edwards': {'pop': 2900, 'type': 'rural', 'metro': None},
        'Stafford': {'pop': 4100, 'type': 'rural', 'metro': None},
        'Rice': {'pop': 9400, 'type': 'rural', 'metro': None},
        'McPherson': {'pop': 28500, 'type': 'rural', 'metro': None},
        'Marion': {'pop': 11700, 'type': 'rural', 'metro': None},
        'Chase': {'pop': 2600, 'type': 'rural', 'metro': None},
        'Morris': {'pop': 5500, 'type': 'rural', 'metro': None},
        'Dickinson': {'pop': 18700, 'type': 'rural', 'metro': None},
        'Geary': {'pop': 36000, 'type': 'mixed', 'metro': None},
        'Wabaunsee': {'pop': 6900, 'type': 'rural', 'metro': None},
        'Pottawatomie': {'pop': 25200, 'type': 'rural', 'metro': None},
        'Jackson': {'pop': 13200, 'type': 'rural', 'metro': None},
        'Jefferson': {'pop': 18800, 'type': 'rural', 'metro': 'Kansas City'},
        'Atchison': {'pop': 16300, 'type': 'rural', 'metro': None},
        'Brown': {'pop': 9500, 'type': 'rural', 'metro': None},
        'Doniphan': {'pop': 7200, 'type': 'rural', 'metro': None},
        'Marshall': {'pop': 9800, 'type': 'rural', 'metro': None},
        'Nemaha': {'pop': 10200, 'type': 'rural', 'metro': None},
        'Washington': {'pop': 5500, 'type': 'rural', 'metro': None},
        'Republic': {'pop': 4600, 'type': 'rural', 'metro': None},
        'Cloud': {'pop': 9000, 'type': 'rural', 'metro': None},
        'Clay': {'pop': 8100, 'type': 'rural', 'metro': None},
        'Ottawa': {'pop': 5900, 'type': 'rural', 'metro': None},
        'Lincoln': {'pop': 2900, 'type': 'rural', 'metro': None},
        'Mitchell': {'pop': 5900, 'type': 'rural', 'metro': None},
        'Osborne': {'pop': 3500, 'type': 'rural', 'metro': None},
        'Smith': {'pop': 3500, 'type': 'rural', 'metro': None},
        'Jewell': {'pop': 2900, 'type': 'rural', 'metro': None},
        'Phillips': {'pop': 4600, 'type': 'rural', 'metro': None},
        'Rooks': {'pop': 4900, 'type': 'rural', 'metro': None},
        'Russell': {'pop': 6800, 'type': 'rural', 'metro': None},
        'Ellis': {'pop': 28300, 'type': 'mixed', 'metro': None},
        'Trego': {'pop': 2800, 'type': 'rural', 'metro': None},
        'Graham': {'pop': 2400, 'type': 'rural', 'metro': None},
        'Norton': {'pop': 5400, 'type': 'rural', 'metro': None},
        'Decatur': {'pop': 2900, 'type': 'rural', 'metro': None},
        'Sheridan': {'pop': 2400, 'type': 'rural', 'metro': None},
        'Thomas': {'pop': 7900, 'type': 'rural', 'metro': None},
        'Sherman': {'pop': 5900, 'type': 'rural', 'metro': None},
        'Cheyenne': {'pop': 2600, 'type': 'rural', 'metro': None},
        'Rawlins': {'pop': 2500, 'type': 'rural', 'metro': None},
        'Logan': {'pop': 2800, 'type': 'rural', 'metro': None},
        'Gove': {'pop': 2600, 'type': 'rural', 'metro': None},
        'Ness': {'pop': 2900, 'type': 'rural', 'metro': None},
        'Lane': {'pop': 1700, 'type': 'rural', 'metro': None},
        'Scott': {'pop': 4700, 'type': 'rural', 'metro': None},
        'Wichita': {'pop': 2100, 'type': 'rural', 'metro': None},
        'Greeley': {'pop': 1200, 'type': 'rural', 'metro': None},
        'Wallace': {'pop': 1500, 'type': 'rural', 'metro': None},
        'Hamilton': {'pop': 2500, 'type': 'rural', 'metro': None},
        'Kearny': {'pop': 3900, 'type': 'rural', 'metro': None},
        'Grant': {'pop': 7300, 'type': 'rural', 'metro': None},
        'Haskell': {'pop': 3900, 'type': 'rural', 'metro': None},
        'Gray': {'pop': 5900, 'type': 'rural', 'metro': None},
        'Meade': {'pop': 4200, 'type': 'rural', 'metro': None},
        'Clark': {'pop': 1900, 'type': 'rural', 'metro': None},
        'Comanche': {'pop': 1700, 'type': 'rural', 'metro': None},
        'Barton': {'pop': 25600, 'type': 'rural', 'metro': None},
        'Pawnee': {'pop': 6600, 'type': 'rural', 'metro': None},
        'Rush': {'pop': 3000, 'type': 'rural', 'metro': None},
        'Hodgeman': {'pop': 1700, 'type': 'rural', 'metro': None},
        'Finney': {'pop': 36000, 'type': 'rural', 'metro': None},
        'Seward': {'pop': 21900, 'type': 'rural', 'metro': None},
        'Stevens': {'pop': 5200, 'type': 'rural', 'metro': None},
        'Morton': {'pop': 2700, 'type': 'rural', 'metro': None},
        'Stanton': {'pop': 2000, 'type': 'rural', 'metro': None},
        'Osage': {'pop': 15800, 'type': 'rural', 'metro': None},
        'Linn': {'pop': 9600, 'type': 'rural', 'metro': 'Kansas City'}
    }
    
    # Claim types and base rates per 1000 people per day
    claim_types = {
        'emergency': 0.8,
        'inpatient': 0.3,
        'outpatient': 2.5,
        'pharmacy': 4.0,
        'mental_health': 0.6,
        'preventive': 1.2
    }
    
    start_date = datetime.now() - timedelta(days=365*years)
    end_date = datetime.now()
    
    data = []
    
    for single_date in pd.date_range(start_date, end_date):
        for county, info in kansas_counties.items():
            for claim_type, base_rate in claim_types.items():
                
                # Base daily claims for this county/type
                base_claims = (info['pop'] / 1000) * base_rate
                
                # Seasonal adjustments
                seasonal_multiplier = get_seasonal_multiplier(single_date, claim_type)
                
                # Day of week effect
                dow_multiplier = get_dow_multiplier(single_date.weekday(), claim_type)
                
                # Urban/rural adjustment
                area_multiplier = get_area_multiplier(info['type'], claim_type)
                
                # Random variation
                random_multiplier = np.random.normal(1.0, 0.15)
                
                # Calculate final claim count
                daily_claims = max(0, int(base_claims * seasonal_multiplier * 
                                         dow_multiplier * area_multiplier * random_multiplier))
                
                # Calculate costs
                avg_cost = get_avg_cost(claim_type, info['type'])
                cost_variation = np.random.normal(1.0, 0.25)
                total_cost = daily_claims * avg_cost * max(0.3, cost_variation)
                
                data.append({
                    'date': single_date,
                    'county': county,
                    'area_type': info['type'],
                    'metro': info['metro'],
                    'population': info['pop'],
                    'claim_type': claim_type,
                    'claim_count': daily_claims,
                    'total_cost': round(total_cost, 2),
                    'avg_cost_per_claim': round(total_cost / max(1, daily_claims), 2)
                })
    
    return pd.DataFrame(data)

def get_seasonal_multiplier(date, claim_type):
    """Apply seasonal patterns"""
    month = date.month
    day_of_year = date.timetuple().tm_yday
    
    if claim_type == 'emergency':
        # Winter spike (flu, accidents), summer spike (injuries)
        if month in [12, 1, 2]:
            return 1.4  # Winter spike
        elif month in [6, 7, 8]:
            return 1.2  # Summer activities
        else:
            return 1.0
            
    elif claim_type == 'pharmacy':
        # Allergy season, flu season
        if month in [3, 4, 5]:  # Spring allergies
            return 1.3
        elif month in [12, 1, 2]:  # Flu season
            return 1.5
        else:
            return 1.0
            
    elif claim_type == 'mental_health':
        # Winter depression, holiday stress
        if month in [11, 12, 1, 2]:
            return 1.3
        else:
            return 1.0
            
    elif claim_type == 'preventive':
        # Annual checkups, back-to-school
        if month in [8, 9]:  # Back to school
            return 1.4
        elif month == 1:  # New year resolutions
            return 1.2
        else:
            return 1.0
    
    return 1.0

def get_dow_multiplier(weekday, claim_type):
    """Day of week patterns (0=Monday, 6=Sunday)"""
    if claim_type == 'emergency':
        if weekday >= 5:  # Weekend
            return 1.2  # More accidents/injuries
        else:
            return 1.0
    elif claim_type in ['outpatient', 'preventive']:
        if weekday >= 5:  # Weekend
            return 0.3  # Clinics closed
        else:
            return 1.0
    elif claim_type == 'pharmacy':
        if weekday == 0:  # Monday
            return 1.2  # Weekend prescriptions
        else:
            return 1.0
    
    return 1.0

def get_area_multiplier(area_type, claim_type):
    """Urban vs rural patterns"""
    if area_type == 'urban':
        if claim_type == 'emergency':
            return 1.2  # More urban emergencies
        elif claim_type == 'mental_health':
            return 1.3  # More mental health services
        else:
            return 1.1
    elif area_type == 'rural':
        if claim_type == 'preventive':
            return 0.8  # Less preventive care access
        elif claim_type == 'emergency':
            return 1.1  # Farming/industrial accidents
        else:
            return 1.0
    else:  # mixed
        return 1.0

def get_avg_cost(claim_type, area_type):
    """Average cost per claim by type and area"""
    base_costs = {
        'emergency': 1500,
        'inpatient': 8000,
        'outpatient': 400,
        'pharmacy': 85,
        'mental_health': 150,
        'preventive': 200
    }
    
    base = base_costs[claim_type]
    
    # Urban areas 20% more expensive
    if area_type == 'urban':
        return base * 1.2
    elif area_type == 'rural':
        return base * 0.9
    else:
        return base

if __name__ == "__main__":
    print("Generating Kansas claims data...")
    df = generate_kansas_claims_data(10)
    
    # Save to CSV
    df.to_csv('../data/kansas_claims_10years.csv', index=False)
    
    print(f"Generated {len(df)} records")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total claims: {df['claim_count'].sum():,}")
    print(f"Total cost: ${df['total_cost'].sum():,.2f}")
    print("\nSample data:")
    print(df.head())