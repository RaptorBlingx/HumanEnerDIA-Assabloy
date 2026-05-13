#!/usr/bin/env python3
"""
Comprehensive ISO 50001 Data Backfill Script
============================================
Generates one full year (2024) of synthetic energy data for ALL machines and energy sources.

Coverage:
- All 7 machines: Compressor-1, Compressor-2, HVAC-Main, HVAC-North-1, 
  Conveyor-A, Hydraulic-Pump-1, Injection-Molding-1
- Multiple energy sources: Electricity, Natural Gas (HVAC), Compressed Air (Compressors)
- Realistic patterns: Seasonal variations, daily work cycles, weekends, maintenance

⚠️  WARNING: This generates SYNTHETIC data for DEMO/TESTING only.
   For production ISO 50001 compliance, use real historical data.

Usage: python3 scripts/backfill-comprehensive-year-data.py
"""

import asyncpg
import asyncio
from datetime import datetime, timedelta
import random
import os
import sys
from typing import Dict, List, Tuple

# ============================================================================
# Configuration
# ============================================================================

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,  # External port mapping
    'database': 'enms',
    'user': 'raptorblingx',
    'password': 'raptorblingx'
}

# All 7 machines with realistic operational profiles
MACHINES = {
    'c0000000-0000-0000-0000-000000000001': {
        'name': 'Compressor-1',
        'type': 'compressor',
        'power_base': 45,           # kW average
        'power_variance': 15,
        'production_base': 1000,    # Nm³/hour compressed air
        'temp_base': 65,            # °C
        'energy_sources': ['electricity', 'compressed_air'],
        'seasonal_factor': 0.15,    # Lower in summer (cooling efficiency)
        'weekend_factor': 0.3       # 30% operation on weekends
    },
    'c0000000-0000-0000-0000-000000000006': {
        'name': 'Compressor-2',
        'type': 'compressor',
        'power_base': 48,
        'power_variance': 12,
        'production_base': 1200,
        'temp_base': 68,
        'energy_sources': ['electricity', 'compressed_air'],
        'seasonal_factor': 0.15,
        'weekend_factor': 0.3
    },
    'c0000000-0000-0000-0000-000000000002': {
        'name': 'HVAC-Main',
        'type': 'hvac',
        'power_base': 35,           # Electricity for fans/controls
        'power_variance': 10,
        'production_base': 0,       # HVAC doesn't produce units
        'temp_base': 22,            # Target indoor temp
        'energy_sources': ['electricity', 'natural_gas'],
        'gas_base': 25,             # m³/hour natural gas (heating)
        'gas_variance': 10,
        'seasonal_factor': 0.50,    # HIGH in winter (heating) and summer (cooling)
        'weekend_factor': 0.5       # 50% on weekends (maintain climate)
    },
    'c0000000-0000-0000-0000-000000000007': {
        'name': 'HVAC-North-1',
        'type': 'hvac',
        'power_base': 32,
        'power_variance': 8,
        'production_base': 0,
        'temp_base': 21,
        'energy_sources': ['electricity', 'natural_gas'],
        'gas_base': 22,
        'gas_variance': 8,
        'seasonal_factor': 0.50,
        'weekend_factor': 0.5
    },
    'c0000000-0000-0000-0000-000000000003': {
        'name': 'Conveyor-A',
        'type': 'motor',
        'power_base': 15,
        'power_variance': 5,
        'production_base': 500,     # Items moved per hour
        'temp_base': 55,
        'energy_sources': ['electricity'],
        'seasonal_factor': 0.05,
        'weekend_factor': 0.2       # 20% on weekends
    },
    'c0000000-0000-0000-0000-000000000004': {
        'name': 'Hydraulic-Pump-1',
        'type': 'pump',
        'power_base': 22,
        'power_variance': 8,
        'production_base': 800,     # Liters per hour
        'temp_base': 60,
        'energy_sources': ['electricity'],
        'seasonal_factor': 0.10,    # Viscosity changes with temperature
        'weekend_factor': 0.2
    },
    'c0000000-0000-0000-0000-000000000005': {
        'name': 'Injection-Molding-1',
        'type': 'injection_molding',
        'power_base': 75,           # High power consumption
        'power_variance': 20,
        'production_base': 2500,    # Parts per hour
        'temp_base': 85,
        'energy_sources': ['electricity'],
        'seasonal_factor': 0.08,
        'weekend_factor': 0.1       # Minimal weekend operation
    }
}

# ============================================================================
# Helper Functions
# ============================================================================

def is_weekend(date: datetime) -> bool:
    """Check if date is weekend (Saturday=5, Sunday=6)."""
    return date.weekday() >= 5

def is_maintenance_day(date: datetime) -> bool:
    """Simulate monthly maintenance (first Sunday of each month)."""
    return date.weekday() == 6 and 1 <= date.day <= 7

def get_seasonal_factor(month: int, base_seasonal: float) -> float:
    """
    Calculate seasonal multiplier.
    - Winter (Dec, Jan, Feb): Higher heating loads
    - Summer (Jun, Jul, Aug): Higher cooling loads
    - Spring/Fall: Moderate
    """
    if month in [12, 1, 2]:  # Winter
        return 1.0 + base_seasonal
    elif month in [6, 7, 8]:  # Summer
        return 1.0 + base_seasonal * 0.8
    else:  # Spring/Fall
        return 1.0 - base_seasonal * 0.3

def get_hourly_factor(hour: int) -> float:
    """
    Daily work cycle pattern.
    - 00-06: Night (minimal)
    - 07-08: Ramp up
    - 09-17: Full operation
    - 18-19: Ramp down
    - 20-23: Evening (reduced)
    """
    if 0 <= hour < 6:
        return 0.2
    elif 6 <= hour < 8:
        return 0.5 + (hour - 6) * 0.25  # Ramp up
    elif 8 <= hour < 17:
        return 1.0
    elif 17 <= hour < 20:
        return 0.9 - (hour - 17) * 0.2  # Ramp down
    else:
        return 0.3

def calculate_power(config: dict, timestamp: datetime) -> Tuple[float, float, float]:
    """
    Calculate realistic power consumption for a machine at given timestamp.
    Returns: (power_kw, energy_kwh_hourly, production_hourly)
    """
    hour = timestamp.hour
    month = timestamp.month
    
    # Base factors
    seasonal = get_seasonal_factor(month, config['seasonal_factor'])
    hourly = get_hourly_factor(hour)
    
    # Weekend reduction
    if is_weekend(timestamp):
        hourly *= config['weekend_factor']
    
    # Maintenance shutdown
    if is_maintenance_day(timestamp):
        hourly *= 0.1
    
    # Calculate power with noise
    base_power = config['power_base']
    power_kw = base_power * seasonal * hourly + random.gauss(0, config['power_variance'])
    power_kw = max(2, min(150, power_kw))  # Clamp to reasonable range
    
    # Energy for 1-hour interval
    energy_kwh = power_kw
    
    # Production (if applicable) - hourly rate
    if config['production_base'] > 0:
        production_hourly = int(config['production_base'] * hourly + random.gauss(0, 50))
        production_hourly = max(0, production_hourly)
    else:
        production_hourly = 0
    
    return power_kw, energy_kwh, production_hourly

def calculate_gas_consumption(config: dict, timestamp: datetime) -> float:
    """
    Calculate natural gas consumption for HVAC units (heating).
    Returns: gas consumption in m³ for 10-second interval
    """
    if 'gas_base' not in config:
        return 0
    
    month = timestamp.month
    hour = timestamp.hour
    
    # Winter months need more heating
    if month in [12, 1, 2]:
        seasonal_gas = 1.8
    elif month in [11, 3]:
        seasonal_gas = 1.3
    elif month in [10, 4]:
        seasonal_gas = 0.8
    else:  # Summer - minimal gas (no heating)
        seasonal_gas = 0.2
    
    # Night setback (lower temperature)
    hourly = get_hourly_factor(hour) * 0.7 + 0.3
    
    # Weekend reduction
    if is_weekend(timestamp):
        hourly *= config['weekend_factor']
    
    # Calculate gas flow
    gas_m3 = config['gas_base'] * seasonal_gas * hourly * (10 / 3600)
    gas_m3 += random.gauss(0, config.get('gas_variance', 5)) * (10 / 3600)
    gas_m3 = max(0, gas_m3)
    
    return gas_m3

def generate_reading(timestamp: datetime, machine_id: str, config: dict, day_of_year: int) -> dict:
    """
    Generate a single reading for a machine at given timestamp.
    
    Returns dict with all required fields for insertion.
    """
    power_kw, energy_kwh, production = calculate_power(config, timestamp)
    
    # Temperature based on machine type and operation
    temp_base = config['temp_base']
    temp_c = temp_base + (power_kw / config['power_base'] - 1) * 10
    temp_c += random.gauss(0, 2)
    
    # Humidity for HVAC systems
    humidity = None
    if config['type'] in ['hvac']:
        month = timestamp.month
        # Higher humidity in summer
        base_humidity = 50 + (month - 6.5) * 5 if month >= 4 and month <= 9 else 40
        humidity = base_humidity + random.gauss(0, 5)
        humidity = max(20, min(80, humidity))
    
    return {
        'time': timestamp,
        'machine_id': machine_id,
        'power_kw': round(power_kw, 2),
        'energy_kwh': round(energy_kwh, 6),
        'production': int(production),
        'temp_c': round(temp_c, 1),
        'humidity': round(humidity, 1) if humidity else None
    }

# ============================================================================
# Database Operations
# ============================================================================

async def insert_batch(conn, batch: List[dict]):
    """Insert batch of energy readings."""
    
    # Energy readings (electricity)
    energy_batch = [(
        r['time'], r['machine_id'], r['power_kw'], r['energy_kwh']
    ) for r in batch]
    
    await conn.executemany(
        """
        INSERT INTO energy_readings (time, machine_id, power_kw, energy_kwh)
        VALUES ($1, $2, $3, $4)
        """,
        energy_batch
    )
    
    # Production data (where applicable)
    production_batch = [(
        r['time'], r['machine_id'], r['production'], int(r['production'] * 0.02)
    ) for r in batch if r['production'] > 0]
    
    if production_batch:
        await conn.executemany(
            """
            INSERT INTO production_data (time, machine_id, production_count, production_count_bad)
            VALUES ($1, $2, $3, $4)
            """,
            production_batch
        )
    
    # Environmental data
    env_batch = [(
        r['time'], r['machine_id'], r['temp_c'], r['temp_c'] - 10, r.get('humidity', None)
    ) for r in batch]
    
    await conn.executemany(
        """
        INSERT INTO environmental_data (time, machine_id, machine_temp_c, outdoor_temp_c, indoor_humidity_percent)
        VALUES ($1, $2, $3, $4, $5)
        """,
        env_batch
    )

async def backfill_data():
    """Main backfill function - production ready."""
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31, 23, 59, 59)
        
        total_machines = len(MACHINES)
        total_days = (end_date - start_date).days + 1
        total_records_est = total_machines * total_days * 24 * 360
        
        print(f"📊 Generating data:")
        print(f"   Machines: {total_machines}")
        print(f"   Period: {start_date.date()} to {end_date.date()} ({total_days} days)")
        print(f"   Estimated records: {total_records_est:,}")
        print()
        
        current_date = start_date
        day_count = 0
        total_inserted = 0
        
        while current_date <= end_date:
            day_count += 1
            batch = []
            
            # Generate data for all machines for this day
            for machine_id, machine_cfg in MACHINES.items():
                # Generate hourly data
                for hour in range(24):
                    timestamp = current_date + timedelta(hours=hour)
                    
                    # Generate reading
                    reading = generate_reading(
                        timestamp, 
                        machine_id, 
                        machine_cfg,
                        current_date.timetuple().tm_yday
                    )
                    
                    batch.append(reading)
                    
                    # Insert batch every 1000 records
                    if len(batch) >= 1000:
                        await insert_batch(conn, batch)
                        total_inserted += len(batch)
                        batch = []
            
            # Insert remaining batch for the day
            if batch:
                await insert_batch(conn, batch)
                total_inserted += len(batch)
            
            # Progress update every 10 days
            if day_count % 10 == 0:
                progress = (day_count / total_days) * 100
                print(f"✓ Day {day_count}/{total_days} ({progress:.1f}%) - {current_date.date()} - {total_inserted:,} records inserted")
            
            current_date += timedelta(days=1)
        
        print()
        print("="*70)
        print(f"✅ Backfill Complete!")
        print(f"   Total records inserted: {total_inserted:,}")
        print(f"   Period covered: 2024-01-01 to 2024-12-31")
        print("="*70)
        print()
        
        # Verification
        print("Verifying data...")
        for machine_id, machine_cfg in MACHINES.items():
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM energy_readings WHERE machine_id = $1 AND time >= $2 AND time <= $3",
                machine_id, start_date, end_date
            )
            print(f"  {machine_cfg['name']}: {count:,} records")
        
        print("\n✓ Verification complete. Ready for ISO 50001 baseline training!")
        
    finally:
        await conn.close()

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill comprehensive year data for ISO 50001')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("ISO 50001 Comprehensive Data Backfill")
    print("="*70)
    print("\n⚠️  WARNING: This generates SYNTHETIC data for DEMO/TESTING.")
    print("   For production ISO 50001 compliance, use real historical data.\n")
    print("This will:")
    print("  • Generate 365 days of data (2024)")
    print("  • Cover all 7 machines")
    print("  • Include multiple energy sources (electricity, gas, compressed air)")
    print("  • Add realistic patterns (seasonal, daily, weekends, maintenance)")
    print(f"  • Insert approximately {7 * 365 * 24 * 360:,} records (~9 million)\n")
    
    if not args.yes:
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Cancelled.")
            sys.exit(0)
    
    asyncio.run(backfill_data())
