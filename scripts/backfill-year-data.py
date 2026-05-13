#!/usr/bin/env python3
"""
Backfill one year of synthetic energy data for ISO 50001 baseline training.
This is for TESTING/DEMO purposes only - production should use real data.

Features:
- Seasonal variations (summer/winter)
- Daily patterns (work hours 8-17)
- Weekend reductions (50% capacity)
- Holiday shutdowns (New Year, Christmas)
- Maintenance periods (quarterly)
- Realistic power-production correlation

Usage: python3 scripts/backfill-year-data.py
"""

import asyncpg
import asyncio
from datetime import datetime, timedelta
import random
import os
import sys

# Database connection from environment
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'enms',
    'user': os.getenv('POSTGRES_USER', 'raptorblingx'),
    'password': os.getenv('POSTGRES_PASSWORD', 'raptorblingx')
}

# Machine configuration (from your existing data)
MACHINES = {
    'c0000000-0000-0000-0000-000000000001': {  # Compressor-1
        'name': 'Compressor-1',
        'power_base': 45,
        'power_variance': 15,
        'production_base': 1000,
        'temp_base': 65
    },
    'c0000000-0000-0000-0000-000000000006': {  # Compressor-2
        'name': 'Compressor-2',
        'power_base': 48,
        'power_variance': 12,
        'production_base': 1200,
        'temp_base': 68
    }
}

# Holidays (machines shut down)
HOLIDAYS_2024 = [
    datetime(2024, 1, 1),   # New Year
    datetime(2024, 4, 19),  # Good Friday
    datetime(2024, 5, 1),   # Labor Day
    datetime(2024, 12, 25), # Christmas
    datetime(2024, 12, 26), # Boxing Day
]

# Maintenance periods (one week each quarter)
MAINTENANCE_PERIODS = [
    (datetime(2024, 3, 15), datetime(2024, 3, 22)),  # Q1
    (datetime(2024, 6, 10), datetime(2024, 6, 17)),  # Q2
    (datetime(2024, 9, 5), datetime(2024, 9, 12)),   # Q3
    (datetime(2024, 12, 2), datetime(2024, 12, 9)),  # Q4
]

def is_weekend(dt):
    """Check if date is weekend (Saturday=5, Sunday=6)."""
    return dt.weekday() >= 5

def is_holiday(dt):
    """Check if date is a holiday."""
    return dt.date() in [h.date() for h in HOLIDAYS_2024]

def is_maintenance(dt):
    """Check if date is in maintenance period."""
    for start, end in MAINTENANCE_PERIODS:
        if start <= dt <= end:
            return True
    return False

async def backfill_data():
    """Generate one year of synthetic data."""
    
    print("Connecting to database...")
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Start date: Jan 1, 2024
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31, 23, 59, 59)
        
        print(f"📅 Backfilling data from {start_date.date()} to {end_date.date()}")
        print(f"🏭 Machines: {len(MACHINES)}")
        for mid, config in MACHINES.items():
            print(f"   - {config['name']} (base power: {config['power_base']} kW)")
        
        # Delete existing data in 2024 range (if any)
        print("\n🗑️  Clearing existing 2024 data...")
        deleted = await conn.execute(
            "DELETE FROM energy_readings WHERE time >= $1 AND time < $2",
            start_date, datetime(2025, 1, 1)
        )
        print(f"   Removed: {deleted}")
        
        # Also clear production and environmental data
        await conn.execute(
            "DELETE FROM production_data WHERE time >= $1 AND time < $2",
            start_date, datetime(2025, 1, 1)
        )
        await conn.execute(
            "DELETE FROM environmental_data WHERE time >= $1 AND time < $2",
            start_date, datetime(2025, 1, 1)
        )
        
        # Generate data every 10 seconds for full year
        print(f"\n📊 Generating synthetic data (10-second intervals)...")
        print(f"   - Seasonal variations: ✓")
        print(f"   - Daily patterns (8-17 work hours): ✓")
        print(f"   - Weekend reductions (50%): ✓")
        print(f"   - Holiday shutdowns ({len(HOLIDAYS_2024)} days): ✓")
        print(f"   - Maintenance periods ({len(MAINTENANCE_PERIODS)} weeks): ✓\n")
        
        current_time = start_date
        interval = timedelta(seconds=10)
        batch_size = 1000
        batch = []
        total_inserted = 0
        records_skipped = 0
        
        while current_time <= end_date:
            # Check if machines should be running
            if is_holiday(current_time):
                # Skip holidays (machines off)
                current_time += interval
                records_skipped += len(MACHINES)
                continue
            
            if is_maintenance(current_time):
                # Skip maintenance periods
                current_time += interval
                records_skipped += len(MACHINES)
                continue
            
            for machine_id, config in MACHINES.items():
                # Add seasonal and daily patterns
                hour = current_time.hour
                month = current_time.month
                day_of_week = current_time.weekday()
                
                # Weekend reduction (50% capacity)
                weekend_factor = 0.5 if is_weekend(current_time) else 1.0
                
                # Daily pattern (higher during work hours 8-17)
                if 8 <= hour < 17:
                    hour_factor = 1.2  # Peak production
                elif 6 <= hour < 20:
                    hour_factor = 0.8  # Ramp up/down
                else:
                    hour_factor = 0.3  # Night shift minimal
                
                # Seasonal pattern (higher in summer for cooling compressors)
                # Peak in July/August, lowest in January/February
                month_factor = 1.0 + 0.25 * ((month - 1.5) / 10.5)
                
                # Combined factor
                total_factor = hour_factor * month_factor * weekend_factor
                
                # Generate power with patterns + randomness
                base_power = config['power_base']
                power_kw = base_power * total_factor + random.gauss(0, config['power_variance'] * 0.3)
                power_kw = max(5, min(100, power_kw))  # Clamp to reasonable range
                
                # Energy = Power * Time interval (in hours)
                energy_kwh = power_kw * (10 / 3600)  # 10 seconds in hours
                
                # Production (strongly correlated with power, R²≈0.85+)
                production_correlation = 0.9  # High correlation for good baseline
                production_base = config['production_base'] * total_factor
                production_random = production_base * (1 - production_correlation) * random.uniform(0.8, 1.2)
                production_from_power = (power_kw / base_power) * config['production_base'] * production_correlation
                production = int(production_from_power + production_random)
                production = max(0, production)
                
                # Temperature (seasonal + daily pattern + machine load)
                outdoor_temp = 15 + 15 * ((month - 1) / 11) - 10 * ((month - 6.5) / 5.5) + random.gauss(0, 3)
                machine_temp = config['temp_base'] + (power_kw / base_power) * 10 + random.gauss(0, 2)
                
                batch.append((
                    current_time,
                    machine_id,
                    power_kw,
                    energy_kwh,
                    production,
                    machine_temp,
                    outdoor_temp
                ))
            
            current_time += interval
            
            # Insert in batches with progress indicator
            if len(batch) >= batch_size:
                await insert_batch(conn, batch)
                total_inserted += len(batch)
                
                # Progress indicator
                days_processed = (current_time - start_date).days
                total_days = 365
                progress_pct = (days_processed / total_days) * 100
                
                print(f"   {current_time.date()} | {progress_pct:5.1f}% | {total_inserted:,} records | {records_skipped:,} skipped", end='\r')
                batch = []
        
        # Insert remaining
        if batch:
            await insert_batch(conn, batch)
            total_inserted += len(batch)
        
        print(f"\n\n✅ Backfill complete!")
        print(f"   📊 Total records inserted: {total_inserted:,}")
        print(f"   ⏭️  Records skipped (holidays/maintenance): {records_skipped:,}")
        
        # Verify data with detailed breakdown
        print(f"\n🔍 Verifying database...")
        
        for table in ['energy_readings', 'production_data', 'environmental_data']:
            count = await conn.fetchval(
                f"SELECT COUNT(*) FROM {table} WHERE time >= $1 AND time < $2",
                start_date, datetime(2025, 1, 1)
            )
            print(f"   {table}: {count:,} records")
        
        # Check data range
        min_date, max_date = await conn.fetchrow(
            "SELECT MIN(time)::date, MAX(time)::date FROM energy_readings WHERE time >= $1",
            start_date
        )
        print(f"\n   Date range: {min_date} to {max_date}")
        
        # Sample data points
        print(f"\n📈 Sample data points:")
        samples = await conn.fetch(
            """
            SELECT time::date as day, AVG(power_kw)::numeric(10,2) as avg_power
            FROM energy_readings
            WHERE time >= $1 AND time < $2
            GROUP BY day
            ORDER BY day
            LIMIT 5
            """,
            start_date, datetime(2025, 1, 1)
        )
        for row in samples:
            print(f"   {row['day']}: {row['avg_power']} kW (avg)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await conn.close()
        print(f"\n✅ Database connection closed")

async def insert_batch(conn, batch):
    """Insert batch of records into all three tables."""
    # Insert into energy_readings
    await conn.executemany(
        """
        INSERT INTO energy_readings (time, machine_id, power_kw, energy_kwh)
        VALUES ($1, $2, $3, $4)
        """,
        [(t, m, p, e) for t, m, p, e, prod, mtemp, otemp in batch]
    )
    
    # Insert into production_data
    await conn.executemany(
        """
        INSERT INTO production_data (time, machine_id, production_count, production_count_bad, throughput_units_per_hour)
        VALUES ($1, $2, $3, $4, $5)
        """,
        [(t, m, prod, int(prod * 0.02), prod * 6) for t, m, p, e, prod, mtemp, otemp in batch]
    )
    
    # Insert into environmental_data
    await conn.executemany(
        """
        INSERT INTO environmental_data (time, machine_id, machine_temp_c, outdoor_temp_c, indoor_temp_c)
        VALUES ($1, $2, $3, $4, $5)
        """,
        [(t, m, mtemp, otemp, otemp + 5) for t, m, p, e, prod, mtemp, otemp in batch]
    )

if __name__ == '__main__':
    print("=" * 70)
    print("  ISO 50001 Data Backfill Script - DEMO VERSION")
    print("=" * 70)
    print("\n⚠️  WARNING: This generates SYNTHETIC data for testing/demo.")
    print("   For production ISO 50001 compliance, use REAL historical data.\n")
    print("📋 What will be generated:")
    print("   - Year: 2024 (full calendar year)")
    print("   - Interval: 10 seconds")
    print("   - Machines: 2 compressors")
    print("   - Expected records: ~3.1 million (before holidays/maintenance)")
    print("   - Features: Seasonal, daily, weekend, holiday patterns")
    print("   - Estimated time: 3-5 minutes\n")
    
    response = input("Continue with backfill? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        print("")
        asyncio.run(backfill_data())
        print("\n" + "=" * 70)
        print("  Next steps:")
        print("  1. Create/get SEU ID: curl http://localhost:8001/api/v1/seus")
        print("  2. Train baseline: POST /api/v1/baseline/seu/train")
        print("  3. Generate report: POST /api/v1/reports/seu-performance")
        print("  4. View in Grafana dashboard")
        print("=" * 70)
    else:
        print("❌ Cancelled.")
