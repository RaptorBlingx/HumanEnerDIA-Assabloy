#!/usr/bin/env python3
"""
Fast ISO 50001 Data Backfill - Essential Columns Only
======================================================
Simplified version that populates only essential columns for ISO 50001 baseline training.
Much faster than comprehensive version.

Generates:
- Full year 2024 data (Jan 1 - Dec 31)
- All 7 machines
- Only essential columns: time, machine_id, power_kw, energy_kwh
- Realistic patterns for baseline training

Usage: python3 scripts/backfill-fast-year-data.py
"""

import asyncpg
import asyncio
from datetime import datetime, timedelta
import random
import math

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'enms',
    'user': 'raptorblingx',
    'password': 'raptorblingx'
}

# Machines with simple power profiles
MACHINES = {
    'c0000000-0000-0000-0000-000000000001': {'name': 'Compressor-1', 'power_avg': 45, 'var': 10},
    'c0000000-0000-0000-0000-000000000006': {'name': 'Compressor-2', 'power_avg': 48, 'var': 12},
    'c0000000-0000-0000-0000-000000000002': {'name': 'HVAC-Main', 'power_avg': 35, 'var': 15},
    'c0000000-0000-0000-0000-000000000007': {'name': 'HVAC-North-1', 'power_avg': 32, 'var': 12},
    'c0000000-0000-0000-0000-000000000003': {'name': 'Conveyor-A', 'power_avg': 15, 'var': 5},
    'c0000000-0000-0000-0000-000000000004': {'name': 'Hydraulic-Pump-1', 'power_avg': 22, 'var': 8},
    'c0000000-0000-0000-0000-000000000005': {'name': 'Injection-Molding-1', 'power_avg': 85, 'var': 20}
}

START_DATE = datetime(2024, 1, 1, 0, 0, 0)
END_DATE = datetime(2024, 12, 31, 23, 59, 59)
INTERVAL_SECONDS = 60  # 1 minute intervals for speed

def calculate_power(machine_id, timestamp):
    """Calculate realistic power consumption for a given time."""
    config = MACHINES[machine_id]
    hour = timestamp.hour
    day_of_week = timestamp.weekday()
    day_of_year = timestamp.timetuple().tm_yday
    
    # Base power
    power = config['power_avg']
    
    # Daily pattern (work hours)
    if 6 <= hour < 22:
        hourly_factor = 0.8 + 0.2 * math.sin((hour - 6) * math.pi / 16)
    else:
        hourly_factor = 0.3
    
    # Weekend reduction
    if day_of_week >= 5:  # Saturday, Sunday
        hourly_factor *= 0.4
    
    # Seasonal variation (winter heating, summer cooling for HVAC)
    if 'HVAC' in config['name']:
        seasonal = 1.3 if day_of_year < 90 or day_of_year > 300 else 0.9  # Winter peak
    else:
        seasonal = 1.0
    
    power *= hourly_factor * seasonal
    power += random.gauss(0, config['var'])
    power = max(0, power)
    
    # Energy = Power × Time (in hours)
    energy_kwh = power * (INTERVAL_SECONDS / 3600)
    
    return power, energy_kwh

async def insert_chunk(conn, chunk):
    """Insert a chunk of data."""
    await conn.executemany(
        """
        INSERT INTO energy_readings (time, machine_id, power_kw, energy_kwh)
        VALUES ($1, $2, $3, $4)
        """,
        chunk
    )

async def insert_production_chunk(conn, chunk):
    """Insert production data chunk."""
    if not chunk:
        return
    await conn.executemany(
        """
        INSERT INTO production_data (time, machine_id, production_count, production_count_bad)
        VALUES ($1, $2, $3, $4)
        """,
        chunk
    )

async def insert_environmental_chunk(conn, chunk):
    """Insert environmental data chunk."""
    await conn.executemany(
        """
        INSERT INTO environmental_data (time, machine_id, machine_temp_c, outdoor_temp_c)
        VALUES ($1, $2, $3, $4)
        """,
        chunk
    )

async def backfill():
    print("\n" + "="*60)
    print("ISO 50001 Fast Data Backfill - Essential Columns")
    print("="*60)
    print(f"Period: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Machines: {len(MACHINES)}")
    print(f"Interval: {INTERVAL_SECONDS} seconds")
    print(f"Estimated records: ~{len(MACHINES) * 365 * 24 * (3600/INTERVAL_SECONDS):,.0f}")
    print("="*60 + "\n")
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Clear existing 2024 data
        print("Clearing existing 2024 data...")
        deleted_energy = await conn.execute(
            "DELETE FROM energy_readings WHERE time >= '2024-01-01' AND time < '2025-01-01'"
        )
        deleted_prod = await conn.execute(
            "DELETE FROM production_data WHERE time >= '2024-01-01' AND time < '2025-01-01'"
        )
        deleted_env = await conn.execute(
            "DELETE FROM environmental_data WHERE time >= '2024-01-01' AND time < '2025-01-01'"
        )
        print(f"  Deleted: {deleted_energy}, {deleted_prod}, {deleted_env}\n")
        
        print("Generating data...")
        current = START_DATE
        total_records = 0
        energy_batch = []
        prod_batch = []
        env_batch = []
        batch_size = 1000
        
        start_time = asyncio.get_event_loop().time()
        
        while current <= END_DATE:
            for machine_id, config in MACHINES.items():
                power_kw, energy_kwh = calculate_power(machine_id, current)
                
                # Energy readings
                energy_batch.append((current, machine_id, power_kw, energy_kwh))
                
                # Production data (simple correlation: production ~ power * 20)
                production = int(power_kw * 20 + random.gauss(0, 50))
                production = max(0, production)
                if production > 0:
                    prod_batch.append((current, machine_id, production, int(production * 0.02)))
                
                # Environmental data (simple temp calculation)
                machine_temp = 45 + power_kw * 0.5 + random.gauss(0, 5)
                outdoor_temp = 15 + 10 * math.sin((current.timetuple().tm_yday - 90) * 2 * math.pi / 365)
                env_batch.append((current, machine_id, machine_temp, outdoor_temp))
            
            total_records += len(MACHINES)
            
            # Insert in batches
            if len(energy_batch) >= batch_size:
                await insert_chunk(conn, energy_batch)
                await insert_production_chunk(conn, prod_batch)
                await insert_environmental_chunk(conn, env_batch)
                energy_batch = []
                prod_batch = []
                env_batch = []
                
                # Progress update
                elapsed = asyncio.get_event_loop().time() - start_time
                progress = (current - START_DATE).days / 365 * 100
                rate = total_records / elapsed if elapsed > 0 else 0
                eta = (365 * len(MACHINES) * 24 * (3600/INTERVAL_SECONDS) - total_records) / rate if rate > 0 else 0
                
                print(f"  {current.date()} [{progress:5.1f}%] - {total_records:,} records "
                      f"({rate:,.0f}/s, ETA: {eta/60:.1f}min)")
            
            current += timedelta(seconds=INTERVAL_SECONDS)
        
        # Insert remaining
        if energy_batch:
            await insert_chunk(conn, energy_batch)
            await insert_production_chunk(conn, prod_batch)
            await insert_environmental_chunk(conn, env_batch)
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        print(f"\n✅ Backfill complete!")
        print(f"  Total records: {total_records:,}")
        print(f"  Duration: {elapsed/60:.1f} minutes")
        print(f"  Rate: {total_records/elapsed:,.0f} records/second")
        
        # Verify
        print("\nVerification:")
        for machine_id, config in MACHINES.items():
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM energy_readings WHERE machine_id = $1 AND time >= '2024-01-01' AND time < '2025-01-01'",
                machine_id
            )
            print(f"  {config['name']:20} - {count:,} records")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(backfill())
