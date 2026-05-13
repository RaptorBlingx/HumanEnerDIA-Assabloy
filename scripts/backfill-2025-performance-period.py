#!/usr/bin/env python3
"""
Generate 2025 Q1-Q3 Performance Period Data (Jan-Sep)
Uses REAL simulator logic with 2-4% efficiency improvement
Keeps Oct 2025 live data untouched
"""

import asyncio
import asyncpg
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'enms',
    'user': 'raptorblingx',
    'password': 'raptorblingx'
}

# Efficiency improvement factor (2-4% savings)
EFFICIENCY_FACTOR = lambda: random.uniform(0.96, 0.98)  # 2-4% reduction in power

# Machines configuration (from database)
MACHINES = {
    'c0000000-0000-0000-0000-000000000001': {'name': 'Compressor-1', 'type': 'compressor'},
    'c0000000-0000-0000-0000-000000000006': {'name': 'Compressor-2', 'type': 'compressor'},
    'c0000000-0000-0000-0000-000000000002': {'name': 'HVAC-Main', 'type': 'hvac'},
    'c0000000-0000-0000-0000-000000000007': {'name': 'HVAC-North-1', 'type': 'hvac'},
    'c0000000-0000-0000-0000-000000000003': {'name': 'Conveyor-A', 'type': 'motor'},
    'c0000000-0000-0000-0000-000000000004': {'name': 'Hydraulic-Pump-1', 'type': 'pump'},
    'c0000000-0000-0000-0000-000000000005': {'name': 'Injection-Molding-1', 'type': 'injection_molding'},
}

# Energy source ID (electricity)
ENERGY_SOURCE_ID = 'abca19aa-dc80-4949-9e62-eb455da376b8'


def get_shift_factor(hour: int, is_weekend: bool) -> float:
    """Match real simulator shift logic."""
    if is_weekend:
        return 0.3
    if 22 <= hour or hour < 6:
        return 0.5  # Night shift
    return 1.0  # Day shift


def get_seasonal_temp_offset(month: int) -> float:
    """Match real simulator seasonal temperature offset."""
    seasonal_offsets = {
        1: -10, 2: -8, 3: -5, 4: 0, 5: 5, 6: 10,
        7: 15, 8: 15, 9: 10, 10: 5, 11: 0, 12: -5
    }
    return seasonal_offsets.get(month, 0)


def add_noise(value: float, noise_percent: float = 0.05) -> float:
    """Add realistic noise to values."""
    noise = random.uniform(-noise_percent, noise_percent)
    return value * (1 + noise)


def generate_compressor_reading(timestamp: datetime, machine_id: str) -> Dict:
    """Generate compressor data matching real simulator."""
    hour = timestamp.hour
    is_weekend = timestamp.weekday() >= 5
    shift_factor = get_shift_factor(hour, is_weekend)
    temp_offset = get_seasonal_temp_offset(timestamp.month)
    
    # Base production (m³/hour)
    base_production = 350 * shift_factor
    production = add_noise(base_production, 0.10)
    
    # Power consumption (kW) with efficiency improvement
    base_power = 13 * shift_factor * (1 + temp_offset * 0.01)
    power = add_noise(base_power, 0.08) * EFFICIENCY_FACTOR()  # 2-4% improvement
    
    # Temperature
    ambient_temp = 15 + temp_offset
    temp = add_noise(ambient_temp, 0.05)
    
    # Pressure (bar)
    pressure = add_noise(7.0, 0.05)
    
    return {
        'machine_id': machine_id,
        'timestamp': timestamp,
        'power_kw': round(power, 2),
        'energy_kwh': round(power, 4),  # 1 hour interval
        'production_count': round(production, 0),
        'temp_c': round(temp, 1),
        'pressure_bar': round(pressure, 2),
    }


def generate_hvac_reading(timestamp: datetime, machine_id: str) -> Dict:
    """Generate HVAC data (no production)."""
    hour = timestamp.hour
    is_weekend = timestamp.weekday() >= 5
    shift_factor = get_shift_factor(hour, is_weekend)
    temp_offset = get_seasonal_temp_offset(timestamp.month)
    
    # HVAC power depends heavily on temperature difference
    ambient_temp = 15 + temp_offset
    target_temp = 20
    temp_diff = abs(ambient_temp - target_temp)
    
    # Base power for HVAC
    base_power = 19 * (1 + temp_diff * 0.15) * shift_factor
    power = add_noise(base_power, 0.10) * EFFICIENCY_FACTOR()
    
    return {
        'machine_id': machine_id,
        'timestamp': timestamp,
        'power_kw': round(power, 2),
        'energy_kwh': round(power, 4),
        'production_count': None,  # HVAC has no production
        'temp_c': round(add_noise(ambient_temp, 0.05), 1),
        'pressure_bar': None,
    }


def generate_motor_reading(timestamp: datetime, machine_id: str) -> Dict:
    """Generate motor/conveyor data."""
    hour = timestamp.hour
    is_weekend = timestamp.weekday() >= 5
    shift_factor = get_shift_factor(hour, is_weekend)
    temp_offset = get_seasonal_temp_offset(timestamp.month)
    
    # Production (units moved per hour)
    base_production = 800 * shift_factor
    production = add_noise(base_production, 0.12)
    
    # Power
    base_power = 16 * shift_factor
    power = add_noise(base_power, 0.08) * EFFICIENCY_FACTOR()
    
    ambient_temp = 15 + temp_offset
    
    return {
        'machine_id': machine_id,
        'timestamp': timestamp,
        'power_kw': round(power, 2),
        'energy_kwh': round(power, 4),
        'production_count': round(production, 0),
        'temp_c': round(add_noise(ambient_temp, 0.05), 1),
        'pressure_bar': None,
    }


def generate_pump_reading(timestamp: datetime, machine_id: str) -> Dict:
    """Generate hydraulic pump data."""
    hour = timestamp.hour
    is_weekend = timestamp.weekday() >= 5
    shift_factor = get_shift_factor(hour, is_weekend)
    temp_offset = get_seasonal_temp_offset(timestamp.month)
    
    # Production (cycles per hour)
    base_production = 600 * shift_factor
    production = add_noise(base_production, 0.15)
    
    # Power
    base_power = 19 * shift_factor
    power = add_noise(base_power, 0.10) * EFFICIENCY_FACTOR()
    
    # Pressure
    pressure = add_noise(200.0, 0.08)  # bar
    
    ambient_temp = 15 + temp_offset
    
    return {
        'machine_id': machine_id,
        'timestamp': timestamp,
        'power_kw': round(power, 2),
        'energy_kwh': round(power, 4),
        'production_count': round(production, 0),
        'temp_c': round(add_noise(ambient_temp, 0.05), 1),
        'pressure_bar': round(pressure, 2),
    }


def generate_injection_molding_reading(timestamp: datetime, machine_id: str) -> Dict:
    """Generate injection molding machine data."""
    hour = timestamp.hour
    is_weekend = timestamp.weekday() >= 5
    shift_factor = get_shift_factor(hour, is_weekend)
    temp_offset = get_seasonal_temp_offset(timestamp.month)
    
    # Production (parts per hour)
    base_production = 400 * shift_factor
    production = add_noise(base_production, 0.12)
    
    # Power (high energy process)
    base_power = 24 * shift_factor
    power = add_noise(base_power, 0.09) * EFFICIENCY_FACTOR()
    
    ambient_temp = 15 + temp_offset
    
    return {
        'machine_id': machine_id,
        'timestamp': timestamp,
        'power_kw': round(power, 2),
        'energy_kwh': round(power, 4),
        'production_count': round(production, 0),
        'temp_c': round(add_noise(ambient_temp, 0.05), 1),
        'pressure_bar': round(add_noise(150.0, 0.10), 2),
    }


# Generator mapping
GENERATORS = {
    'compressor': generate_compressor_reading,
    'hvac': generate_hvac_reading,
    'motor': generate_motor_reading,
    'pump': generate_pump_reading,
    'injection_molding': generate_injection_molding_reading,
}


async def generate_and_insert_data(conn, start_date: str, end_date: str):
    """Generate 2025 performance period data with efficiency improvement."""
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    current = start
    batch_energy = []
    batch_production = []
    batch_environmental = []
    batch_size = 1000
    total_inserted = 0
    
    while current <= end:
        for hour in range(24):
            timestamp = current.replace(hour=hour, minute=0, second=0)
            
            for machine_id, machine_info in MACHINES.items():
                machine_type = machine_info['type']
                generator = GENERATORS[machine_type]
                
                reading = generator(timestamp, machine_id)
                
                # Energy readings
                batch_energy.append((
                    reading['timestamp'],
                    reading['machine_id'],
                    reading['power_kw'],
                    reading['energy_kwh']
                ))
                
                # Production data (if applicable)
                if reading['production_count'] is not None:
                    batch_production.append((
                        reading['timestamp'],
                        reading['machine_id'],
                        reading['production_count']
                    ))
                
                # Environmental data - FIXED: Include outdoor_temp_c for weather normalization
                batch_environmental.append((
                    reading['timestamp'],
                    reading['machine_id'],
                    reading['temp_c'],  # outdoor_temp_c (ambient temperature)
                    reading['temp_c'],  # machine_temp_c (same as outdoor for simplicity)
                    reading.get('pressure_bar')
                ))
            
            # Insert in batches
            if len(batch_energy) >= batch_size:
                await conn.executemany("""
                    INSERT INTO energy_readings (time, machine_id, power_kw, energy_kwh)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT DO NOTHING
                """, batch_energy)
                
                await conn.executemany("""
                    INSERT INTO production_data (time, machine_id, production_count)
                    VALUES ($1, $2, $3)
                    ON CONFLICT DO NOTHING
                """, batch_production)
                
                await conn.executemany("""
                    INSERT INTO environmental_data (time, machine_id, outdoor_temp_c, machine_temp_c, pressure_bar)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (time, machine_id) DO UPDATE SET
                        outdoor_temp_c = EXCLUDED.outdoor_temp_c,
                        machine_temp_c = EXCLUDED.machine_temp_c,
                        pressure_bar = EXCLUDED.pressure_bar
                """, batch_environmental)
                
                total_inserted += len(batch_energy)
                print(f"Inserted {total_inserted} records... ({current.date()})")
                
                batch_energy = []
                batch_production = []
                batch_environmental = []
        
        current += timedelta(days=1)
    
    # Insert remaining
    if batch_energy:
        await conn.executemany("""
            INSERT INTO energy_readings (time, machine_id, power_kw, energy_kwh)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT DO NOTHING
        """, batch_energy)
        
        await conn.executemany("""
            INSERT INTO production_data (time, machine_id, production_count)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
        """, batch_production)
        
        await conn.executemany("""
            INSERT INTO environmental_data (time, machine_id, outdoor_temp_c, machine_temp_c, pressure_bar)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (time, machine_id) DO UPDATE SET
                outdoor_temp_c = EXCLUDED.outdoor_temp_c,
                machine_temp_c = EXCLUDED.machine_temp_c,
                pressure_bar = EXCLUDED.pressure_bar
        """, batch_environmental)
        
        total_inserted += len(batch_energy)
    
    print(f"\n✅ Total inserted: {total_inserted} records")
    return total_inserted


async def verify_data(conn):
    """Verify inserted data."""
    print("\nVerifying per-machine counts:")
    
    for machine_id, machine_info in MACHINES.items():
        result = await conn.fetchrow("""
            SELECT 
                COUNT(*) as count,
                MIN(time) as first_date,
                MAX(time) as last_date
            FROM energy_readings
            WHERE machine_id = $1
              AND time >= '2025-01-01'
              AND time < '2025-10-01'
        """, machine_id)
        
        # Get production average if applicable
        if machine_info['type'] != 'hvac':
            prod_result = await conn.fetchrow("""
                SELECT AVG(production_count)::INTEGER as avg_production
                FROM production_data
                WHERE machine_id = $1
                  AND time >= '2025-01-01'
                  AND time < '2025-10-01'
            """, machine_id)
            
            print(f"  {machine_info['name']}: {result['count']} records "
                  f"({result['first_date'].date()} to {result['last_date'].date()}), "
                  f"avg_production: {prod_result['avg_production']}")
        else:
            print(f"  {machine_info['name']}: {result['count']} records "
                  f"({result['first_date'].date()} to {result['last_date'].date()}), "
                  f"(no production)")


async def main():
    """Main execution."""
    print("=" * 60)
    print("Backfilling 2025 Q1-Q3 with efficiency improvement")
    print("=" * 60)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Generate Q1-Q3 2025 (273 days)
        expected_records = 273 * 7 * 24  # 45,864 records
        print(f"Expected: {expected_records:,} records (273 days × 7 machines × 24 hours)\n")
        
        total = await generate_and_insert_data(conn, '2025-01-01', '2025-09-30')
        
        print(f"Expected: {expected_records:,}")
        
        # Verify
        await verify_data(conn)
        
    finally:
        await conn.close()
    
    print("\n✅ 2025 Q1-Q3 backfill complete with 2-4% efficiency improvement!")


if __name__ == '__main__':
    asyncio.run(main())
