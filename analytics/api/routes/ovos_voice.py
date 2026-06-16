"""
EnMS Analytics - OVOS Voice Bridge Proxy
=========================================
Proxy endpoint for forwarding natural language queries to OVOS REST Bridge.

This is separate from ovos.py which contains direct database query endpoints.
This router proxies text queries to the OVOS voice assistant system.

Architecture:
    EnMS Frontend → This Proxy → OVOS REST Bridge (WSL2:5000) → OVOS Messagebus → EnMS Skill

Configuration via environment variables:
    OVOS_BRIDGE_HOST: IP address of OVOS REST Bridge (default: 192.168.1.103)
    OVOS_BRIDGE_PORT: Port of OVOS REST Bridge (default: 5000)
    OVOS_BRIDGE_TIMEOUT: Request timeout in seconds (default: 20)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path

from database import db
from services.energy_performance_engine import get_performance_engine
from services.enpi_tracker import EnPITracker
from api.routes.ovos import get_top_consumers
from api.routes.partner_press import PARTNER_FACTORY_NAME, get_partner_press_summary
from reports_v2.services.report_service import ReportGenerationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ovos/voice", tags=["OVOS Voice"])

# ============================================================================
# Configuration (Environment Variables)
# ============================================================================

OVOS_BRIDGE_HOST = os.getenv("OVOS_BRIDGE_HOST", "192.168.1.103")
OVOS_BRIDGE_PORT = os.getenv("OVOS_BRIDGE_PORT", "5000")
OVOS_BRIDGE_TIMEOUT = float(os.getenv("OVOS_BRIDGE_TIMEOUT", "20"))
OVOS_BRIDGE_URL = f"http://{OVOS_BRIDGE_HOST}:{OVOS_BRIDGE_PORT}"
PARTNER_PRESS_PILOT_DEFAULT = os.getenv("PARTNER_PRESS_PILOT_DEFAULT", "false").lower() == "true"
SIMULATED_PILOT_FACTORY_ID = os.getenv(
    "SIMULATED_PILOT_FACTORY_ID",
    "11111111-1111-1111-1111-111111111111",
)
SIMULATED_PILOT_ENPI_PERIOD = os.getenv("SIMULATED_PILOT_ENPI_PERIOD", "2026-Q1")
SIMULATED_PILOT_BASELINE_YEAR = int(os.getenv("SIMULATED_PILOT_BASELINE_YEAR", "2026"))
SIMULATED_PILOT_OPPORTUNITY_PERIOD = os.getenv("SIMULATED_PILOT_OPPORTUNITY_PERIOD", "month")
SIMULATED_PILOT_REPORT_YEAR = int(os.getenv("SIMULATED_PILOT_REPORT_YEAR", "2026"))
SIMULATED_PILOT_REPORT_MONTH = int(os.getenv("SIMULATED_PILOT_REPORT_MONTH", "4"))
enpi_tracker = EnPITracker()


# ============================================================================
# Request/Response Models
# ============================================================================

class VoiceQueryRequest(BaseModel):
    """Request model for voice query"""
    text: str
    session_id: Optional[str] = None
    include_audio: bool = True  # Request audio response from OVOS TTS
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "What's the energy consumption for Compressor-1?",
                "session_id": None,
                "include_audio": True
            }
        }


class VoiceQueryResponse(BaseModel):
    """Response model for voice query with optional audio"""
    success: bool
    response: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    data: Optional[dict] = None
    insights: Optional[dict] = None
    audio_base64: Optional[str] = None  # Base64 encoded WAV audio from OVOS TTS
    audio_format: Optional[str] = None  # Audio format (wav, mp3, etc.) - None if no audio
    pdf_base64: Optional[str] = None  # LEGACY: Base64 encoded PDF for report downloads (V1)
    pdf_filename: Optional[str] = None  # LEGACY: Suggested filename for PDF download (V1)
    pdf_download: Optional[dict] = None  # V2: PDF download metadata {report_id, download_url, filename, file_size_kb, ready}
    error: Optional[str] = None
    session_id: str
    latency_ms: int
    tts_latency_ms: int = 0
    timestamp: str
    bridge_url: str


class VoiceBridgeHealth(BaseModel):
    """Health check response for OVOS bridge"""
    status: str
    bridge_reachable: bool
    bridge_url: str
    ovos_connected: Optional[bool] = None
    tts_available: Optional[bool] = None
    tts_engine: Optional[str] = None
    error: Optional[str] = None


def _normalize_query(text: str) -> str:
    return " ".join((text or "").lower().strip().split())


def _normalize_partner_speech_text(text: str) -> str:
    """Correct common browser-STT mistakes for ASSA ABLOY pilot asset names."""
    normalized = f" {text or ''} "
    replacements = [
        (r"\bthe breakfast club\b", "the Bret press group"),
        (r"\bbreakfast club\b", "Bret press group"),
        (r"\bbreakfast group\b", "Bret press group"),
        (r"\bbreakfast press(?:es)?(?: group)?\b", "Bret press group"),
        (r"\bfor breakfast\b", "for Bret press group"),
        (r"\bgreat businesses\b", "Bret presses"),
        (r"\bfor the purposes\b", "for Bret presses"),
        (r"\bbread press(?:es)?\b", "Bret presses"),
        (r"\bbrett press(?:es)?\b", "Bret presses"),
        (r"\bbrett\b", "Bret"),
        (r"\bbrent\b", "Bret"),
        (r"\bbrat\b", "Bret"),
        (r"\bbreath press(?:es)?\b", "Bret presses"),
        (r"\bdime echo\b", "Dimeco"),
        (r"\bdim echo\b", "Dimeco"),
        (r"\bdynamo\b", "Dimeco"),
        (r"\bdy meco\b", "Dimeco"),
        (r"\bdie meco\b", "Dimeco"),
        (r"\bdinoco\b", "Dimeco"),
        (r"\brasta\b", "Raster"),
        (r"\brastor\b", "Raster"),
        (r"\braster presses?\b", "Raster presses"),
        (r"\bflexy\b", "Flexi"),
        (r"\bshoe eighty\b", "Schu80"),
        (r"\bshoe 80\b", "Schu80"),
        (r"\bschu eighty\b", "Schu80"),
        (r"\braster one sixty\b", "Rast160"),
        (r"\brast one sixty\b", "Rast160"),
        (r"\bbret one twenty five\b", "Bret125"),
        (r"\bbret one sixty\b", "Bret160"),
        (r"\bbret two fifty\b", "Bret250"),
        (r"\b(?:press\s+)?group (?:one|won|1)\b", "Bret press group"),
        (r"\b(?:press\s+)?group (?:two|2|to|too)\b", "Raster press group"),
        (r"\b(?:press\s+)?group (?:three|tree|3)\b", "Dimeco press group"),
        (r"\b(?:first|left) (?:press\s+)?group\b", "Bret press group"),
        (r"\b(?:second|middle|center|centre) (?:press\s+)?group\b", "Raster press group"),
        (r"\b(?:third|right) (?:press\s+)?group\b", "Dimeco press group"),
        (r"\boption (?:one|1)\b", "Bret press group"),
        (r"\boption (?:two|2|to|too)\b", "Raster press group"),
        (r"\boption (?:three|3)\b", "Dimeco press group"),
    ]
    for pattern, replacement in replacements:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    return " ".join(normalized.split())


def _is_enpi_query(text: str) -> bool:
    normalized = _normalize_query(text)
    phrases = [
        "energy performance indicator report",
        "energy performance indicators report",
        "show energy performance indicator",
        "performance indicator report",
        "performance indicators report",
        "enpi report",
        "enpi status",
        "iso 50001 report",
        "iso 50001 enpi",
    ]
    return any(phrase in normalized for phrase in phrases)


def _is_opportunity_query(text: str) -> bool:
    normalized = _normalize_query(text)
    phrases = [
        "energy saving opportunities",
        "energy improvement opportunities",
        "optimization opportunities",
        "where can we save energy",
        "save energy",
    ]
    return any(phrase in normalized for phrase in phrases)


def _is_top_consumers_query(text: str) -> bool:
    normalized = _normalize_query(text)
    return (
        "top" in normalized
        and any(term in normalized for term in ["consumer", "consumers", "energy users", "machines"])
        and any(term in normalized for term in ["energy", "consumption", "power"])
    )


def _is_partner_press_query(text: str) -> bool:
    normalized = _normalize_query(text)
    terms = [
        "assa abloy",
        "partner",
        "press shop",
        "press-shop",
        "bret",
        "raster",
        "dimeco",
        "dime echo",
        "dim echo",
        "dynamo",
        "breakfast club",
        "breakfast group",
        "brett",
        "brent",
        "rasta",
        "rastor",
        "flexy",
        "group one",
        "group two",
        "group three",
        "press group one",
        "press group two",
        "press group three",
        "first group",
        "second group",
        "third group",
        "sqdc",
    ]
    return any(term in normalized for term in terms)


def _is_partner_pilot_default_query(text: str) -> bool:
    normalized = _normalize_query(text)
    if _is_partner_press_query(normalized):
        return True
    if not PARTNER_PRESS_PILOT_DEFAULT:
        return False

    demo_terms = [
        "compressor", "boiler", "hvac", "conveyor", "injection", "molding",
        "hydraulic", "pump", "machine status", "anomaly", "forecast",
        "report", "enpi", "baseline", "opportunity", "save energy",
    ]
    if any(term in normalized for term in demo_terms):
        return False

    partner_default_terms = [
        "energy", "consumption", "kwh", "electricity", "power",
        "production", "produced", "quantity", "units", "parts",
        "kpi", "sec", "energy per", "top consumer", "top consumers",
        "summary", "overview",
    ]
    return any(term in normalized for term in partner_default_terms)


MONTH_ALIASES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _is_report_download_query(text: str) -> bool:
    normalized = _normalize_query(text)
    return (
        "report" in normalized
        and any(term in normalized for term in ["download", "generate", "create", "export", "pdf"])
    )


def _parse_report_period(text: str) -> tuple[int, int]:
    normalized = _normalize_query(text).replace(",", " ")
    tokens = normalized.split()

    month = None
    for token in tokens:
        cleaned = token.strip(".")
        if cleaned in MONTH_ALIASES:
            month = MONTH_ALIASES[cleaned]
            break

    year = None
    for token in tokens:
        cleaned = token.strip(".")
        if cleaned.isdigit() and len(cleaned) == 4:
            parsed_year = int(cleaned)
            if 2000 <= parsed_year <= 2100:
                year = parsed_year
                break

    return (
        year or SIMULATED_PILOT_REPORT_YEAR,
        month or SIMULATED_PILOT_REPORT_MONTH,
    )


def _top_consumer_limit(text: str) -> int:
    if "top 3" in text or "top three" in text:
        return 3
    return 5


async def _resolve_report_factory_id(normalized_text: str) -> str:
    """Resolve report factory for the active pilot instead of using stale demo UUIDs."""
    preferred_name = PARTNER_FACTORY_NAME if _is_partner_pilot_default_query(normalized_text) else None

    async with db.pool.acquire() as conn:
        if preferred_name:
            factory_id = await conn.fetchval(
                """
                SELECT id::text
                FROM factories
                WHERE name = $1
                  AND is_active = TRUE
                LIMIT 1
                """,
                preferred_name,
            )
            if factory_id:
                return factory_id

        factory_id = await conn.fetchval(
            """
            SELECT id::text
            FROM factories
            WHERE id::text = $1
              AND is_active = TRUE
            LIMIT 1
            """,
            SIMULATED_PILOT_FACTORY_ID,
        )
        if factory_id:
            return factory_id

        factory_id = await conn.fetchval(
            """
            SELECT id::text
            FROM factories
            WHERE is_active = TRUE
            ORDER BY name
            LIMIT 1
            """
        )
        if not factory_id:
            raise ValueError("No active factory is available for report generation")
        return factory_id


def _humanize_status(value: str) -> str:
    return str(value or "unknown").replace("_", " ")


async def _build_enpi_fallback_response(session_id: str, start_time: datetime) -> VoiceQueryResponse:
    report = await enpi_tracker.generate_enpi_report(
        factory_id=SIMULATED_PILOT_FACTORY_ID,
        period=SIMULATED_PILOT_ENPI_PERIOD,
        baseline_year=SIMULATED_PILOT_BASELINE_YEAR,
    )

    performance = report["overall_performance"]
    actual_kwh = performance["total_energy_actual_kwh"]
    baseline_kwh = performance["total_energy_baseline_kwh"]
    deviation_percent = performance["deviation_percent"]
    deviation_kwh = performance.get("deviation_kwh", actual_kwh - baseline_kwh)
    gap_kwh = abs(deviation_kwh)

    if deviation_percent > 0:
        direction_text = "above baseline"
        gap_text = f"a {gap_kwh:,.1f} kilowatt-hour performance gap to review"
    elif deviation_percent < 0:
        direction_text = "below baseline"
        gap_text = f"{gap_kwh:,.1f} kilowatt-hours of savings against baseline"
    else:
        direction_text = "aligned with baseline"
        gap_text = "no material performance gap"

    response = (
        f"For {SIMULATED_PILOT_ENPI_PERIOD}, the ISO 50001 EnPI status is {_humanize_status(performance['iso_status'])}. "
        f"{report['seus_analyzed']} significant energy uses were analyzed. Actual energy was {actual_kwh:,.1f} kilowatt hours "
        f"versus a {baseline_kwh:,.1f} kilowatt-hour baseline, which is {abs(deviation_percent):.2f} percent {direction_text}. "
        f"This indicates {gap_text}."
    )

    latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    return VoiceQueryResponse(
        success=True,
        response=response,
        intent="enpi_report",
        confidence=1.0,
        data=report,
        insights={
            "source": "analytics_fallback",
            "period": SIMULATED_PILOT_ENPI_PERIOD,
            "baseline_year": SIMULATED_PILOT_BASELINE_YEAR,
        },
        audio_base64=None,
        audio_format=None,
        pdf_base64=None,
        pdf_filename=None,
        pdf_download=None,
        error=None,
        session_id=session_id,
        latency_ms=latency_ms,
        tts_latency_ms=0,
        timestamp=datetime.now().isoformat(),
        bridge_url=OVOS_BRIDGE_URL,
    )


async def _build_top_consumers_fallback_response(session_id: str, start_time: datetime, normalized_text: str) -> VoiceQueryResponse:
    limit = _top_consumer_limit(normalized_text)
    if _is_partner_pilot_default_query(normalized_text):
        partner_data = await get_partner_press_summary(
            question_type="top_energy",
            group=None,
            press=None,
            start_time=None,
            end_time=None,
        )
        energy_by_group = partner_data.get("energy_by_group", [])[:limit]
        total_value = float(partner_data.get("total_energy_kwh") or 0)
        ranking = [
            {
                "rank": idx,
                "machine_id": item.get("group"),
                "machine_name": item.get("asset_name"),
                "machine_type": "meter_group",
                "value": round(float(item.get("energy_kwh") or 0), 2),
                "percentage": round((float(item.get("energy_kwh") or 0) / total_value * 100), 1) if total_value else 0,
                "energy_kwh": round(float(item.get("energy_kwh") or 0), 2),
                "cost_usd": round(float(item.get("energy_kwh") or 0) * 0.15, 2),
                "avg_power_kw": round(float(item.get("avg_power_kw") or 0), 2),
            }
            for idx, item in enumerate(energy_by_group, start=1)
        ]
        ranking_data = {
            "metric": "energy",
            "metric_label": "Energy Consumption",
            "time_period": partner_data.get("period"),
            "factory_filter": "Partner Press Shop",
            "total_value": round(total_value, 2),
            "unit": "kWh",
            "machines_analyzed": len(ranking),
            "ranking": ranking,
            "scope_note": partner_data.get("scope_note"),
            "source_dataset": partner_data.get("source_dataset"),
            "auxiliary_energy": partner_data.get("auxiliary_energy", []),
        }
        response_override = partner_data.get("response")
        subtitle = "Partner press-shop dataset, May 2025 through May 2026"
    else:
        ranking_data = await get_top_consumers(metric="energy", limit=limit)
        response_override = None
        subtitle = "Current ranking snapshot"
    ranking = ranking_data.get("ranking", [])

    latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    if not ranking:
        response_text = "No energy-consumption ranking data is available for the current period."
        return VoiceQueryResponse(
            success=True,
            response=response_text,
            intent="ranking",
            confidence=1.0,
            data=ranking_data,
            insights={"source": "analytics_fallback", "metric": "energy", "factory_filter": ranking_data.get("factory_filter")},
            audio_base64=None,
            audio_format=None,
            pdf_base64=None,
            pdf_filename=None,
            pdf_download=None,
            error=None,
            session_id=session_id,
            latency_ms=latency_ms,
            tts_latency_ms=0,
            timestamp=datetime.now().isoformat(),
            bridge_url=OVOS_BRIDGE_URL,
        )

    total_value = ranking_data.get("total_value", 0)
    response_text = response_override or (
        f"Top {len(ranking)} energy consumers:\n" + "\n".join(
            f"{item['rank']}. {item['machine_name']}: {item['value']} kWh ({item['percentage']}% of total)"
            for item in ranking
        )
    )

    top_item = ranking[0]
    return VoiceQueryResponse(
        success=True,
        response=response_text,
        intent="ranking",
        confidence=1.0,
        data=ranking_data,
        insights={
            "panel_type": "ranking",
            "title": "Energy Consumption",
            "subtitle": subtitle,
            "spotlight": {
                "kicker": "Top consumer",
                "title": top_item["machine_name"],
                "detail": f"{top_item['value']} kWh · {top_item['percentage']}% of tracked load",
                "tone": "info",
            },
            "summary_metrics": [
                {"label": "Top Value", "value": top_item["value"], "unit": "kWh", "tone": "info"},
                {"label": "Leader Share", "value": top_item["percentage"], "unit": "%", "tone": "good"},
                {"label": "Machines", "value": ranking_data.get("machines_analyzed", len(ranking)), "unit": None, "tone": "neutral"},
                {"label": "Total", "value": total_value, "unit": "kWh", "tone": "warning"},
            ],
            "status_badges": [{"label": "Energy", "tone": "neutral"}],
            "secondary_lines": [
                f"{item['rank']}. {item['machine_name']} - {item['value']} kWh ({item['percentage']}%)"
                for item in ranking[:3]
            ],
            "links": [{"label": "Open reports", "href": "/reports.html"}],
            "source": "analytics_fallback",
            "factory_filter": ranking_data.get("factory_filter"),
        },
        audio_base64=None,
        audio_format=None,
        pdf_base64=None,
        pdf_filename=None,
        pdf_download=None,
        error=None,
        session_id=session_id,
        latency_ms=latency_ms,
        tts_latency_ms=0,
        timestamp=datetime.now().isoformat(),
        bridge_url=OVOS_BRIDGE_URL,
    )


async def _build_report_download_response(
    session_id: str,
    start_time: datetime,
    normalized_text: str,
) -> VoiceQueryResponse:
    year, month = _parse_report_period(normalized_text)
    month_name = datetime(year, month, 1).strftime("%B")
    report_id = str(uuid.uuid4())
    output_path = Path(f"/tmp/enms_report_v2_{report_id}.pdf")
    factory_id = await _resolve_report_factory_id(normalized_text)

    service = ReportGenerationService(db)
    result_path = await service.generate_monthly_report(
        factory_id=factory_id,
        year=year,
        month=month,
        output_path=output_path,
    )
    file_size_kb = result_path.stat().st_size / 1024
    filename = f"HumanEnerDIA_Monthly_Energy_Report_{year}_{month:02d}.pdf"
    download_url = f"/api/v1/reports/v2/download/{report_id}"

    latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    return VoiceQueryResponse(
        success=True,
        response=(
            f"{month_name} {year} monthly energy report is ready. "
            "The browser download should start now."
        ),
        intent="report_download",
        confidence=1.0,
        data={
            "success": True,
            "factory_id": factory_id,
            "report_id": report_id,
            "report_type": "monthly_energy",
            "year": year,
            "month": month,
            "filename": filename,
            "download_url": download_url,
            "file_size_kb": round(file_size_kb, 2),
        },
        insights={
            "panel_type": "report_download",
            "title": "Monthly Energy Report",
            "subtitle": f"{month_name} {year}",
            "spotlight": {
                "kicker": "Report ready",
                "title": filename,
                "detail": f"{round(file_size_kb, 1)} KB PDF generated from analytics data",
                "tone": "good",
            },
            "status_badges": [
                {"label": "PDF", "tone": "neutral"},
                {"label": month_name, "tone": "info"},
                {"label": str(year), "tone": "neutral"},
            ],
            "links": [{"label": "Open reports", "href": "/reports.html"}],
            "source": "analytics_fallback",
        },
        audio_base64=None,
        audio_format=None,
        pdf_base64=None,
        pdf_filename=None,
        pdf_download={
            "report_id": report_id,
            "download_url": download_url,
            "filename": filename,
            "file_size_kb": round(file_size_kb, 2),
            "ready": True,
        },
        error=None,
        session_id=session_id,
        latency_ms=latency_ms,
        tts_latency_ms=0,
        timestamp=datetime.now().isoformat(),
        bridge_url=OVOS_BRIDGE_URL,
    )


async def _build_opportunities_fallback_response(session_id: str, start_time: datetime) -> VoiceQueryResponse:
    engine = get_performance_engine()
    opportunities = await engine.get_improvement_opportunities(
        SIMULATED_PILOT_FACTORY_ID,
        SIMULATED_PILOT_OPPORTUNITY_PERIOD,
    )

    latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    if not opportunities:
        response_text = (
            "No major factory-wide improvement opportunities were detected for the configured pilot period. "
            "Focus on current deviations, anomalies, and scheduling review."
        )
        return VoiceQueryResponse(
            success=True,
            response=response_text,
            intent="performance_opportunities",
            confidence=1.0,
            data={"opportunities": []},
            insights={"source": "analytics_fallback", "period": SIMULATED_PILOT_OPPORTUNITY_PERIOD},
            audio_base64=None,
            audio_format=None,
            pdf_base64=None,
            pdf_filename=None,
            pdf_download=None,
            error=None,
            session_id=session_id,
            latency_ms=latency_ms,
            tts_latency_ms=0,
            timestamp=datetime.now().isoformat(),
            bridge_url=OVOS_BRIDGE_URL,
        )

    top_items = opportunities[:3]
    response_text = "Top energy saving opportunities: " + " ".join(
        f"{index}. {opp.seu_name}, about {opp.potential_savings_kwh:.1f} kilowatt hours."
        for index, opp in enumerate(top_items, start=1)
    )
    response_text += " Recommended action: time-based setback scheduling for off-hours operation."

    return VoiceQueryResponse(
        success=True,
        response=response_text,
        intent="performance_opportunities",
        confidence=1.0,
        data={
            "total_opportunities": len(opportunities),
            "total_potential_savings_kwh": round(sum(opp.potential_savings_kwh for opp in opportunities), 2),
            "top_opportunities": [
                {
                    "seu_name": opp.seu_name,
                    "issue_type": opp.issue_type.value if hasattr(opp.issue_type, "value") else str(opp.issue_type),
                    "potential_savings_kwh": opp.potential_savings_kwh,
                    "recommended_action": opp.recommended_action,
                }
                for opp in top_items
            ],
        },
        insights={"source": "analytics_fallback", "period": SIMULATED_PILOT_OPPORTUNITY_PERIOD},
        audio_base64=None,
        audio_format=None,
        pdf_base64=None,
        pdf_filename=None,
        pdf_download=None,
        error=None,
        session_id=session_id,
        latency_ms=latency_ms,
        tts_latency_ms=0,
        timestamp=datetime.now().isoformat(),
        bridge_url=OVOS_BRIDGE_URL,
    )


def _repair_bridge_payload(payload: dict, normalized_text: str) -> dict:
    if not isinstance(payload, dict):
        return payload

    response_text = payload.get("response")
    if isinstance(response_text, str):
        payload["response"] = response_text.replace("Top  energy consumers:", "Top energy consumers:")
        if "top 3 energy consumers" in normalized_text:
            payload["response"] = payload["response"].replace("Top energy consumers:", "Top 3 energy consumers:")

    return _repair_anomaly_insights(payload)


def _repair_anomaly_insights(payload: dict) -> dict:
    """
    Normalize anomaly insight counts from bridge responses using the raw anomaly list.

    Some bridge responses summarize the anomaly text correctly but return stale
    severity counts in the insight card. For the simulated pilot we want the
    card totals to match the actual anomaly payload used in the demo.
    """
    if not isinstance(payload, dict):
        return payload

    data = payload.get("data")
    insights = payload.get("insights")
    if not isinstance(data, dict) or not isinstance(insights, dict):
        return payload

    if insights.get("panel_type") != "anomaly_summary":
        return payload

    anomalies = data.get("anomalies")
    if not isinstance(anomalies, list):
        return payload

    severity_counts = {"critical": 0, "warning": 0, "normal": 0}
    affected_machines = []
    for anomaly in anomalies:
        if not isinstance(anomaly, dict):
            continue
        severity = str(anomaly.get("severity") or "").lower()
        if severity in severity_counts:
            severity_counts[severity] += 1

        machine_name = anomaly.get("machine_name")
        if machine_name and machine_name not in affected_machines:
            affected_machines.append(machine_name)

    summary_metrics = insights.get("summary_metrics")
    if isinstance(summary_metrics, list):
        for metric in summary_metrics:
            if not isinstance(metric, dict):
                continue
            label = str(metric.get("label") or "").lower()
            if label == "total alerts":
                metric["value"] = len(anomalies)
                metric["tone"] = "danger" if anomalies else "good"
            elif label == "critical":
                metric["value"] = severity_counts["critical"]
            elif label == "warnings":
                metric["value"] = severity_counts["warning"]
            elif label == "machines":
                metric["value"] = len(affected_machines)

    payload["insights"] = insights
    return payload


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/query", response_model=VoiceQueryResponse)
async def voice_query(request: VoiceQueryRequest):
    """
    Send natural language query to OVOS voice assistant.
    
    This endpoint proxies text queries to the OVOS REST Bridge running on WSL2,
    which then forwards to OVOS messagebus for processing by the EnMS skill.
    
    **Audio Response:**
    When include_audio=true (default), returns base64-encoded WAV audio from OVOS TTS (Mimic3).
    Browser can play it with: `new Audio("data:audio/wav;base64," + audio_base64).play()`
    
    **Example queries:**
    - "What's the energy consumption for Compressor-1?"
    - "Give me a factory overview"
    - "How much did we spend on energy today?"
    - "Are there any anomalies?"
    - "What's the forecast for tomorrow?"
    
    **Configuration:**
    Set OVOS_BRIDGE_HOST environment variable to the Windows/WSL2 machine IP.
    """
    start_time = datetime.now()
    corrected_text = _normalize_partner_speech_text(request.text)
    normalized_text = _normalize_query(corrected_text)
    fallback_session_id = request.session_id or "auto"

    if _is_top_consumers_query(normalized_text):
        try:
            return await _build_top_consumers_fallback_response(fallback_session_id, start_time, normalized_text)
        except Exception as e:
            logger.error(f"Analytics top-consumers fallback failed: {e}")

    if _is_report_download_query(normalized_text):
        try:
            return await _build_report_download_response(fallback_session_id, start_time, normalized_text)
        except Exception as e:
            logger.error(f"Analytics report-download fallback failed: {e}", exc_info=True)

    if _is_enpi_query(normalized_text):
        try:
            return await _build_enpi_fallback_response(fallback_session_id, start_time)
        except Exception as e:
            logger.error(f"Analytics EnPI fallback failed: {e}")

    if _is_opportunity_query(normalized_text):
        try:
            return await _build_opportunities_fallback_response(fallback_session_id, start_time)
        except Exception as e:
            logger.error(f"Analytics opportunities fallback failed: {e}")
    
    # Use /query/voice endpoint for audio, /query for text-only
    endpoint = "/query/voice" if request.include_audio else "/query"
    
    try:
        async with httpx.AsyncClient(timeout=OVOS_BRIDGE_TIMEOUT) as client:
            response = await client.post(
                f"{OVOS_BRIDGE_URL}{endpoint}",
                json={
                    "text": corrected_text,
                    "session_id": request.session_id
                }
            )
            
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if response.status_code != 200:
                logger.error(f"OVOS Bridge returned {response.status_code}: {response.text}")
                return VoiceQueryResponse(
                    success=False,
                    response=None,
                    intent=None,
                    confidence=None,
                    data=None,
                    insights=None,
                    audio_base64=None,
                    error=f"OVOS Bridge error: {response.status_code}",
                    session_id=request.session_id or "none",
                    latency_ms=latency_ms,
                    tts_latency_ms=0,
                    timestamp=datetime.now().isoformat(),
                    bridge_url=OVOS_BRIDGE_URL
                )
            
            data = _repair_bridge_payload(response.json(), normalized_text)
            
            return VoiceQueryResponse(
                success=data.get("success", False),
                response=data.get("response"),
                intent=data.get("intent"),
                confidence=data.get("confidence"),
                data=data.get("data"),
                insights=data.get("insights"),
                audio_base64=data.get("audio_base64"),
                audio_format=data.get("audio_format", "wav"),
                pdf_base64=data.get("pdf_base64"),  # V1 legacy
                pdf_filename=data.get("pdf_filename"),  # V1 legacy
                pdf_download=data.get("pdf_download"),  # V2: Pass through PDF metadata object
                error=data.get("error"),
                session_id=data.get("session_id", request.session_id or "auto"),
                latency_ms=latency_ms,
                tts_latency_ms=data.get("tts_latency_ms", 0),
                timestamp=datetime.now().isoformat(),
                bridge_url=OVOS_BRIDGE_URL
            )
            
    except httpx.ConnectError as e:
        latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.error(f"Cannot connect to OVOS Bridge at {OVOS_BRIDGE_URL}: {e}")
        return VoiceQueryResponse(
            success=False,
            response=None,
            intent=None,
            confidence=None,
            data=None,
            insights=None,
            audio_base64=None,
            error=f"Cannot connect to OVOS Bridge at {OVOS_BRIDGE_URL}. Is it running?",
            session_id=request.session_id or "none",
            latency_ms=latency_ms,
            tts_latency_ms=0,
            timestamp=datetime.now().isoformat(),
            bridge_url=OVOS_BRIDGE_URL
        )
        
    except httpx.TimeoutException as e:
        latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.error(f"Timeout connecting to OVOS Bridge: {e}")
        return VoiceQueryResponse(
            success=False,
            response=None,
            intent=None,
            confidence=None,
            data=None,
            insights=None,
            audio_base64=None,
            error=f"Timeout after {OVOS_BRIDGE_TIMEOUT}s waiting for OVOS response",
            session_id=request.session_id or "none",
            latency_ms=latency_ms,
            tts_latency_ms=0,
            timestamp=datetime.now().isoformat(),
            bridge_url=OVOS_BRIDGE_URL
        )
        
    except Exception as e:
        latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.error(f"Error querying OVOS: {e}")
        return VoiceQueryResponse(
            success=False,
            response=None,
            intent=None,
            confidence=None,
            data=None,
            insights=None,
            audio_base64=None,
            error=str(e),
            session_id=request.session_id or "none",
            latency_ms=latency_ms,
            tts_latency_ms=0,
            timestamp=datetime.now().isoformat(),
            bridge_url=OVOS_BRIDGE_URL
        )


@router.get("/health", response_model=VoiceBridgeHealth)
async def voice_bridge_health():
    """
    Check connectivity to OVOS REST Bridge.
    
    Use this to verify the OVOS voice system is reachable before sending queries.
    
    **Returns:**
    - bridge_reachable: Can we connect to the REST bridge?
    - ovos_connected: Is the bridge connected to OVOS messagebus?
    - tts_available: Is TTS (Mimic3) available for audio responses?
    - tts_engine: Which TTS engine is configured (mimic3, piper, espeak)
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OVOS_BRIDGE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                # OVOS bridge returns 'messagebus_connected', map to 'ovos_connected'
                is_connected = data.get("messagebus_connected", data.get("ovos_connected", False))
                return VoiceBridgeHealth(
                    status="ok" if is_connected else "degraded",
                    bridge_reachable=True,
                    bridge_url=OVOS_BRIDGE_URL,
                    ovos_connected=is_connected,
                    tts_available=data.get("tts_available", False),
                    tts_engine=data.get("tts_engine"),
                    error=None
                )
            else:
                return VoiceBridgeHealth(
                    status="error",
                    bridge_reachable=True,
                    bridge_url=OVOS_BRIDGE_URL,
                    ovos_connected=False,
                    tts_available=False,
                    tts_engine=None,
                    error=f"Bridge returned status {response.status_code}"
                )
                
    except httpx.ConnectError:
        return VoiceBridgeHealth(
            status="unreachable",
            bridge_reachable=False,
            bridge_url=OVOS_BRIDGE_URL,
            ovos_connected=False,
            tts_available=False,
            tts_engine=None,
            error=f"Cannot connect to OVOS Bridge at {OVOS_BRIDGE_URL}"
        )
        
    except Exception as e:
        return VoiceBridgeHealth(
            status="error",
            bridge_reachable=False,
            bridge_url=OVOS_BRIDGE_URL,
            ovos_connected=False,
            tts_available=False,
            tts_engine=None,
            error=str(e)
        )


@router.get("/config")
async def voice_config():
    """
    Get current OVOS Bridge configuration.
    
    Shows the configured OVOS Bridge connection details.
    Useful for debugging connectivity issues.
    """
    return {
        "bridge_host": OVOS_BRIDGE_HOST,
        "bridge_port": OVOS_BRIDGE_PORT,
        "bridge_url": OVOS_BRIDGE_URL,
        "timeout_seconds": OVOS_BRIDGE_TIMEOUT,
        "env_vars": {
            "OVOS_BRIDGE_HOST": "Set this to change the bridge IP",
            "OVOS_BRIDGE_PORT": "Set this to change the bridge port (default: 5000)",
            "OVOS_BRIDGE_TIMEOUT": "Set this to change timeout (default: 20s)"
        }
    }
