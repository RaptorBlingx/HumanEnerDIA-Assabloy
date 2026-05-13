#!/usr/bin/env python3
"""
Backfill Q1 2025 data (Jan-Mar) for ISO 50001 performance reporting.
Generates 3 months × 7 machines × 24 hours/day × ~30 days = ~15,120 records
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
from typing import Dict, Any
import random
import math

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'enms',
    'user': 'raptorblingx',
    'password': 'raptorblingx'
}

# Machine configurations
MACHINES = [
    {
        'id': 'c0000000-0000-0000-0000-000000000001',
        'name': 'Compressor-1',
        'type': 'compressor',
        'base_power': 15.0,
        'base_production': 1200,
        'has_production': True
    },
    {
        'id': 'c0000000-0000-0000-0000-000000000002',
        'name': 'Compressor-2',
        'type': 'compressor',
        'base_power': 18.0,
        'base_production': 1400,
        'has_production': True
    },
    {
        'id': 'c0000000-0000-0000-0000-000000000003',
        'name': 'HVAC-Main',
        'type': 'hvac',
        'base_power': 22.0,
        'base_production': 0,
        'has_production': False
    },
    {
        'id': 'c0000000-0000-0000-0000-000000000004',
        'name': 'HVAC-North-1',
        'type': 'hvac',
        'base_power': 20.0,
        'base_production': 0,
        'has_production': False
    },
    {
        'id': 'c0000000-0000-0000-0000-000000000005',
        'name': 'Conveyor-A',
        'type': 'production',
        'base_power': 5.5,
        'base_production': 800,
        'has_production': True
    },
    {
        'id': 'c0000000-0000-0000-0000-000000000006',
        'name': 'Hydraulic-Pump-1',
        'type': 'production',
        'base_power': 11.0,
        'base_production': 600,
        'has_production': True
    },
    {
        'id': 'c0000000-0000-0000-0000-000000000007',
        'name': 'Injection-Molding-1',
        'type': 'production',
        'base_power': 25.0,
        'base_production': 400,
        'has_production': True
    }
]

def generate_reading(machine: Dict[str, Any], timestamp: datetime) -> Dict[str, Any]:
    """Generate single hourly reading with slight efficiency improvement vs 2024"""
    hour = timestamp.hour
    day_of_week = timestamp.weekday()
    day_of_year = timestamp.timetuple().tm_yday
    
    # Temperature: Winter (Jan-Mar) = cooler than 2024 average
    base_temp = 18.0 + 3 * math.sin((day_of_year / 365) * 2 * math.pi)
    temp_variation = random.uniform(-2, 2)
    temperature = base_temp + temp_variation
    
    # Humidity
    humidity = 45 + random.uniform(-10, 10)
    
    # Weekend/night reduction (more realistic for continuous operations)
    if day_of_week >= 5:  # Weekend
        production_factor = 0.85  # 85% capacity on weekends
    elif hour < 6 or hour > 22:  # Night
        production_factor = 0.90  # 90% capacity at night
    else:
        production_factor = 1.0
    
    # Improved efficiency: 2-4% less energy for same production vs 2024
    efficiency_improvement = random.uniform(0.96, 0.98)
    
    # Power calculation with improvement
    base_power = machine['base_power'] * efficiency_improvement
    power_variation = random.uniform(0.9, 1.1)
    
    # HVAC affected more by temperature
    if machine['type'] == 'hvac':
        temp_factor = 1.0 + (temperature - 20) * 0.02
        power = base_power * temp_factor * power_variation * production_factor
    else:
        power = base_power * power_variation * production_factor
    
    # Production
    if machine['has_production']:
        production = int(machine['base_production'] * production_factor * random.uniform(0.95, 1.05))
        bad_count = random.randint(0, int(production * 0.02))  # 0-2% defect rate
    else:
        production = None
        bad_count = None
    
    return {
        'machine_id': machine['id'],
        'time': timestamp,
        'power_kw': round(power, 3),
        'energy_kwh': round(power, 3),  # 1-hour interval
        'voltage_v': 400 + random.uniform(-5, 5),
        'current_a': round(power / 0.4, 2),
        'power_factor': round(random.uniform(0.92, 0.98), 3),
        'frequency_hz': 50.0,
        'production_count': production,
        'production_count_bad': bad_count,
        'machine_temp_c': round(temperature + random.uniform(5, 15), 2),
        'ambient_temp_c': round(temperature, 2),
        'humidity_percent': round(humidity, 1)
    }

async def backfill_q1_2025(conn):
    """Backfill Q1 2025 (90 days × 7 machines × 24 hours = 15,120 records)"""
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 4, 1)
    
    print(f"Backfilling Q1 2025: {start_date.date()} to {end_date.date()}")
    print(f"Expected records: 90 days × 7 machines × 24 hours = 15,120")
    
    total_inserted = 0
    batch = []
    batch_size = 1000
    
    current = start_date
    while current < end_date:
        for machine in MACHINES:
            reading = generate_reading(machine, current)
            batch.append(reading)
            
            if len(batch) >= batch_size:
                await insert_batch(conn, batch)
                total_inserted += len(batch)
                print(f"Inserted {total_inserted} records... ({current.date()})")
                batch = []
        
        current += timedelta(hours=1)
    
    # Insert remaining
    if batch:
        await insert_batch(conn, batch)
        total_inserted += len(batch)
    
    print(f"\n✅ Total inserted: {total_inserted} records")
    return total_inserted

async def insert_batch(conn, batch):
    """Insert batch into all 3 tables"""
    # Energy readings
    await conn.executemany("""
        INSERT INTO energy_readings (
            machine_id, time, power_kw, energy_kwh, voltage_v, 
            current_a, power_factor, frequency_hz
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (machine_id, time) DO NOTHING
    """, [(r['machine_id'], r['time'], r['power_kw'], r['energy_kwh'],
           r['voltage_v'], r['current_a'], r['power_factor'], r['frequency_hz'])
          for r in batch])
    
    # Production data
    production_batch = [r for r in batch if r['production_count'] is not None]
    if production_batch:
        await conn.executemany("""
            INSERT INTO production_data (
                machine_id, time, production_count, production_count_bad
            ) VALUES ($1, $2, $3, $4)
            ON CONFLICT (machine_id, time) DO NOTHING
        """, [(r['machine_id'], r['time'], r['production_count'],
               r['production_count_bad'])
              for r in production_batch])
    
    # Environmental data
    await conn.executemany("""
        INSERT INTO environmental_data (
            machine_id, time, machine_temp_c, outdoor_temp_c, indoor_humidity_percent
        ) VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (machine_id, time) DO NOTHING
    """, [(r['machine_id'], r['time'], r['machine_temp_c'],
           r['ambient_temp_c'], r['humidity_percent'])
          for r in batch])

async def main():
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        total = await backfill_q1_2025(conn)
        
        # Verify
        print("\nVerifying per-machine counts:")
        rows = await conn.fetch("""
            SELECT 
                machine_id,
                COUNT(*) as records,
                MIN(time)::DATE as first_date,
                MAX(time)::DATE as last_date
            FROM energy_readings
            WHERE time >= '2025-01-01' AND time < '2025-04-01'
            GROUP BY machine_id
            ORDER BY machine_id
        """)
        
        for row in rows:
            print(f"  {row['machine_id']}: {row['records']} records ({row['first_date']} to {row['last_date']})")
        
        # Refresh continuous aggregates for Q1 2025
        print("\nRefreshing continuous aggregates for Q1 2025...")
        await conn.execute("CALL refresh_continuous_aggregate('energy_readings_1hour', '2025-01-01', '2025-04-01')")
        await conn.execute("CALL refresh_continuous_aggregate('production_data_1hour', '2025-01-01', '2025-04-01')")
        await conn.execute("CALL refresh_continuous_aggregate('environmental_data_1hour', '2025-01-01', '2025-04-01')")
        print("✅ Aggregates refreshed")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
