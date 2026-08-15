"""Schema and Seed Data Registry for Synthetic Data Distillation.

This module defines:
- The 10 canonical JSON output schemas required by the offline desktop business assistant.
- 5 comprehensive, realistic few-shot seed examples for EACH schema (50 seeds total).
- Real-world business vertical context definitions (Retail, Pharmacy, Hospitality, Logistics, Tech Services, Finance).
"""

from enum import Enum
from typing import Any, Dict, List, Optional

SYSTEM_PROMPT = "You are a desktop business assistant. Respond using the appropriate structured JSON output schema."


class OutputSchemaType(str, Enum):
    GENERATIVE_CHART = "GENERATIVE_CHART"
    DOCUMENT_OUTPUT = "DOCUMENT_OUTPUT"
    CONVERSATIONAL_CHAT = "CONVERSATIONAL_CHAT"
    DEEP_RESEARCH = "DEEP_RESEARCH"
    SHIFT_SCHEDULE = "SHIFT_SCHEDULE"
    PRODUCTIVITY_CHART = "PRODUCTIVITY_CHART"
    RED_FLAG_ALERT = "RED_FLAG_ALERT"
    AUTO_TASK = "AUTO_TASK"
    TOOL_CALL = "TOOL_CALL"
    ACTION_CONFIRMATION = "ACTION_CONFIRMATION"


BUSINESS_VERTICALS = [
    "Documents",
    "POS",
    "Inventory",
    "Staff",
    "Finance",
    "Task Management",
]

DOMAIN_CONTEXTS = [
    {
        "domain": "Retail & Supermarket",
        "description": "Multi-category point-of-sale, barcode scanning, seasonal inventory, discount limits, cashier reconciliation.",
    },
    {
        "domain": "Pharmacy & Healthcare Clinic",
        "description": "Prescription logging, batch expiration tracking, controlled substance audits, licensed pharmacist shifts, compliance.",
    },
    {
        "domain": "Hospitality & Restaurant",
        "description": "Table management, peak rush hour staffing, ingredient waste logs, kitchen inventory, server tip payouts.",
    },
    {
        "domain": "Logistics & Warehousing",
        "description": "Pallet SKU auditing, dispatch schedules, forklift driver assignments, route fuel expenses, stock shrink tracking.",
    },
    {
        "domain": "Tech Services & IT Consulting",
        "description": "SLA incident resolution, billing milestone documents, software licensing cost breakdown, developer capacity planning.",
    },
    {
        "domain": "Financial & Accounting Practice",
        "description": "P&L variance reports, tax filing checklists, payroll authorization, invoice factoring, expense reconciliation.",
    },
]

# JSON Schemas for prompt guidance & reference
OUTPUT_SCHEMAS: Dict[str, Dict[str, Any]] = {
    OutputSchemaType.GENERATIVE_CHART.value: {
        "type": "object",
        "required": ["output_type", "chart_type", "title", "summary", "data"],
        "properties": {
            "output_type": {"type": "string", "enum": ["GENERATIVE_CHART"]},
            "chart_type": {"type": "string", "enum": ["bar", "line", "pie", "doughnut", "radar", "scatter", "area"]},
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "data": {
                "type": "object",
                "required": ["labels", "datasets"],
                "properties": {
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "datasets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["label", "values"],
                            "properties": {
                                "label": {"type": "string"},
                                "values": {"type": "array", "items": {"type": "number"}},
                            },
                        },
                    },
                },
            },
        },
    },
    OutputSchemaType.DOCUMENT_OUTPUT.value: {
        "type": "object",
        "required": ["output_type", "doc_title", "format", "content"],
        "properties": {
            "output_type": {"type": "string", "enum": ["DOCUMENT_OUTPUT"]},
            "doc_title": {"type": "string"},
            "format": {"type": "string", "enum": ["markdown", "plain_text", "html"]},
            "content": {"type": "string"},
        },
    },
    OutputSchemaType.CONVERSATIONAL_CHAT.value: {
        "type": "object",
        "required": ["output_type", "message"],
        "properties": {
            "output_type": {"type": "string", "enum": ["CONVERSATIONAL_CHAT"]},
            "message": {"type": "string"},
        },
    },
    OutputSchemaType.DEEP_RESEARCH.value: {
        "type": "object",
        "required": ["output_type", "target_sources", "search_queries", "sources", "response"],
        "properties": {
            "output_type": {"type": "string", "enum": ["DEEP_RESEARCH"]},
            "target_sources": {"type": "array", "items": {"type": "string"}},
            "search_queries": {"type": "array", "items": {"type": "string"}},
            "sources": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "type", "record_id", "relevance"],
                    "properties": {
                        "title": {"type": "string"},
                        "type": {"type": "string"},
                        "record_id": {"type": "string"},
                        "relevance": {"type": "string"},
                    },
                },
            },
            "response": {"type": "string"},
        },
    },
    OutputSchemaType.SHIFT_SCHEDULE.value: {
        "type": "object",
        "required": ["output_type", "week_starting", "schedule"],
        "properties": {
            "output_type": {"type": "string", "enum": ["SHIFT_SCHEDULE"]},
            "week_starting": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
            "schedule": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["staff_id", "name", "role", "day", "shift"],
                    "properties": {
                        "staff_id": {"type": "string"},
                        "name": {"type": "string"},
                        "role": {"type": "string"},
                        "day": {"type": "string"},
                        "shift": {"type": "string"},
                    },
                },
            },
        },
    },
    OutputSchemaType.PRODUCTIVITY_CHART.value: {
        "type": "object",
        "required": ["output_type", "employee_name", "period", "chart_type", "data", "summary"],
        "properties": {
            "output_type": {"type": "string", "enum": ["PRODUCTIVITY_CHART"]},
            "employee_name": {"type": "string"},
            "period": {"type": "string"},
            "chart_type": {"type": "string", "enum": ["bar", "line", "pie", "radar", "area"]},
            "data": {
                "type": "object",
                "required": ["labels", "datasets"],
                "properties": {
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "datasets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["label", "values"],
                            "properties": {
                                "label": {"type": "string"},
                                "values": {"type": "array", "items": {"type": "number"}},
                            },
                        },
                    },
                },
            },
            "summary": {"type": "string"},
        },
    },
    OutputSchemaType.RED_FLAG_ALERT.value: {
        "type": "object",
        "required": ["output_type", "severity", "flagged_module", "anomaly_type", "reasoning", "recommended_action"],
        "properties": {
            "output_type": {"type": "string", "enum": ["RED_FLAG_ALERT"]},
            "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
            "flagged_module": {"type": "string"},
            "anomaly_type": {"type": "string"},
            "transaction_id": {"type": "string"},
            "reasoning": {"type": "string"},
            "recommended_action": {"type": "string"},
        },
    },
    OutputSchemaType.AUTO_TASK.value: {
        "type": "object",
        "required": ["output_type", "task_title", "priority", "assignee_role", "due_date", "subtasks"],
        "properties": {
            "output_type": {"type": "string", "enum": ["AUTO_TASK"]},
            "task_title": {"type": "string"},
            "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
            "assignee_role": {"type": "string"},
            "due_date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
            "subtasks": {"type": "array", "items": {"type": "string"}},
        },
    },
    OutputSchemaType.TOOL_CALL.value: {
        "type": "object",
        "required": ["output_type", "module", "endpoint", "parameters"],
        "properties": {
            "output_type": {"type": "string", "enum": ["TOOL_CALL"]},
            "module": {"type": "string"},
            "endpoint": {"type": "string"},
            "parameters": {"type": "object"},
        },
    },
    OutputSchemaType.ACTION_CONFIRMATION.value: {
        "type": "object",
        "required": ["output_type", "action_name", "target_module", "impact_summary", "requires_auth"],
        "properties": {
            "output_type": {"type": "string", "enum": ["ACTION_CONFIRMATION"]},
            "action_name": {"type": "string"},
            "target_module": {"type": "string"},
            "impact_summary": {"type": "string"},
            "requires_auth": {"type": "boolean"},
        },
    },
}

# 5 High-Quality Seed Examples for EACH of the 10 schemas (50 Total Seeds)
SEED_EXAMPLES: Dict[str, List[Dict[str, Any]]] = {
    OutputSchemaType.GENERATIVE_CHART.value: [
        {
            "domain": "Retail",
            "user_query": "Show me the revenue vs expense chart for Q1 across all store locations.",
            "response": {
                "output_type": "GENERATIVE_CHART",
                "chart_type": "bar",
                "title": "Q1 Financial Breakdown: Revenue vs Expenses",
                "summary": "Total Q1 revenue reached $415,000 against operating expenses of $295,000, delivering an average net margin of 28.9%.",
                "data": {
                    "labels": ["January", "February", "March"],
                    "datasets": [
                        {"label": "Revenue ($)", "values": [128000, 139000, 148000]},
                        {"label": "Expenses ($)", "values": [96000, 98000, 101000]},
                    ],
                },
            },
        },
        {
            "domain": "Pharmacy",
            "user_query": "Plot our prescription sales volume trend by category over the last four months.",
            "response": {
                "output_type": "GENERATIVE_CHART",
                "chart_type": "line",
                "title": "Prescription Dispensing Volume by Category",
                "summary": "Cardiovascular and antibiotic prescriptions saw a 14% uptick heading into late winter, while OTC sales stabilized.",
                "data": {
                    "labels": ["Nov", "Dec", "Jan", "Feb"],
                    "datasets": [
                        {"label": "Cardiovascular", "values": [1420, 1510, 1680, 1720]},
                        {"label": "Antibiotics", "values": [890, 1140, 1290, 1210]},
                        {"label": "OTC Wellness", "values": [2100, 2450, 2300, 2180]},
                    ],
                },
            },
        },
        {
            "domain": "Hospitality",
            "user_query": "Compare drink vs food revenue across weekday dinner shifts.",
            "response": {
                "output_type": "GENERATIVE_CHART",
                "chart_type": "bar",
                "title": "Dinner Service Revenue Mix (Tue - Sun)",
                "summary": "Friday and Saturday evenings generated 58% of total weekly beverage sales, driven by cocktail specials.",
                "data": {
                    "labels": ["Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    "datasets": [
                        {"label": "Food Sales ($)", "values": [3400, 4100, 5200, 8900, 10400, 6300]},
                        {"label": "Beverage Sales ($)", "values": [1600, 2200, 3100, 6800, 8200, 3900]},
                    ],
                },
            },
        },
        {
            "domain": "Logistics",
            "user_query": "Can you display our fleet delivery on-time performance percentage for H1?",
            "response": {
                "output_type": "GENERATIVE_CHART",
                "chart_type": "line",
                "title": "H1 Fleet On-Time Delivery Rate (%)",
                "summary": "On-time delivery rebounded to 96.4% in June following route optimization and depot automation upgrades in April.",
                "data": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "datasets": [
                        {"label": "On-Time Rate (%)", "values": [91.2, 89.8, 92.5, 94.1, 95.8, 96.4]},
                        {"label": "SLA Benchmark (%)", "values": [95.0, 95.0, 95.0, 95.0, 95.0, 95.0]},
                    ],
                },
            },
        },
        {
            "domain": "Tech Services",
            "user_query": "Give me a breakdown of support tickets by severity level for July.",
            "response": {
                "output_type": "GENERATIVE_CHART",
                "chart_type": "pie",
                "title": "July Support Ticket Severity Distribution",
                "summary": "Low and Medium tickets formed 83% of the 540 total client inquiries, with Critical outages limited to 4 incidents.",
                "data": {
                    "labels": ["Critical", "High", "Medium", "Low"],
                    "datasets": [
                        {"label": "Ticket Count", "values": [4, 88, 210, 238]},
                    ],
                },
            },
        },
    ],
    OutputSchemaType.DOCUMENT_OUTPUT.value: [
        {
            "domain": "Inventory",
            "user_query": "Generate the Q3 warehouse inventory audit summary report.",
            "response": {
                "output_type": "DOCUMENT_OUTPUT",
                "doc_title": "Q3 Warehouse Inventory Audit Summary",
                "format": "markdown",
                "content": "# Q3 Warehouse Inventory Audit\n**Facility:** Central Fulfillment Depot #4\n**Auditor:** Lead Logistics Specialist\n**Date:** September 30, 2026\n\n## Executive Summary\nInventory shrinkage decreased by 3.8% quarter-over-quarter. Total reconciled stock value stands at **$1,420,500** across 18,400 SKUs.\n\n## Key Findings\n- **Fast-Moving SKUs:** High turnover in consumer electronics created 2 stockout events.\n- **Discrepancies:** 14 units of SKU-9042 unaccounted for during cycle count in Aisle 7.\n\n## Action Items\n1. Recalibrate barcode scanners at Receiving Dock B.\n2. Reorder buffer stock for top 20 velocity items.",
            },
        },
        {
            "domain": "Staff",
            "user_query": "Draft a formal warning letter regarding repeated unexcused tardiness for staff file.",
            "response": {
                "output_type": "DOCUMENT_OUTPUT",
                "doc_title": "Written Disciplinary Notice: Attendance Policy",
                "format": "markdown",
                "content": "# Notice of Corrective Action\n**Employee Name:** Employee #4091\n**Department:** Front of House\n**Supervisor:** Operations Manager\n**Date:** August 15, 2026\n\n## Reason for Notice\nThis document records formal notice regarding unexcused tardiness on August 3, August 8, and August 12, exceeding allowable company tolerances.\n\n## Required Improvement\n- Punctual arrival at assigned workstation at shift start time.\n- Immediate notification to shift manager at least 2 hours prior in emergency situations.\n\nFailure to maintain attendance standards may result in further disciplinary action up to termination.",
            },
        },
        {
            "domain": "Finance",
            "user_query": "Prepare the monthly executive P&L statement overview for the board.",
            "response": {
                "output_type": "DOCUMENT_OUTPUT",
                "doc_title": "Monthly P&L Executive Review - July 2026",
                "format": "markdown",
                "content": "# Executive P&L Overview: July 2026\n\n## 1. Financial Performance Highlights\n- **Gross Revenue:** $342,800 (+8.2% vs budget)\n- **Cost of Goods Sold (COGS):** $154,260 (45.0% of revenue)\n- **Operating Expenses:** $112,400\n- **EBITDA:** $76,140 (22.2% margin)\n\n## 2. Variance Analysis\nMarketing expenditure came in $4,500 under forecast due to delayed Q3 campaign rollout, while logistics freight rates increased 2.1%.\n\n## 3. Cash Position\nEnding cash balance stands at $512,000 with 4.8 months of operational runway.",
            },
        },
        {
            "domain": "Pharmacy",
            "user_query": "Create the Standard Operating Procedure document for handling cold-chain vaccine storage.",
            "response": {
                "output_type": "DOCUMENT_OUTPUT",
                "doc_title": "SOP-PHARM-082: Cold-Chain Storage & Temperature Logging",
                "format": "markdown",
                "content": "# SOP: Cold-Chain Pharmaceutical Storage\n**Protocol ID:** SOP-PHARM-082\n**Effective Date:** 2026-08-01\n**Target Roles:** Staff Pharmacists, Pharmacy Technicians\n\n## 1. Temperature Standards\n- Refrigerated vaccines: Maintain strictly between **2.0°C and 8.0°C**.\n- Digital data loggers must record temperatures at 15-minute intervals.\n\n## 2. Daily Verification Protocol\n1. Inspect digital gauge at 08:00 and 18:00 daily.\n2. Log manual readings in the central compliance terminal.\n3. In event of excursion (>8.5°C for >30 mins), quarantine batch and notify QA.",
            },
        },
        {
            "domain": "Tech Services",
            "user_query": "Export the Post-Mortem Incident Report for yesterday's database connection pool exhaustion.",
            "response": {
                "output_type": "DOCUMENT_OUTPUT",
                "doc_title": "Incident Post-Mortem: DB Connection Pool Starvation",
                "format": "markdown",
                "content": "# Incident Post-Mortem: INC-8821\n**Service Impacted:** Core Transaction Processing API\n**Downtime Duration:** 14 minutes (14:22 - 14:36 UTC)\n**Lead Engineer:** Staff Site Reliability Engineer\n\n## Root Cause\nAn unindexed analytics query executed by the automated batch report worker locked 40 active connections, exhausting the maximum pool limit of 50.\n\n## Resolution\n- Connection pool size increased to 120 with strict 5-second query timeouts.\n- Analytics worker routed to read-only replica.\n\n## Preventative Actions\n- Add automated query cost linter to deployment pipeline.",
            },
        },
    ],
    OutputSchemaType.CONVERSATIONAL_CHAT.value: [
        {
            "domain": "General Business",
            "user_query": "Hey, what business modules can you help me manage today?",
            "response": {
                "output_type": "CONVERSATIONAL_CHAT",
                "message": "I can assist you across all 6 core business modules: Documents, Point of Sale (POS), Inventory, Staff Rostering, Financial Reports, and Task Management. Let me know if you want to inspect register anomalies, generate a sales chart, or adjust this week's shift schedule.",
            },
        },
        {
            "domain": "POS & Retail",
            "user_query": "Why did register 3 close out with a cash variance yesterday?",
            "response": {
                "output_type": "CONVERSATIONAL_CHAT",
                "message": "Register 3 recorded a -$45.20 cash discrepancy at the 21:00 drawer closeout. Would you like me to pull the transaction log for Cashier Shift #14 or flag this for manager review in the task board?",
            },
        },
        {
            "domain": "Inventory",
            "user_query": "Do we have enough organic coffee beans in stock for the weekend brunch rush?",
            "response": {
                "output_type": "CONVERSATIONAL_CHAT",
                "message": "Currently, you have 18.5 kg of organic espresso blend on hand. Based on average weekend consumption of 24 kg, you are projected to run short by Sunday morning. Would you like me to trigger an expedited supplier purchase order?",
            },
        },
        {
            "domain": "Staff",
            "user_query": "Who is currently on duty as the lead shift supervisor?",
            "response": {
                "output_type": "CONVERSATIONAL_CHAT",
                "message": "Marcus Vance is clocked in as Shift Supervisor until 17:30, after which Elena Rostova takes over the evening shift from 17:00 to 23:30.",
            },
        },
        {
            "domain": "Finance",
            "user_query": "Can you explain what caused the spike in utility expenses last month?",
            "response": {
                "output_type": "CONVERSATIONAL_CHAT",
                "message": "The 24% increase in July utilities was primarily driven by HVAC peak-rate electrical charges during the consecutive heatwave weeks, combined with an annual water backflow testing fee of $380.",
            },
        },
    ],
    OutputSchemaType.DEEP_RESEARCH.value: [
        {
            "domain": "Retail & Finance",
            "user_query": "Investigate the Q3 tax compliance rules for digital point-of-sale surcharges and our internal variance history.",
            "response": {
                "output_type": "DEEP_RESEARCH",
                "target_sources": ["LOCAL_DB", "WEB_SEARCH"],
                "search_queries": [
                    "2026 digital payment surcharge compliance regulations",
                    "POS credit card fee pass-through state limits",
                    "Internal tax audit variance Q1-Q2 2026",
                ],
                "sources": [
                    {
                        "title": "State Department of Revenue Bulletin 2026-04",
                        "type": "WEB_SEARCH",
                        "record_id": "https://tax.state.gov/bulletin-2026-04",
                        "relevance": "High",
                    },
                    {
                        "title": "2026 Internal Merchant Fee Reconciliation Report",
                        "type": "LOCAL_DB",
                        "record_id": "FIN-REC-2026-088",
                        "relevance": "High",
                    },
                ],
                "response": "Under updated 2026 regulations, credit card surcharge pass-throughs must not exceed actual merchant processing fees (capped at 3.0%) and must be itemized before payment authorization. Internal records show our current POS configuration charges a flat 2.5%, remaining fully compliant.",
            },
        },
        {
            "domain": "Pharmacy",
            "user_query": "Check regulatory expiry guidelines for schedule II compounds and cross-reference our batch inventory.",
            "response": {
                "output_type": "DEEP_RESEARCH",
                "target_sources": ["LOCAL_DB", "REGULATORY_DOCS"],
                "search_queries": [
                    "DEA controlled substance disposal retention guidelines 2026",
                    "Schedule II compounding shelf life limits",
                    "Pharmacy vault stock batch expiries Q3 2026",
                ],
                "sources": [
                    {
                        "title": "DEA Pharmacist Manual Section VII - Destruction",
                        "type": "REGULATORY_DOCS",
                        "record_id": "DEA-MAN-SEC-07",
                        "relevance": "High",
                    },
                    {
                        "title": "Vault Controlled Substance Ledger",
                        "type": "LOCAL_DB",
                        "record_id": "PHARM-VAULT-2026-07",
                        "relevance": "Critical",
                    },
                ],
                "response": "Regulations require reverse distributor transfer for schedule II substances reaching within 30 days of expiry. Ledger check identifies two lots (Lot #C2-991 and Lot #C2-994) expiring on September 15. Form DEA-41 transfer documentation should be generated immediately.",
            },
        },
        {
            "domain": "Hospitality",
            "user_query": "Research local municipal food safety sanitation code updates regarding sous-vide holding times.",
            "response": {
                "output_type": "DEEP_RESEARCH",
                "target_sources": ["LOCAL_DB", "WEB_SEARCH"],
                "search_queries": [
                    "Municipal Food Code 2026 Reduced Oxygen Packaging sous-vide",
                    "Health Department HACCP temperature compliance logs",
                ],
                "sources": [
                    {
                        "title": "City Public Health Food Code Section 3-502.12",
                        "type": "WEB_SEARCH",
                        "record_id": "https://health.city.gov/foodcode/3-502",
                        "relevance": "High",
                    },
                    {
                        "title": "Kitchen HACCP Plan & Variance Approval",
                        "type": "LOCAL_DB",
                        "record_id": "HACCP-DOC-2025-V2",
                        "relevance": "High",
                    },
                ],
                "response": "The updated food safety code requires continuous water bath temperature recording for sous-vide proteins held over 4 hours at under 57°C (135°F). Our active HACCP variance covers current 54.5°C cook-chill cycles, but calibration logs must be timestamped digitally every 2 hours.",
            },
        },
        {
            "domain": "Logistics",
            "user_query": "Analyze regional diesel fuel surcharge index trends and match against our freight carrier contracts.",
            "response": {
                "output_type": "DEEP_RESEARCH",
                "target_sources": ["LOCAL_DB", "WEB_SEARCH"],
                "search_queries": [
                    "EIA Weekly On-Highway Diesel Fuel Price Index 2026",
                    "Freight Master Services Agreement fuel peg clauses",
                ],
                "sources": [
                    {
                        "title": "U.S. EIA National Diesel Price Index",
                        "type": "WEB_SEARCH",
                        "record_id": "https://eia.gov/petroleum/gasdiesel/",
                        "relevance": "High",
                    },
                    {
                        "title": "Carrier Contract - Apex Freight Lines MSA",
                        "type": "LOCAL_DB",
                        "record_id": "CONTRACT-LOG-2025-019",
                        "relevance": "High",
                    },
                ],
                "response": "The national diesel benchmark dipped to $3.82/gal this week. Under Clause 8.2 of the Apex Freight agreement, fuel surcharges adjust down from 14.5% to 12.0% starting next Monday, reducing estimated freight spend by ~$2,800 for August.",
            },
        },
        {
            "domain": "Tech Services",
            "user_query": "Investigate SLA downtime penalty clauses in our tier-1 enterprise client agreements.",
            "response": {
                "output_type": "DEEP_RESEARCH",
                "target_sources": ["LOCAL_DB"],
                "search_queries": [
                    "Enterprise Master Services Agreement SLA credit table",
                    "Quarterly uptime log Q2-Q3 2026",
                ],
                "sources": [
                    {
                        "title": "Enterprise Client MSA - CloudServices Tier 1",
                        "type": "LOCAL_DB",
                        "record_id": "MSA-ENT-2024-003",
                        "relevance": "High",
                    },
                    {
                        "title": "System Uptime & Incident Log Q2 2026",
                        "type": "LOCAL_DB",
                        "record_id": "OPS-SLA-2026-Q2",
                        "relevance": "Medium",
                    },
                ],
                "response": "Tier-1 agreements stipulate a 99.9% uptime SLA. Monthly availability between 99.0% and 99.89% triggers a 10% invoice credit upon client request within 30 days. Our July uptime was 99.94%, so no SLA penalties were triggered.",
            },
        },
    ],
    OutputSchemaType.SHIFT_SCHEDULE.value: [
        {
            "domain": "Retail",
            "user_query": "Generate next week's cashier and floor team shift roster starting August 17.",
            "response": {
                "output_type": "SHIFT_SCHEDULE",
                "week_starting": "2026-08-17",
                "schedule": [
                    {"staff_id": "EMP_101", "name": "Sarah Jenkins", "role": "Head Cashier", "day": "Monday", "shift": "08:00 - 16:30"},
                    {"staff_id": "EMP_104", "name": "David Kim", "role": "Floor Associate", "day": "Monday", "shift": "10:00 - 18:30"},
                    {"staff_id": "EMP_108", "name": "Alicia Rivera", "role": "Inventory Clerk", "day": "Tuesday", "shift": "07:00 - 15:30"},
                    {"staff_id": "EMP_101", "name": "Sarah Jenkins", "role": "Head Cashier", "day": "Wednesday", "shift": "08:00 - 16:30"},
                    {"staff_id": "EMP_112", "name": "Jason Thorne", "role": "Store Supervisor", "day": "Friday", "shift": "12:00 - 20:30"},
                ],
            },
        },
        {
            "domain": "Hospitality",
            "user_query": "Build the kitchen brigade and dining room roster for the week of 2026-08-24.",
            "response": {
                "output_type": "SHIFT_SCHEDULE",
                "week_starting": "2026-08-24",
                "schedule": [
                    {"staff_id": "KIT_01", "name": "Chef Antonio Rossi", "role": "Head Chef", "day": "Wednesday", "shift": "14:00 - 23:00"},
                    {"staff_id": "KIT_04", "name": "Maya Lin", "role": "Sous Chef", "day": "Wednesday", "shift": "10:00 - 19:00"},
                    {"staff_id": "FOH_08", "name": "Liam Connor", "role": "Lead Bartender", "day": "Friday", "shift": "16:00 - 01:00"},
                    {"staff_id": "FOH_12", "name": "Chloe Bennett", "role": "Server", "day": "Friday", "shift": "17:00 - 23:30"},
                    {"staff_id": "KIT_01", "name": "Chef Antonio Rossi", "role": "Head Chef", "day": "Saturday", "shift": "12:00 - 23:00"},
                ],
            },
        },
        {
            "domain": "Pharmacy",
            "user_query": "Set up the licensed pharmacist coverage schedule for week starting 2026-09-07.",
            "response": {
                "output_type": "SHIFT_SCHEDULE",
                "week_starting": "2026-09-07",
                "schedule": [
                    {"staff_id": "PHARM_01", "name": "Dr. Rebecca Patel", "role": "Pharmacist-in-Charge", "day": "Monday", "shift": "08:00 - 16:00"},
                    {"staff_id": "PHARM_03", "name": "Dr. Tyler Hayes", "role": "Staff Pharmacist", "day": "Monday", "shift": "14:00 - 22:00"},
                    {"staff_id": "TECH_02", "name": "Brianna Scott", "role": "Certified Pharmacy Tech", "day": "Tuesday", "shift": "09:00 - 17:30"},
                    {"staff_id": "PHARM_01", "name": "Dr. Rebecca Patel", "role": "Pharmacist-in-Charge", "day": "Wednesday", "shift": "08:00 - 16:00"},
                    {"staff_id": "PHARM_03", "name": "Dr. Tyler Hayes", "role": "Staff Pharmacist", "day": "Saturday", "shift": "09:00 - 18:00"},
                ],
            },
        },
        {
            "domain": "Logistics",
            "user_query": "Create the warehouse dispatch and forklift operator shifts for week of August 31, 2026.",
            "response": {
                "output_type": "SHIFT_SCHEDULE",
                "week_starting": "2026-08-31",
                "schedule": [
                    {"staff_id": "LOG_21", "name": "Hector Ramirez", "role": "Lead Dispatcher", "day": "Monday", "shift": "05:00 - 13:30"},
                    {"staff_id": "LOG_33", "name": "Samira Khan", "role": "Forklift Operator", "day": "Monday", "shift": "06:00 - 14:30"},
                    {"staff_id": "LOG_44", "name": "Owen Murphy", "role": "Receiving Specialist", "day": "Tuesday", "shift": "08:00 - 16:30"},
                    {"staff_id": "LOG_33", "name": "Samira Khan", "role": "Forklift Operator", "day": "Thursday", "shift": "06:00 - 14:30"},
                    {"staff_id": "LOG_21", "name": "Hector Ramirez", "role": "Lead Dispatcher", "day": "Friday", "shift": "05:00 - 13:30"},
                ],
            },
        },
        {
            "domain": "Tech Services",
            "user_query": "Schedule on-call tier-2 customer support rotation for week starting 2026-09-14.",
            "response": {
                "output_type": "SHIFT_SCHEDULE",
                "week_starting": "2026-09-14",
                "schedule": [
                    {"staff_id": "ENG_09", "name": "Nate Robinson", "role": "Tier 2 Support Engineer", "day": "Monday", "shift": "00:00 - 23:59 (Primary On-Call)"},
                    {"staff_id": "ENG_14", "name": "Amina Al-Mansoor", "role": "Systems Specialist", "day": "Wednesday", "shift": "00:00 - 23:59 (Primary On-Call)"},
                    {"staff_id": "ENG_05", "name": "Chris Taylor", "role": "DevOps Engineer", "day": "Friday", "shift": "18:00 - 06:00 (Weekend Primary)"},
                    {"staff_id": "ENG_09", "name": "Nate Robinson", "role": "Tier 2 Support Engineer", "day": "Saturday", "shift": "06:00 - 18:00 (Weekend Secondary)"},
                    {"staff_id": "ENG_14", "name": "Amina Al-Mansoor", "role": "Systems Specialist", "day": "Sunday", "shift": "18:00 - 06:00 (Shift Handover)"},
                ],
            },
        },
    ],
    OutputSchemaType.PRODUCTIVITY_CHART.value: [
        {
            "domain": "Staff & Retail",
            "user_query": "Show productivity metrics and transaction scan speeds for cashier Michael Chen in Q2.",
            "response": {
                "output_type": "PRODUCTIVITY_CHART",
                "employee_name": "Michael Chen",
                "period": "Q2 2026",
                "chart_type": "line",
                "data": {
                    "labels": ["April", "May", "June"],
                    "datasets": [
                        {"label": "Items Scanned / Min", "values": [18.4, 21.2, 23.8]},
                        {"label": "Transactions Processed", "values": [1240, 1380, 1490]},
                    ],
                },
                "summary": "Michael improved scanning speed by 29.3% across Q2 while maintaining zero cash drawer variances.",
            },
        },
        {
            "domain": "Tech Services",
            "user_query": "Display quarterly sprint velocity and bug resolution stats for developer Priya Sharma.",
            "response": {
                "output_type": "PRODUCTIVITY_CHART",
                "employee_name": "Priya Sharma",
                "period": "Q1 - Q2 2026",
                "chart_type": "bar",
                "data": {
                    "labels": ["Sprint 14", "Sprint 15", "Sprint 16", "Sprint 17"],
                    "datasets": [
                        {"label": "Story Points Completed", "values": [34, 42, 38, 45]},
                        {"label": "Bugs Closed", "values": [8, 12, 11, 15]},
                    ],
                },
                "summary": "Priya maintained an average sprint velocity of 39.8 story points with an 88% PR approval rate on first review.",
            },
        },
        {
            "domain": "Logistics",
            "user_query": "Chart order picking velocity for warehouse associate Jamal Wright over the last 3 months.",
            "response": {
                "output_type": "PRODUCTIVITY_CHART",
                "employee_name": "Jamal Wright",
                "period": "May - July 2026",
                "chart_type": "line",
                "data": {
                    "labels": ["May", "June", "July"],
                    "datasets": [
                        {"label": "Picks Per Hour", "values": [92, 108, 119]},
                        {"label": "Accuracy Rate (%)", "values": [99.1, 99.4, 99.8]},
                    ],
                },
                "summary": "Jamal exceeded facility picking targets by 19% with near-flawless pick accuracy (99.8% in July).",
            },
        },
        {
            "domain": "Hospitality",
            "user_query": "Show table turnover rate and guest satisfaction score for server Chloe Bennett.",
            "response": {
                "output_type": "PRODUCTIVITY_CHART",
                "employee_name": "Chloe Bennett",
                "period": "Summer 2026",
                "chart_type": "bar",
                "data": {
                    "labels": ["June", "July", "August"],
                    "datasets": [
                        {"label": "Average Tip (%)", "values": [20.4, 21.8, 22.5]},
                        {"label": "Guest Satisfaction Score", "values": [4.7, 4.8, 4.9]},
                    ],
                },
                "summary": "Chloe achieved top-ranked guest satisfaction ratings for three consecutive months with average tip percentages exceeding 22%.",
            },
        },
        {
            "domain": "Pharmacy",
            "user_query": "View prescription fill throughput and verification speed for technician Brianna Scott.",
            "response": {
                "output_type": "PRODUCTIVITY_CHART",
                "employee_name": "Brianna Scott",
                "period": "Q2 2026",
                "chart_type": "line",
                "data": {
                    "labels": ["April", "May", "June"],
                    "datasets": [
                        {"label": "Prescriptions Filled / Day", "values": [145, 162, 178]},
                        {"label": "Verification Accuracy (%)", "values": [99.8, 99.9, 100.0]},
                    ],
                },
                "summary": "Brianna processed 178 fills per day in June with 100% verification accuracy on pre-check audit logs.",
            },
        },
    ],
    OutputSchemaType.RED_FLAG_ALERT.value: [
        {
            "domain": "POS & Retail",
            "user_query": "Alert the manager if any unusual manual discount exceeds security thresholds on register 2.",
            "response": {
                "output_type": "RED_FLAG_ALERT",
                "severity": "HIGH",
                "flagged_module": "POS",
                "anomaly_type": "UNUSUALLY_HIGH_DISCOUNT",
                "transaction_id": "TXN_98421",
                "reasoning": "A 90% manual markdown ($450 value) was applied on item SKU-8812 without manager override credentials.",
                "recommended_action": "Review register surveillance video and interview Cashier #104 regarding TXN_98421.",
            },
        },
        {
            "domain": "Inventory",
            "user_query": "Flag any sudden bulk inventory depletion detected during after-hours.",
            "response": {
                "output_type": "RED_FLAG_ALERT",
                "severity": "CRITICAL",
                "flagged_module": "Inventory",
                "anomaly_type": "AFTER_HOURS_STOCK_DEPLETION",
                "transaction_id": "INV_ADJ_7720",
                "reasoning": "50 units of high-value graphics cards were written off as damaged at 02:45 AM outside scheduled warehouse operating hours.",
                "recommended_action": "Lock inventory access logs, preserve security footage from Bay 4, and alert the Warehouse Director.",
            },
        },
        {
            "domain": "Finance",
            "user_query": "Scan vendor payables for duplicate invoice submissions.",
            "response": {
                "output_type": "RED_FLAG_ALERT",
                "severity": "HIGH",
                "flagged_module": "Finance",
                "anomaly_type": "DUPLICATE_INVOICE_SUBMISSION",
                "transaction_id": "INV-PAY-55104",
                "reasoning": "Invoice #8992 for $12,400 from Vendor 'Global Logistics LLC' shares the exact purchase order and amount as paid invoice #8921.",
                "recommended_action": "Halt payment release and request original bill of lading verification from Accounts Payable.",
            },
        },
        {
            "domain": "Pharmacy",
            "user_query": "Check if any controlled substance count discrepancies exceed daily tolerance limits.",
            "response": {
                "output_type": "RED_FLAG_ALERT",
                "severity": "CRITICAL",
                "flagged_module": "Pharmacy",
                "anomaly_type": "CONTROLLED_SUBSTANCE_DISCREPANCY",
                "transaction_id": "VAULT_AUDIT_303",
                "reasoning": "Perpetual inventory indicates 200 tablets of Oxycodone 10mg, but physical vault count showed 170 tablets (discrepancy of -30 units).",
                "recommended_action": "Immediately notify Pharmacist-in-Charge, initiate mandatory count reconciliation, and log DEA reportable discrepancy.",
            },
        },
        {
            "domain": "Staff & Access",
            "user_query": "Detect any unauthorized badge swipes or clock-ins outside assigned shift schedules.",
            "response": {
                "output_type": "RED_FLAG_ALERT",
                "severity": "MEDIUM",
                "flagged_module": "Staff",
                "anomaly_type": "UNSCHEDULED_OVERTIME_CLOCK_IN",
                "transaction_id": "TIME_PUNCH_4412",
                "reasoning": "Staff member EMP_210 clocked in 4 hours prior to scheduled shift start without prior manager authorization.",
                "recommended_action": "Confirm shift swap authorization with Department Lead and correct timesheet if unapproved.",
            },
        },
    ],
    OutputSchemaType.AUTO_TASK.value: [
        {
            "domain": "Inventory",
            "user_query": "We need to do a full recount of dairy products in cold storage before tomorrow's delivery.",
            "response": {
                "output_type": "AUTO_TASK",
                "task_title": "Count Cold Storage Dairy Inventory",
                "priority": "HIGH",
                "assignee_role": "Inventory Clerk",
                "due_date": "2026-08-16",
                "subtasks": [
                    "Perform cycle count of milk crates and yogurt pallets in Walk-in Cooler A",
                    "Check expiration dates on Greek yogurt stock",
                    "Enter final count in inventory terminal",
                ],
            },
        },
        {
            "domain": "POS & Maintenance",
            "user_query": "Register 4 receipt printer is jamming frequently and needs thermal head cleaning.",
            "response": {
                "output_type": "AUTO_TASK",
                "task_title": "Service POS Register 4 Hardware",
                "priority": "MEDIUM",
                "assignee_role": "Store Technician",
                "due_date": "2026-08-17",
                "subtasks": [
                    "Clean thermal printhead and paper feed rollers with isopropyl alcohol",
                    "Run self-test diagnostic print cycle",
                    "Verify cable connections to cash drawer kick-port",
                ],
            },
        },
        {
            "domain": "Finance",
            "user_query": "Prepare all Q2 sales tax filing documentation before the end of the week.",
            "response": {
                "output_type": "AUTO_TASK",
                "task_title": "Finalize Q2 Sales Tax Submission",
                "priority": "URGENT",
                "assignee_role": "Staff Accountant",
                "due_date": "2026-08-21",
                "subtasks": [
                    "Export taxable vs non-taxable sales summary from POS database",
                    "Reconcile collected state and local sales tax with ledger account 2200",
                    "Submit filing through state revenue electronic portal",
                ],
            },
        },
        {
            "domain": "Staff & Onboarding",
            "user_query": "Create the onboarding setup checklist for the new Assistant Manager starting Monday.",
            "response": {
                "output_type": "AUTO_TASK",
                "task_title": "New Hire Onboarding: Assistant Manager",
                "priority": "HIGH",
                "assignee_role": "HR Specialist",
                "due_date": "2026-08-17",
                "subtasks": [
                    "Provision POS supervisor PIN and override key card",
                    "Configure corporate email and payroll portal access",
                    "Assign store security alarm access code",
                ],
            },
        },
        {
            "domain": "Hospitality",
            "user_query": "Schedule deep cleaning of the commercial grease trap and exhaust hood.",
            "response": {
                "output_type": "AUTO_TASK",
                "task_title": "Kitchen Exhaust Hood & Grease Trap Sanitation",
                "priority": "MEDIUM",
                "assignee_role": "Kitchen Lead",
                "due_date": "2026-08-23",
                "subtasks": [
                    "Coordinate Sunday night maintenance window with certified vendor",
                    "Power down kitchen pilot lights and cover stainless surfaces",
                    "Inspect post-cleaning compliance certificate for fire safety file",
                ],
            },
        },
    ],
    OutputSchemaType.TOOL_CALL.value: [
        {
            "domain": "Finance",
            "user_query": "Fetch the profit and loss statement for Q2 2026.",
            "response": {
                "output_type": "TOOL_CALL",
                "module": "Finance",
                "endpoint": "get_pnl_statement",
                "parameters": {"quarter": "Q2", "year": 2026, "include_tax_provision": True},
            },
        },
        {
            "domain": "POS",
            "user_query": "Pull the daily register drawer reconciliation for Station #2.",
            "response": {
                "output_type": "TOOL_CALL",
                "module": "POS",
                "endpoint": "get_register_reconciliation",
                "parameters": {"register_id": 2, "date": "2026-08-14", "shift": "EVENING"},
            },
        },
        {
            "domain": "Inventory",
            "user_query": "Check current warehouse stock level for SKU #44891.",
            "response": {
                "output_type": "TOOL_CALL",
                "module": "Inventory",
                "endpoint": "query_stock_level",
                "parameters": {"sku": "SKU-44891", "warehouse_id": "MAIN_DEPOT", "include_safety_stock": True},
            },
        },
        {
            "domain": "Staff",
            "user_query": "Retrieve overtime hours worked by all logistics staff in the past 14 days.",
            "response": {
                "output_type": "TOOL_CALL",
                "module": "Staff",
                "endpoint": "get_overtime_records",
                "parameters": {"department": "Logistics", "start_date": "2026-08-01", "end_date": "2026-08-14"},
            },
        },
        {
            "domain": "Documents",
            "user_query": "Search our archived contracts for supplier agreements with Acme Packing Corp.",
            "response": {
                "output_type": "TOOL_CALL",
                "module": "Documents",
                "endpoint": "search_document_archive",
                "parameters": {"query": "Acme Packing Corp supplier agreement", "category": "Contracts", "limit": 5},
            },
        },
    ],
    OutputSchemaType.ACTION_CONFIRMATION.value: [
        {
            "domain": "Staff & Payroll",
            "user_query": "Execute the bi-weekly payroll batch disbursement for all 24 employees.",
            "response": {
                "output_type": "ACTION_CONFIRMATION",
                "action_name": "Execute_Payroll_Batch",
                "target_module": "Staff",
                "impact_summary": "Initiating direct deposit transfers totaling $48,650.00 for 24 staff members. Funds will be debited from primary payroll account.",
                "requires_auth": True,
            },
        },
        {
            "domain": "POS & Inventory",
            "user_query": "Apply a permanent 20% price markdown across all discontinued summer apparel items.",
            "response": {
                "output_type": "ACTION_CONFIRMATION",
                "action_name": "Bulk_Price_Markdown",
                "target_module": "POS",
                "impact_summary": "Modifying retail prices across 142 catalog items in category 'Summer Apparel'. Expected total inventory valuation reduction: $3,210.00.",
                "requires_auth": True,
            },
        },
        {
            "domain": "Staff & Security",
            "user_query": "Deactivate system credentials and badge access for terminated employee EMP_88.",
            "response": {
                "output_type": "ACTION_CONFIRMATION",
                "action_name": "Revoke_User_Access",
                "target_module": "Staff",
                "impact_summary": "Immediately invalidating SSO credentials, POS PIN codes, and RFID building access badges for employee EMP_88.",
                "requires_auth": True,
            },
        },
        {
            "domain": "Finance & POS",
            "user_query": "Process bulk customer refund of $1,850 for the cancelled banquet reservation #BQ-402.",
            "response": {
                "output_type": "ACTION_CONFIRMATION",
                "action_name": "Execute_Customer_Refund",
                "target_module": "Finance",
                "impact_summary": "Reversing charge of $1,850.00 to original cardholder for booking BQ-402 and updating reservation ledger to CANCELLED.",
                "requires_auth": True,
            },
        },
        {
            "domain": "Inventory",
            "user_query": "Purge all expired perishable inventory records dated before 2025.",
            "response": {
                "output_type": "ACTION_CONFIRMATION",
                "action_name": "Purge_Historical_Inventory_Records",
                "target_module": "Inventory",
                "impact_summary": "Permanently archiving and removing 1,840 historical expired lot tracking records prior to 2025-01-01 from the active database.",
                "requires_auth": True,
            },
        },
    ],
}
