# Synthetic Data Distillation Engine
> Offline Synthetic Data Distillation Pipeline: **Qwen2.5-7B-Instruct (Teacher)** ➔ **Qwen2.5-1.5B-Instruct (Student Dataset)**

An automated, CPU-optimized, and resilient synthetic data generation pipeline designed to run on a Linux VPS (6 vCPU, 12 GB RAM) or local environment. The pipeline generates structured training pairs across **6 core business verticals** and **10 strict JSON output schemas**.

---

## 📁 Repository Structure

```
africa-deep/
├── models/                         # GGUF teacher model weights directory (downloaded on VPS)
├── config/
│   ├── __init__.py
│   └── schemas_and_seeds.py        # 10 strict schemas + 50 domain-specific seed examples (5 per format)
├── src/
│   ├── __init__.py
│   ├── generator.py                # Llama-cpp engine (n_threads=5, n_ctx=4096), batching, temp variation (0.75-0.85)
│   ├── validator.py                # Pydantic v2 validation, JSON linting, exact + RapidFuzz deduplication
│   └── utils.py                    # Thread-safe JSONL writer, Rich UI dashboard & statistics
├── scripts/
│   ├── download_model.sh           # Shell script to download GGUF weights directly on VPS
│   └── download_model.py           # Python script for downloading weights via huggingface_hub
├── tests/
│   ├── __init__.py
│   ├── test_schemas_and_seeds.py   # Verifies all 50 seeds conform to strict schemas
│   ├── test_validator.py           # JSON extractor, validator, and deduplication unit tests
│   └── test_pipeline_integration.py# Integration test with MockGenerator
├── run_pipeline.py                 # Main CLI pipeline entry point
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation & VPS deployment guide
```

---

## 🎯 6 Business Verticals & 10 Standardized JSON Schemas

The desktop business assistant handles:
1. **Documents**
2. **POS (Point of Sale)**
3. **Inventory**
4. **Staff**
5. **Finance**
6. **Task Management**

### The 10 Target JSON Schemas & 5 Real Seed Examples Each (50 Total)

<details>
<summary><b>1. GENERATIVE_CHART (5 Seed Examples)</b></summary>

- **Example 1 (Retail):** Q1 Financial Breakdown: Revenue vs Expenses
```json
{
  "output_type": "GENERATIVE_CHART",
  "chart_type": "bar",
  "title": "Q1 Financial Breakdown: Revenue vs Expenses",
  "summary": "Total Q1 revenue reached $415,000 against operating expenses of $295,000, delivering an average net margin of 28.9%.",
  "data": {
    "labels": ["January", "February", "March"],
    "datasets": [
      { "label": "Revenue ($)", "values": [128000, 139000, 148000] },
      { "label": "Expenses ($)", "values": [96000, 98000, 101000] }
    ]
  }
}
```
- **Example 2 (Pharmacy):** Prescription Dispensing Volume by Category (Line chart across Nov, Dec, Jan, Feb)
- **Example 3 (Hospitality):** Dinner Service Revenue Mix across Tuesday - Sunday
- **Example 4 (Logistics):** H1 Fleet On-Time Delivery Rate vs SLA Benchmark
- **Example 5 (Tech Services):** July Support Ticket Severity Distribution (Pie chart)
</details>

<details>
<summary><b>2. DOCUMENT_OUTPUT (5 Seed Examples)</b></summary>

- **Example 1 (Inventory):** Q3 Warehouse Inventory Audit Summary
```json
{
  "output_type": "DOCUMENT_OUTPUT",
  "doc_title": "Q3 Warehouse Inventory Audit Summary",
  "format": "markdown",
  "content": "# Q3 Warehouse Inventory Audit\n**Facility:** Central Fulfillment Depot #4\n**Auditor:** Lead Logistics Specialist\n\n## Executive Summary\nInventory shrinkage decreased by 3.8% quarter-over-quarter...\n\n## Action Items\n1. Recalibrate barcode scanners at Receiving Dock B.\n2. Reorder buffer stock for top 20 velocity items."
}
```
- **Example 2 (Staff):** Written Disciplinary Notice: Attendance Policy
- **Example 3 (Finance):** Monthly P&L Executive Review - July 2026
- **Example 4 (Pharmacy):** SOP-PHARM-082: Cold-Chain Storage & Temperature Logging
- **Example 5 (Tech Services):** Incident Post-Mortem: DB Connection Pool Starvation
</details>

<details>
<summary><b>3. CONVERSATIONAL_CHAT (5 Seed Examples)</b></summary>

- **Example 1 (General Business):** System capability explanation across 6 core modules
```json
{
  "output_type": "CONVERSATIONAL_CHAT",
  "message": "I can assist you across all 6 core business modules: Documents, Point of Sale (POS), Inventory, Staff Rostering, Financial Reports, and Task Management. Let me know if you want to inspect register anomalies, generate a sales chart, or adjust this week's shift schedule."
}
```
- **Example 2 (POS & Retail):** Explanation of -$45.20 cash discrepancy on Register 3
- **Example 3 (Inventory):** Weekend coffee bean inventory shortage projection
- **Example 4 (Staff):** Real-time lead shift supervisor status lookup
- **Example 5 (Finance):** Root-cause breakdown of summer utility cost spike
</details>

<details>
<summary><b>4. DEEP_RESEARCH (5 Seed Examples)</b></summary>

- **Example 1 (Retail & Finance):** Digital payment surcharge compliance vs internal fee logs
```json
{
  "output_type": "DEEP_RESEARCH",
  "target_sources": ["LOCAL_DB", "WEB_SEARCH"],
  "search_queries": [
    "2026 digital payment surcharge compliance regulations",
    "POS credit card fee pass-through state limits",
    "Internal tax audit variance Q1-Q2 2026"
  ],
  "sources": [
    {
      "title": "State Department of Revenue Bulletin 2026-04",
      "type": "WEB_SEARCH",
      "record_id": "https://tax.state.gov/bulletin-2026-04",
      "relevance": "High"
    },
    {
      "title": "2026 Internal Merchant Fee Reconciliation Report",
      "type": "LOCAL_DB",
      "record_id": "FIN-REC-2026-088",
      "relevance": "High"
    }
  ],
  "response": "Under updated 2026 regulations, credit card surcharge pass-throughs must not exceed actual merchant processing fees (capped at 3.0%) and must be itemized before payment authorization..."
}
```
- **Example 2 (Pharmacy):** DEA Schedule II controlled substance disposal & batch inventory check
- **Example 3 (Hospitality):** Municipal Food Safety code sous-vide holding regulations
- **Example 4 (Logistics):** Regional diesel fuel surcharge index vs carrier contracts
- **Example 5 (Tech Services):** Enterprise SLA downtime penalty clauses vs quarterly uptime log
</details>

<details>
<summary><b>5. SHIFT_SCHEDULE (5 Seed Examples)</b></summary>

- **Example 1 (Retail):** Cashier and floor team weekly roster
```json
{
  "output_type": "SHIFT_SCHEDULE",
  "week_starting": "2026-08-17",
  "schedule": [
    { "staff_id": "EMP_101", "name": "Sarah Jenkins", "role": "Head Cashier", "day": "Monday", "shift": "08:00 - 16:30" },
    { "staff_id": "EMP_104", "name": "David Kim", "role": "Floor Associate", "day": "Monday", "shift": "10:00 - 18:30" },
    { "staff_id": "EMP_108", "name": "Alicia Rivera", "role": "Inventory Clerk", "day": "Tuesday", "shift": "07:00 - 15:30" }
  ]
}
```
- **Example 2 (Hospitality):** Kitchen brigade and dining room floor roster
- **Example 3 (Pharmacy):** Licensed Pharmacist-in-Charge and technician coverage
- **Example 4 (Logistics):** Warehouse dispatch and forklift operator schedules
- **Example 5 (Tech Services):** Tier-2 customer support 24/7 on-call rotation
</details>

<details>
<summary><b>6. PRODUCTIVITY_CHART (5 Seed Examples)</b></summary>

- **Example 1 (Staff & Retail):** Cashier Michael Chen Q2 scanning speed & transaction count
```json
{
  "output_type": "PRODUCTIVITY_CHART",
  "employee_name": "Michael Chen",
  "period": "Q2 2026",
  "chart_type": "line",
  "data": {
    "labels": ["April", "May", "June"],
    "datasets": [
      { "label": "Items Scanned / Min", "values": [18.4, 21.2, 23.8] },
      { "label": "Transactions Processed", "values": [1240, 1380, 1490] }
    ]
  },
  "summary": "Michael improved scanning speed by 29.3% across Q2 while maintaining zero cash drawer variances."
}
```
- **Example 2 (Tech Services):** Developer Priya Sharma sprint velocity & bug resolutions
- **Example 3 (Logistics):** Warehouse picker Jamal Wright picks-per-hour and accuracy
- **Example 4 (Hospitality):** Server Chloe Bennett table turnover and tip percentage
- **Example 5 (Pharmacy):** Technician Brianna Scott prescription fill throughput
</details>

<details>
<summary><b>7. RED_FLAG_ALERT (5 Seed Examples)</b></summary>

- **Example 1 (POS & Retail):** Unauthorized 90% manual markdown
```json
{
  "output_type": "RED_FLAG_ALERT",
  "severity": "HIGH",
  "flagged_module": "POS",
  "anomaly_type": "UNUSUALLY_HIGH_DISCOUNT",
  "transaction_id": "TXN_98421",
  "reasoning": "A 90% manual markdown ($450 value) was applied on item SKU-8812 without manager override credentials.",
  "recommended_action": "Review register surveillance video and interview Cashier #104 regarding TXN_98421."
}
```
- **Example 2 (Inventory):** After-hours graphics card stock write-off
- **Example 3 (Finance):** Duplicate $12,400 invoice submission from vendor
- **Example 4 (Pharmacy):** Schedule II controlled substance count discrepancy
- **Example 5 (Staff & Access):** Unscheduled 4-hour early clock-in
</details>

<details>
<summary><b>8. AUTO_TASK (5 Seed Examples)</b></summary>

- **Example 1 (Inventory):** Count Cold Storage Dairy Inventory
```json
{
  "output_type": "AUTO_TASK",
  "task_title": "Count Cold Storage Dairy Inventory",
  "priority": "HIGH",
  "assignee_role": "Inventory Clerk",
  "due_date": "2026-08-16",
  "subtasks": [
    "Perform cycle count of milk crates and yogurt pallets in Walk-in Cooler A",
    "Check expiration dates on Greek yogurt stock",
    "Enter final count in inventory terminal"
  ]
}
```
- **Example 2 (POS & Maintenance):** Service POS Register 4 printer hardware
- **Example 3 (Finance):** Finalize Q2 Sales Tax Submission
- **Example 4 (Staff):** Assistant Manager onboarding checklist
- **Example 5 (Hospitality):** Kitchen exhaust hood & grease trap sanitation
</details>

<details>
<summary><b>9. TOOL_CALL (5 Seed Examples)</b></summary>

- **Example 1 (Finance):** Fetch P&L statement
```json
{
  "output_type": "TOOL_CALL",
  "module": "Finance",
  "endpoint": "get_pnl_statement",
  "parameters": { "quarter": "Q2", "year": 2026, "include_tax_provision": true }
}
```
- **Example 2 (POS):** Pull daily drawer reconciliation for Register #2
- **Example 3 (Inventory):** Check SKU stock level with safety stock
- **Example 4 (Staff):** Retrieve department overtime hours
- **Example 5 (Documents):** Search supplier contracts in archive
</details>

<details>
<summary><b>10. ACTION_CONFIRMATION (5 Seed Examples)</b></summary>

- **Example 1 (Staff & Payroll):** Execute bi-weekly payroll batch disbursement
```json
{
  "output_type": "ACTION_CONFIRMATION",
  "action_name": "Execute_Payroll_Batch",
  "target_module": "Staff",
  "impact_summary": "Initiating direct deposit transfers totaling $48,650.00 for 24 staff members. Funds will be debited from primary payroll account.",
  "requires_auth": true
}
```
- **Example 2 (POS & Inventory):** Apply permanent 20% markdown on discontinued apparel
- **Example 3 (Staff & Security):** Revoke user SSO & RFID credentials for terminated employee
- **Example 4 (Finance & POS):** Process $1,850 refund for cancelled banquet reservation
- **Example 5 (Inventory):** Purge historical perishable inventory logs before 2025
</details>

---

## 🚀 VPS Deployment & Quickstart

### 1. Setup Environment on Linux VPS (6 vCPU, 12 GB RAM)
```bash
git clone <your-repo> africa-deep
cd africa-deep

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Download Teacher Model Weights (`qwen2.5-7b-instruct-q4_k_m.gguf`)
Run the automated downloader directly on the VPS:
```bash
bash scripts/download_model.sh
```

### 3. Run Distillation Pipeline
```bash
# Generate 50 examples per schema (500 total) across all 10 formats using 5 CPU threads
python run_pipeline.py \
  --model-path models/qwen2.5-7b-instruct-q4_k_m.gguf \
  --output-file distillation_dataset.jsonl \
  --samples-per-schema 50 \
  --batch-size 15 \
  --threads 5 \
  --ctx-size 4096 \
  --include-seeds
```

### 4. Local Dry-Run / Testing (No GGUF Download Needed)
You can verify the entire pipeline on your local machine using `--mock`:
```bash
python run_pipeline.py --mock --samples-per-schema 5 --include-seeds
```

---

## ⚙️ Hardware Tuning Guide (6 vCPU / 12 GB RAM)

| Parameter | Recommended Value | Rationale |
| :--- | :--- | :--- |
| `n_threads` | `5` | Allocates 5 out of 6 vCPUs to llama.cpp, leaving 1 vCPU for OS I/O and preventing thread contention. |
| `n_ctx` | `4096` | Accommodates few-shot prompts and detailed multi-turn schema definitions. |
| `n_batch` | `512` | Optimized prompt evaluation throughput within 12 GB RAM constraints. |
| `temperature` | `0.75 - 0.85` | Varied dynamically per batch to maximize syntactic creativity while preserving JSON validity. |
| `fuzzy_threshold` | `0.85` | Discards queries with ≥85% similarity against the established corpus. |

---

## 📊 Dataset Output Format

Each line of `distillation_dataset.jsonl` contains a single JSON object structured for direct SFT fine-tuning with `unsloth` / `transformers`:

```json
{
  "system_prompt": "You are a desktop business assistant. Respond using the appropriate structured JSON output schema.",
  "user_query": "Show me the revenue vs expense chart for Q1 across all store locations.",
  "response": {
    "output_type": "GENERATIVE_CHART",
    "chart_type": "bar",
    "title": "Q1 Financial Breakdown: Revenue vs Expenses",
    "summary": "Total Q1 revenue reached $415,000 against operating expenses of $295,000, delivering an average net margin of 28.9%.",
    "data": {
      "labels": ["January", "February", "March"],
      "datasets": [
        { "label": "Revenue ($)", "values": [128000, 139000, 148000] },
        { "label": "Expenses ($)", "values": [96000, 98000, 101000] }
      ]
    }
  }
}
```
