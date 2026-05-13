#!/usr/bin/env python3
"""
Backfill 2024 historical data using REAL simulator logic.
This script replicates the exact data generation patterns from simulator/machines/*.py
to ensure baseline formulas trained on 2024 data apply correctly to 2025 live data.
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
import numpy as np
import random

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'enms',
    'user': 'raptorblingx',
    'password': 'raptorblingx'
}

# Machine configurations (from database)
MACHINES = [
    {'id': 'c0000000-0000-0000-0000-000000000001', 'name': 'Compressor-1', 'type': 'compressor', 'rated_power': 13.0},
    {'id': 'c0000000-0000-0000-0000-000000000006', 'name': 'Compressor-2', 'type': 'compressor', 'rated_power': 13.0},
    {'id': 'c0000000-0000-0000-0000-000000000002', 'name': 'HVAC-Main', 'type': 'hvac', 'rated_power': 19.0},
    {'id': 'c0000000-0000-0000-0000-000000000007', 'name': 'HVAC-North-1', 'type': 'hvac', 'rated_power': 19.0},
    {'id': 'c0000000-0000-0000-0000-000000000003', 'name': 'Conveyor-A', 'type': 'motor', 'rated_power': 16.0},
    {'id': 'c0000000-0000-0000-0000-000000000004', 'name': 'Hydraulic-Pump-1', 'type': 'pump', 'rated_power': 19.0},
    {'id': 'c0000000-0000-0000-0000-000000000005', 'name': 'Injection-Molding-1', 'type': 'injection_molding', 'rated_power': 24.0},
]

def get_shift_factor(timestamp: datetime) -> float:
    """
    EXACT replica from simulator/machines/base_machine.py
    Returns production factor based on shift schedule.
    """
    hour = timestamp.hour
    day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
    
    # Weekend factor (Saturday=5, Sunday=6)
    if day_of_week >= 5:
        return 0.3  # 30% production on weekends
    
    # Weekday shifts
    # Shift 1: 06:00-14:00 (full production)
    if 6 <= hour < 14:
        return 1.0
    # Shift 2: 14:00-22:00 (full production)
    elif 14 <= hour < 22:
        return 1.0
    # Shift 3: 22:00-06:00 (reduced production - 50%)
    else:
        return 0.5

def get_seasonal_temp_offset(timestamp: datetime) -> float:
    """EXACT replica from simulator base_machine.py"""
    month = timestamp.month
    
    if month in [12, 1, 2]:  # Winter
        return -10.0
    elif month in [6, 7, 8]:  # Summer
        return 15.0
    elif month in [3, 4, 5]:  # Spring
        return (month - 3) * 5.0
    else:  # Fall
        return 15.0 - ((month - 8) * 5.0)

def add_noise(value: float, noise_percent: float = 3.0) -> float:
    """EXACT replica from simulator"""
    noise = np.random.normal(0, value * noise_percent / 100)
    return max(0, value + noise)

def generate_compressor_reading(machine: dict, timestamp: datetime) -> dict:
    """
    Simplified version of CompressorSimulator.generate_*()
    Generates HOURLY aggregate data matching real simulator patterns.
    """
    shift_factor = get_shift_factor(timestamp)
    
    # Flow rate (air delivered) - base 350 m³/h at full shift
    base_flow = 350.0
    flow_rate_m3h = base_flow * shift_factor * np.random.uniform(0.8, 1.2)
    
    # Production count = flow rate (for hourly aggregate)
    production_count = int(flow_rate_m3h) if shift_factor > 0 else 0
    
    # Power: 70-95% of rated when loaded, based on flow
    if shift_factor > 0:
        load_factor = 0.7 + (flow_rate_m3h / 500.0) * 0.25
        power_kw = machine['rated_power'] * load_factor * np.random.uniform(0.95, 1.05)
    else:
        power_kw = 0
    
    # Outdoor temperature
    outdoor_temp = 15.0 + get_seasonal_temp_offset(timestamp) + np.random.uniform(-5, 5)
    machine_temp = outdoor_temp + np.random.uniform(30, 50) if power_kw > 0 else outdoor_temp + 10
    
    # Indoor humidity
    indoor_humidity = 45.0 + np.random.uniform(-10, 10)
    
    # Pressure
    pressure_bar = 7.0 + np.random.uniform(-0.5, 0.5) if shift_factor > 0 else 0
    
    return {
        'power_kw': round(power_kw, 3),
        'energy_kwh': round(power_kw, 3),  # 1 hour * power_kw
        'voltage_v': 400 + np.random.uniform(-5, 5),
        'current_a': (power_kw * 1000) / (np.sqrt(3) * 400 * 0.9) if power_kw > 0 else 0,
        'power_factor': round(np.random.uniform(0.85, 0.95), 3),
        'frequency_hz': 50.0,
        'production_count': production_count,
        'production_count_good': production_count,
        'production_count_bad': int(production_count * 0.02),  # 2% defect rate
        'outdoor_temp_c': round(outdoor_temp, 2),
        'machine_temp_c': round(machine_temp, 2),
        'indoor_humidity_percent': round(indoor_humidity, 1),
        'pressure_bar': round(pressure_bar, 3),
        'flow_rate_m3h': round(flow_rate_m3h, 3)
    }

def generate_hvac_reading(machine: dict, timestamp: datetime) -> dict:
    """HVAC machines - temperature driven, NO production"""
    shift_factor = get_shift_factor(timestamp)
    
    # HVAC runs all the time, but varies with outdoor temp and occupancy
    outdoor_temp = 15.0 + get_seasonal_temp_offset(timestamp) + np.random.uniform(-5, 5)
    
    # Power varies with temperature difference and occupancy (shift factor)
    # Cooling load in summer, heating load in winter
    temp_load_factor = abs(outdoor_temp - 20.0) / 20.0  # Target 20°C indoor
    occupancy_factor = 0.5 + (shift_factor * 0.5)  # 50% base + occupancy
    
    power_kw = machine['rated_power'] * temp_load_factor * occupancy_factor * np.random.uniform(0.9, 1.1)
    power_kw = max(machine['rated_power'] * 0.3, power_kw)  # Min 30% always running
    
    indoor_temp = 20.0 + np.random.uniform(-2, 2)
    supply_air_temp = indoor_temp - 10 if outdoor_temp > 20 else indoor_temp + 15
    
    return {
        'power_kw': round(power_kw, 3),
        'energy_kwh': round(power_kw, 3),
        'voltage_v': 400 + np.random.uniform(-5, 5),
        'current_a': (power_kw * 1000) / (np.sqrt(3) * 400 * 0.9),
        'power_factor': round(np.random.uniform(0.85, 0.95), 3),
        'frequency_hz': 50.0,
        'production_count': None,  # HVAC has NO production
        'production_count_good': None,
        'production_count_bad': None,
        'outdoor_temp_c': round(outdoor_temp, 2),
        'indoor_temp_c': round(indoor_temp, 2),
        'machine_temp_c': round(indoor_temp + 5, 2),
        'indoor_humidity_percent': round(45.0 + np.random.uniform(-10, 10), 1),
        'supply_air_temp_c': round(supply_air_temp, 2)
    }

def generate_motor_reading(machine: dict, timestamp: datetime) -> dict:
    """Motor (conveyor) - production based"""
    shift_factor = get_shift_factor(timestamp)
    
    # Production: base 800 units/hour at full shift
    base_production = 800
    production_count = int(base_production * shift_factor * np.random.uniform(0.95, 1.05))
    
    # Power proportional to production
    if production_count > 0:
        power_kw = machine['rated_power'] * shift_factor * np.random.uniform(0.85, 1.0)
    else:
        power_kw = 0
    
    outdoor_temp = 15.0 + get_seasonal_temp_offset(timestamp) + np.random.uniform(-5, 5)
    machine_temp = outdoor_temp + np.random.uniform(15, 30) if power_kw > 0 else outdoor_temp + 5
    
    return {
        'power_kw': round(power_kw, 3),
        'energy_kwh': round(power_kw, 3),
        'voltage_v': 400 + np.random.uniform(-5, 5),
        'current_a': (power_kw * 1000) / (np.sqrt(3) * 400 * 0.9) if power_kw > 0 else 0,
        'power_factor': round(np.random.uniform(0.85, 0.95), 3),
        'frequency_hz': 50.0,
        'production_count': production_count,
        'production_count_good': production_count,
        'production_count_bad': int(production_count * 0.01),
        'outdoor_temp_c': round(outdoor_temp, 2),
        'machine_temp_c': round(machine_temp, 2),
        'indoor_humidity_percent': round(45.0 + np.random.uniform(-10, 10), 1)
    }

def generate_pump_reading(machine: dict, timestamp: datetime) -> dict:
    """Hydraulic pump - production based"""
    shift_factor = get_shift_factor(timestamp)
    
    base_production = 600
    production_count = int(base_production * shift_factor * np.random.uniform(0.95, 1.05))
    
    if production_count > 0:
        power_kw = machine['rated_power'] * shift_factor * np.random.uniform(0.8, 0.95)
    else:
        power_kw = 0
    
    outdoor_temp = 15.0 + get_seasonal_temp_offset(timestamp) + np.random.uniform(-5, 5)
    machine_temp = outdoor_temp + np.random.uniform(20, 40) if power_kw > 0 else outdoor_temp + 5
    
    pressure_bar = 200.0 + np.random.uniform(-10, 10) if shift_factor > 0 else 0
    flow_rate = 50.0 * shift_factor * np.random.uniform(0.9, 1.1)
    
    return {
        'power_kw': round(power_kw, 3),
        'energy_kwh': round(power_kw, 3),
        'voltage_v': 400 + np.random.uniform(-5, 5),
        'current_a': (power_kw * 1000) / (np.sqrt(3) * 400 * 0.9) if power_kw > 0 else 0,
        'power_factor': round(np.random.uniform(0.85, 0.95), 3),
        'frequency_hz': 50.0,
        'production_count': production_count,
        'production_count_good': production_count,
        'production_count_bad': int(production_count * 0.015),
        'outdoor_temp_c': round(outdoor_temp, 2),
        'machine_temp_c': round(machine_temp, 2),
        'indoor_humidity_percent': round(45.0 + np.random.uniform(-10, 10), 1),
        'pressure_bar': round(pressure_bar, 3),
        'flow_rate_m3h': round(flow_rate, 3)
    }

def generate_injection_molding_reading(machine: dict, timestamp: datetime) -> dict:
    """Injection molding - production based"""
    shift_factor = get_shift_factor(timestamp)
    
    base_production = 400
    production_count = int(base_production * shift_factor * np.random.uniform(0.95, 1.05))
    
    if production_count > 0:
        power_kw = machine['rated_power'] * shift_factor * np.random.uniform(0.75, 0.95)
    else:
        power_kw = 0
    
    outdoor_temp = 15.0 + get_seasonal_temp_offset(timestamp) + np.random.uniform(-5, 5)
    machine_temp = outdoor_temp + np.random.uniform(40, 70) if power_kw > 0 else outdoor_temp + 10
    
    return {
        'power_kw': round(power_kw, 3),
        'energy_kwh': round(power_kw, 3),
        'voltage_v': 400 + np.random.uniform(-5, 5),
        'current_a': (power_kw * 1000) / (np.sqrt(3) * 400 * 0.9) if power_kw > 0 else 0,
        'power_factor': round(np.random.uniform(0.85, 0.95), 3),
        'frequency_hz': 50.0,
        'production_count': production_count,
        'production_count_good': production_count,
        'production_count_bad': int(production_count * 0.03),
        'outdoor_temp_c': round(outdoor_temp, 2),
        'machine_temp_c': round(machine_temp, 2),
        'indoor_humidity_percent': round(45.0 + np.random.uniform(-10, 10), 1)
    }

GENERATOR_MAP = {
    'compressor': generate_compressor_reading,
    'hvac': generate_hvac_reading,
    'motor': generate_motor_reading,
    'pump': generate_pump_reading,
    'injection_molding': generate_injection_molding_reading
}

async def insert_batch(conn, energy_batch, production_batch, environmental_batch):
    """Insert batch into 3 tables"""
    # Energy readings
    if energy_batch:
        await conn.executemany("""
            INSERT INTO energy_readings (
                machine_id, time, power_kw, energy_kwh, voltage_v,
                current_a, power_factor, frequency_hz
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (machine_id, time) DO NOTHING
        """, energy_batch)
    
    # Production data (only for machines with production)
    if production_batch:
        await conn.executemany("""
            INSERT INTO production_data (
                machine_id, time, production_count, production_count_good, production_count_bad
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (machine_id, time) DO NOTHING
        """, production_batch)
    
    # Environmental data
    if environmental_batch:
        await conn.executemany("""
            INSERT INTO environmental_data (
                machine_id, time, outdoor_temp_c, indoor_temp_c, machine_temp_c,
                indoor_humidity_percent, pressure_bar, flow_rate_m3h,
                supply_air_temp_c
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (machine_id, time) DO NOTHING
        """, environmental_batch)

async def backfill_2024():
    """Main backfill function"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        print("=" * 60)
        print("Backfilling 2024 with REAL simulator logic")
        print("=" * 60)
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2025, 1, 1)
        
        total_inserted = 0
        batch_size = 1000
        
        energy_batch = []
        production_batch = []
        environmental_batch = []
        
        current = start_date
        progress_counter = 0
        
        while current < end_date:
            for machine in MACHINES:
                # Generate reading using appropriate generator
                generator = GENERATOR_MAP[machine['type']]
                reading = generator(machine, current)
                
                # Energy readings batch
                energy_batch.append((
                    machine['id'], current, reading['power_kw'], reading['energy_kwh'],
                    reading['voltage_v'], reading['current_a'], reading['power_factor'],
                    reading['frequency_hz']
                ))
                
                # Production batch (only if machine has production)
                if reading['production_count'] is not None:
                    production_batch.append((
                        machine['id'], current, reading['production_count'],
                        reading['production_count_good'], reading['production_count_bad']
                    ))
                
                # Environmental batch
                environmental_batch.append((
                    machine['id'], current,
                    reading.get('outdoor_temp_c'),
                    reading.get('indoor_temp_c'),
                    reading['machine_temp_c'],
                    reading['indoor_humidity_percent'],
                    reading.get('pressure_bar'),
                    reading.get('flow_rate_m3h'),
                    reading.get('supply_air_temp_c')
                ))
                
                progress_counter += 1
                
                # Insert batch
                if len(energy_batch) >= batch_size:
                    await insert_batch(conn, energy_batch, production_batch, environmental_batch)
                    total_inserted += len(energy_batch)
                    print(f"Inserted {total_inserted} records... ({current.date()})")
                    energy_batch = []
                    production_batch = []
                    environmental_batch = []
            
            current += timedelta(hours=1)
        
        # Insert remaining
        if energy_batch:
            await insert_batch(conn, energy_batch, production_batch, environmental_batch)
            total_inserted += len(energy_batch)
        
        print(f"\n✅ Total inserted: {total_inserted} records")
        print(f"Expected: 61,488 (366 days × 7 machines × 24 hours)")
        
        # Verify per machine
        print("\nVerifying per-machine counts:")
        rows = await conn.fetch("""
            SELECT 
                m.name,
                COUNT(*) as records,
                MIN(er.time)::DATE as first_date,
                MAX(er.time)::DATE as last_date,
                AVG(CASE WHEN pd.production_count IS NOT NULL THEN pd.production_count ELSE NULL END) as avg_production
            FROM machines m
            LEFT JOIN energy_readings er ON m.id = er.machine_id
            LEFT JOIN production_data pd ON m.id = pd.machine_id AND er.time = pd.time
            WHERE er.time >= '2024-01-01' AND er.time < '2025-01-01'
            GROUP BY m.name
            ORDER BY m.name
        """)
        
        for row in rows:
            prod_str = f", avg_production: {int(row['avg_production'])}" if row['avg_production'] else ", (no production)"
            print(f"  {row['name']}: {row['records']} records ({row['first_date']} to {row['last_date']}){prod_str}")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(backfill_2024())
