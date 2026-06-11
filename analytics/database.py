"""
EnMS Analytics Service - Database Module
=========================================
Manages asyncpg connection pool and database operations.

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

import asyncpg
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from uuid import UUID

from config import settings

logger = logging.getLogger(__name__)


def slugify_feature_name(value: str) -> str:
    """Convert asset names into stable feature keys used by analytics models."""
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        """Initialize database manager."""
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                min_size=settings.DATABASE_MIN_POOL_SIZE,
                max_size=settings.DATABASE_MAX_POOL_SIZE,
                command_timeout=60
            )
            logger.info(
                f"✓ Database pool created: "
                f"{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
            )
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}", exc_info=True)
            raise
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    async def health_check(self) -> bool:
        """Check database connectivity."""
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
db = Database()


# ============================================================================
# Helper Functions for Data Retrieval
# ============================================================================

async def get_machines(
    factory_id: Optional[UUID] = None,
    is_active: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    Get list of machines.
    
    Args:
        factory_id: Optional factory filter
        is_active: Filter by active status (None = all machines)
        
    Returns:
        List of machine records
    """
    query = """
        SELECT 
            m.id, 
            m.factory_id, 
            m.name, 
            m.type, 
            m.rated_power_kw,
            m.is_active,
            m.metadata,
            m.metadata->>'asset_level' AS asset_level,
            m.metadata->>'energy_scope' AS energy_scope,
            m.metadata->>'group' AS group_key,
            f.name as factory_name,
            f.location as factory_location
        FROM machines m
        JOIN factories f ON m.factory_id = f.id
        WHERE 1=1
    """
    
    params = []
    param_count = 1
    
    if is_active is not None:
        query += f" AND m.is_active = ${param_count}"
        params.append(is_active)
        param_count += 1
    
    if factory_id:
        query += f" AND m.factory_id = ${param_count}"
        params.append(factory_id)
        param_count += 1
    
    query += " ORDER BY m.name"
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


async def get_machine_by_id(machine_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get machine by ID.
    
    Args:
        machine_id: Machine UUID
        
    Returns:
        Machine record or None
    """
    query = """
        SELECT 
            m.id, 
            m.factory_id, 
            m.name, 
            m.type, 
            m.rated_power_kw,
            m.is_active,
            m.metadata,
            m.metadata->>'asset_level' AS asset_level,
            m.metadata->>'energy_scope' AS energy_scope,
            m.metadata->>'source_dataset' AS source_dataset,
            f.name as factory_name,
            f.location as factory_location
        FROM machines m
        JOIN factories f ON m.factory_id = f.id
        WHERE m.id = $1
    """
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, machine_id)
        return dict(row) if row else None


async def get_energy_readings(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime,
    include_machine_status: bool = True
) -> List[Dict[str, Any]]:
    """
    Get energy readings for a machine within time range.
    Uses 1-hour continuous aggregate for efficiency.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        include_machine_status: Whether to filter by machine status
        
    Returns:
        List of energy reading records
    """
    # Base query using continuous aggregate (using 1min for now, TODO: create 1hour aggregate)
    query = """
        SELECT 
            er.bucket as time,
            er.machine_id,
            er.avg_power_kw,
            er.total_energy_kwh,
            er.max_power_kw as peak_demand_kw,
            er.min_power_kw,
            er.max_power_kw,
            er.avg_load_factor
        FROM energy_readings_1hour er
    """
    
    # Add machine status filter if requested
    if include_machine_status:
        query += """
            JOIN machine_status ms ON er.machine_id = ms.machine_id
        """
    
    query += """
        WHERE er.machine_id = $1
          AND er.bucket >= $2
          AND er.bucket <= $3
    """
    
    # Filter by machine status
    if include_machine_status:
        query += """
          AND ms.is_running = TRUE
          AND ms.current_mode NOT IN ('maintenance', 'fault', 'offline')
        """
    
    query += " ORDER BY er.bucket"
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        return [dict(row) for row in rows]


async def get_production_data(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Get production data for a machine within time range.
    Uses 1-hour continuous aggregate.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        
    Returns:
        List of production data records
    """
    query = """
        SELECT 
            pd.bucket as time,
            pd.machine_id,
            pd.total_production_count,
            pd.avg_throughput as avg_throughput_units_per_hour,
            pd.avg_throughput as max_throughput_units_per_hour
        FROM production_data_1hour pd
        WHERE pd.machine_id = $1
          AND pd.bucket >= $2
          AND pd.bucket <= $3
        ORDER BY pd.bucket
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        return [dict(row) for row in rows]


async def get_environmental_data(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Get environmental data for a machine within time range.
    Uses 1-hour continuous aggregate.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        
    Returns:
        List of environmental data records
    """
    query = """
        SELECT 
            ed.bucket as time,
            ed.machine_id,
            ed.avg_outdoor_temp_c,
            ed.avg_indoor_temp_c,
            ed.avg_machine_temp_c,
            ed.avg_outdoor_humidity_percent,
            ed.avg_indoor_humidity_percent,
            ed.avg_pressure_bar
        FROM environmental_data_1hour ed
        WHERE ed.machine_id = $1
          AND ed.bucket >= $2
          AND ed.bucket <= $3
        ORDER BY ed.bucket
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        return [dict(row) for row in rows]


async def get_machine_data_combined(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime,
    include_machine_status: bool = True,
    aggregate_interval: str = "1hour"
) -> List[Dict[str, Any]]:
    """
    Get combined data (energy + production + environmental) for ML training.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        include_machine_status: Whether to filter by machine status
        aggregate_interval: Continuous aggregate interval to query ("15min" or "1hour")
        
    Returns:
        List of combined data records
    """
    aggregate_views = {
        "15min": {
            "energy": "energy_readings_15min",
            "production": "production_data_15min",
            "environmental": "environmental_data_15min",
        },
        "1hour": {
            "energy": "energy_readings_1hour",
            "production": "production_data_1hour",
            "environmental": "environmental_data_1hour",
        },
    }

    if aggregate_interval not in aggregate_views:
        raise ValueError(f"Unsupported aggregate interval: {aggregate_interval}")

    views = aggregate_views[aggregate_interval]

    load_factor_column = "er.load_factor" if aggregate_interval == "15min" else "er.avg_load_factor"

    query = f"""
        SELECT 
            er.bucket as time,
            er.machine_id,
            er.avg_power_kw,
            er.total_energy_kwh,
            er.max_power_kw as peak_demand_kw,
            {load_factor_column} as avg_load_factor,
            pd.total_production_count,
            pd.avg_throughput as avg_throughput_units_per_hour,
            pd.total_production_good,
            pd.total_production_bad,
            CASE
                WHEN pd.total_production_count > 0
                THEN (pd.total_production_good::numeric / pd.total_production_count::numeric) * 100
                ELSE NULL
            END AS quality_percent,
            pd.avg_speed_percent,
            ed.avg_outdoor_temp_c,
            ed.avg_indoor_temp_c,
            ed.avg_machine_temp_c,
            ed.avg_pressure_bar,
            ed.avg_outdoor_humidity,
            ed.avg_indoor_humidity,
            ed.avg_flow_rate_m3h,
            EXTRACT(HOUR FROM er.bucket) as hour_of_day,
            EXTRACT(DOW FROM er.bucket) as day_of_week,
            CASE WHEN EXTRACT(DOW FROM er.bucket) IN (0, 6) THEN 1 ELSE 0 END as is_weekend,
            CASE WHEN EXTRACT(ISODOW FROM er.bucket) BETWEEN 1 AND 5 THEN 1 ELSE 0 END as is_working_day,
            CASE WHEN EXTRACT(ISODOW FROM er.bucket) = 6 THEN 1 ELSE 0 END as is_saturday,
            GREATEST(0, ed.avg_outdoor_temp_c - 18) as cooling_degree_hours,
            GREATEST(0, 18 - ed.avg_outdoor_temp_c) as heating_degree_hours,
            ABS(ed.avg_outdoor_temp_c - ed.avg_indoor_temp_c) as temp_difference,
            ed.avg_outdoor_temp_c * {load_factor_column} as temp_load_interaction,
            POWER(ed.avg_outdoor_temp_c, 2) as outdoor_temp_squared,
            POWER({load_factor_column}, 2) as load_factor_squared
        FROM {views['energy']} er
        LEFT JOIN {views['production']} pd 
            ON er.machine_id = pd.machine_id 
            AND er.bucket = pd.bucket
        LEFT JOIN {views['environmental']} ed 
            ON er.machine_id = ed.machine_id 
            AND er.bucket = ed.bucket
    """
    
    # Add machine status filter if requested
    if include_machine_status:
        query += """
            JOIN machine_status ms ON er.machine_id = ms.machine_id
        """
    
    query += """
        WHERE er.machine_id = $1
          AND er.bucket >= $2
          AND er.bucket <= $3
    """
    
    # Filter by machine status
    if include_machine_status:
        query += """
          AND ms.is_running = TRUE
          AND ms.current_mode NOT IN ('maintenance', 'fault', 'offline')
        """
    
    query += " ORDER BY er.bucket"
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        records = [dict(row) for row in rows]
        if records:
            await _add_partner_press_mix_features(
                conn=conn,
                records=records,
                meter_group_id=machine_id,
                start_time=start_time,
                end_time=end_time,
                production_view=views["production"],
            )
        return records


async def _add_partner_press_mix_features(
    conn: asyncpg.Connection,
    records: List[Dict[str, Any]],
    meter_group_id: UUID,
    start_time: datetime,
    end_time: datetime,
    production_view: str,
) -> None:
    """
    Add per-press production drivers to imported partner meter-group rows.

    Partner energy is only available at Bret/Raster/Dimeco meter-group level.
    These drivers preserve that boundary while allowing the group baseline to
    account for production mix inside each shared meter group.
    """
    machine = await conn.fetchrow(
        """
        SELECT factory_id, metadata->>'asset_level' AS asset_level, metadata->>'group' AS group_key
        FROM machines
        WHERE id = $1
        """,
        meter_group_id,
    )
    if not machine or machine["asset_level"] != "meter_group" or not machine["group_key"]:
        return

    presses = await conn.fetch(
        """
        SELECT id, name
        FROM machines
        WHERE factory_id = $1
          AND metadata->>'asset_level' = 'press'
          AND metadata->>'group' = $2
        ORDER BY name
        """,
        machine["factory_id"],
        machine["group_key"],
    )
    if not presses:
        return

    feature_by_press_id = {
        press["id"]: f"press_production_{slugify_feature_name(press['name'])}"
        for press in presses
    }
    active_feature_by_press_id = {
        press_id: feature_name.replace("press_production_", "press_active_", 1)
        for press_id, feature_name in feature_by_press_id.items()
    }

    for record in records:
        for feature_name in feature_by_press_id.values():
            record[feature_name] = 0.0
        for feature_name in active_feature_by_press_id.values():
            record[feature_name] = 0.0
        record["active_press_count"] = 0.0

    production_rows = await conn.fetch(
        f"""
        SELECT machine_id, bucket, total_production_count
        FROM {production_view}
        WHERE machine_id = ANY($1::uuid[])
          AND bucket >= $2
          AND bucket <= $3
        ORDER BY bucket
        """,
        list(feature_by_press_id.keys()),
        start_time,
        end_time,
    )

    records_by_time = {record["time"]: record for record in records}
    for row in production_rows:
        record = records_by_time.get(row["bucket"])
        if record is None:
            continue
        feature_name = feature_by_press_id.get(row["machine_id"])
        if feature_name:
            quantity = float(row["total_production_count"] or 0.0)
            record[feature_name] = quantity
            active_feature_name = active_feature_by_press_id.get(row["machine_id"])
            if active_feature_name and quantity > 0:
                record[active_feature_name] = 1.0

    for record in records:
        record["active_press_count"] = sum(
            float(record.get(feature_name, 0.0) or 0.0)
            for feature_name in active_feature_by_press_id.values()
        )


async def save_baseline_model(model_data: Dict[str, Any]) -> UUID:
    """
    Save baseline model to database.
    
    Args:
        model_data: Model metadata and parameters (must include energy_source_id)
        
    Returns:
        Model ID (UUID)
    """
    query = """
        INSERT INTO energy_baselines (
            machine_id, energy_source_id, model_name, model_type, model_version,
            training_start_date, training_end_date, training_samples,
            coefficients, intercept, feature_names,
            r_squared, rmse, mae, is_active, trained_by
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
        )
        RETURNING id
    """
    
    async with db.pool.acquire() as conn:
        model_id = await conn.fetchval(
            query,
            model_data['machine_id'],
            model_data['energy_source_id'],  # NEW: Required for multi-energy support
            model_data['model_name'],
            model_data.get('model_type', 'linear_regression'),
            model_data['model_version'],
            model_data['training_start_date'],
            model_data['training_end_date'],
            model_data['training_samples'],
            model_data['coefficients'],  # JSONB
            model_data.get('intercept'),
            model_data['feature_names'],  # Array
            model_data.get('r_squared'),
            model_data.get('rmse'),
            model_data.get('mae'),
            model_data.get('is_active', True),
            model_data.get('trained_by', 'analytics-service')
        )
    
    logger.info(f"✓ Baseline model saved: {model_id}")
    return model_id


async def save_anomaly(anomaly_data: Dict[str, Any]) -> UUID:
    """
    Save detected anomaly to database.
    
    Args:
        anomaly_data: Anomaly details
        
    Returns:
        Anomaly ID (UUID)
    """
    query = """
        INSERT INTO anomalies (
            machine_id, detected_at, anomaly_type, severity,
            metric_name, metric_value, expected_value,
            deviation_percent, deviation_std_dev,
            detection_method, confidence_score,
            is_resolved, resolved_at, resolution_notes, metadata
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15::jsonb
        )
        RETURNING id
    """

    metadata = anomaly_data.get('metadata')
    if metadata is None:
        metadata_json = '{}'
    elif isinstance(metadata, str):
        metadata_json = metadata
    else:
        metadata_json = json.dumps(metadata)
    
    async with db.pool.acquire() as conn:
        existing_id = await conn.fetchval(
            """
            SELECT id
            FROM anomalies
            WHERE machine_id = $1
              AND detected_at = $2
              AND anomaly_type = $3
              AND metric_name IS NOT DISTINCT FROM $4
            LIMIT 1
            """,
            anomaly_data['machine_id'],
            anomaly_data['detected_at'],
            anomaly_data['anomaly_type'],
            anomaly_data.get('metric_name'),
        )
        if existing_id:
            logger.info(
                "Anomaly already exists for %s at %s (%s); reusing %s",
                anomaly_data['machine_id'],
                anomaly_data['detected_at'],
                anomaly_data['anomaly_type'],
                existing_id,
            )
            return existing_id

        anomaly_id = await conn.fetchval(
            query,
            anomaly_data['machine_id'],
            anomaly_data['detected_at'],
            anomaly_data['anomaly_type'],
            anomaly_data['severity'],
            anomaly_data.get('metric_name'),
            anomaly_data.get('metric_value'),
            anomaly_data.get('expected_value'),
            anomaly_data.get('deviation_percent'),
            anomaly_data.get('deviation_std_dev'),
            anomaly_data.get('detection_method', 'isolation_forest'),
            anomaly_data.get('confidence_score'),
            anomaly_data.get('is_resolved', False),
            anomaly_data.get('resolved_at'),
            anomaly_data.get('resolution_notes'),
            metadata_json
        )
    
    logger.info(f"✓ Anomaly saved: {anomaly_id} ({anomaly_data['anomaly_type']})")
    return anomaly_id


async def get_active_baseline_model(
    machine_id: UUID, 
    energy_source_id: Optional[UUID] = None
) -> Optional[Dict[str, Any]]:
    """
    Get active baseline model for a machine and optionally specific energy source.
    
    Args:
        machine_id: Machine UUID
        energy_source_id: Optional energy source UUID (for multi-energy machines)
        
    Returns:
        Model record or None
    """
    if energy_source_id:
        # Get model for specific energy source (multi-energy support)
        query = """
            SELECT 
                id, machine_id, energy_source_id, model_name, model_type, model_version,
                training_start_date, training_end_date, training_samples,
                coefficients, intercept, feature_names,
                r_squared, rmse, mae, created_at
            FROM energy_baselines
            WHERE machine_id = $1 AND energy_source_id = $2 AND is_active = TRUE
            ORDER BY model_version DESC
            LIMIT 1
        """
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(query, machine_id, energy_source_id)
            return dict(row) if row else None
    else:
        # Backward compatibility: get first active model (any energy source)
        query = """
            SELECT 
                id, machine_id, energy_source_id, model_name, model_type, model_version,
                training_start_date, training_end_date, training_samples,
                coefficients, intercept, feature_names,
                r_squared, rmse, mae, created_at
            FROM energy_baselines
            WHERE machine_id = $1 AND is_active = TRUE
            ORDER BY model_version DESC
            LIMIT 1
        """
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(query, machine_id)
            return dict(row) if row else None


async def deactivate_baseline_models(machine_id: UUID, energy_source_id: Optional[UUID] = None):
    """
    Deactivate baseline models for a machine (optionally for specific energy source).
    Used before saving a new model.
    
    Args:
        machine_id: Machine UUID
        energy_source_id: Optional energy source UUID (for multi-energy machines)
    """
    if energy_source_id:
        # Deactivate only models for this energy source
        query = """
            UPDATE energy_baselines
            SET is_active = FALSE
            WHERE machine_id = $1 AND energy_source_id = $2 AND is_active = TRUE
        """
        async with db.pool.acquire() as conn:
            await conn.execute(query, machine_id, energy_source_id)
        logger.info(f"Deactivated baseline models for machine: {machine_id}, energy source: {energy_source_id}")
    else:
        # Deactivate all models (backward compatibility)
        query = """
            UPDATE energy_baselines
            SET is_active = FALSE
            WHERE machine_id = $1 AND is_active = TRUE
        """
        async with db.pool.acquire() as conn:
            await conn.execute(query, machine_id)
        logger.info(f"Deactivated all baseline models for machine: {machine_id}")
