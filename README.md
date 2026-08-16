# Synthetic Data Distillation Engine
> Hybrid CPU/GPU Synthetic Data Distillation Pipeline: **Qwen2.5-7B-Instruct (Teacher)** ➔ **Qwen2.5-1.5B-Instruct (Student Dataset)**

An automated and resilient synthetic data generation pipeline designed to run seamlessly across both **standard CPU environments** and **high-end GPU servers** (like the RTX 4090). Utilizing dynamic hardware toggling, the pipeline automatically scales its multiprocessing, Flash Attention, and GGUF offloading to maximize generation throughput for your specific hardware.

---

## 📁 Repository Structure

```
africa-deep/
├── models/                         # GGUF teacher model weights directory (downloaded on server)
├── config/
│   ├── __init__.py
│   └── schemas_and_seeds.py        # 10 strict schemas + 50 domain-specific seed examples (5 per format)
├── src/
│   ├── __init__.py
│   ├── generator.py                # Llama-cpp engine (n_gpu_layers=100, flash_attn=True), dynamic temperature
│   ├── validator.py                # Pydantic v2 validation, JSON linting, exact + RapidFuzz deduplication
│   └── utils.py                    # Thread-safe JSONL writer, Rich UI dashboard & statistics
├── scripts/
│   ├── download_model.sh           # Shell script to download GGUF weights
│   └── download_model.py           # Python script for downloading weights via huggingface_hub
├── tests/
│   ├── __init__.py
│   ├── test_schemas_and_seeds.py   # Verifies all 50 seeds conform to strict schemas
│   ├── test_validator.py           # JSON extractor, validator, and deduplication unit tests
│   └── test_pipeline_integration.py# Integration test with MockGenerator
├── run_pipeline.py                 # Main CLI pipeline entry point (Worker process)
├── run_parallel.sh                 # Orchestrator script to spawn 4 concurrent GPU workers safely
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation & Deployment guide
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
- **Example 2 (Pharmacy):** Prescription Dispensing Volume by Category
- **Example 3 (Hospitality):** Dinner Service Revenue Mix
- **Example 4 (Logistics):** H1 Fleet On-Time Delivery Rate
- **Example 5 (Tech Services):** July Support Ticket Severity Distribution
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
- **Example 2 (Staff):** Written Disciplinary Notice
- **Example 3 (Finance):** Monthly P&L Executive Review
- **Example 4 (Pharmacy):** SOP-PHARM-082: Cold-Chain Storage
- **Example 5 (Tech Services):** Incident Post-Mortem
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
- **Example 2 (POS & Retail):** Explanation of cash discrepancy
- **Example 3 (Inventory):** Weekend coffee bean shortage projection
- **Example 4 (Staff):** Real-time shift supervisor status lookup
- **Example 5 (Finance):** Root-cause breakdown of utility cost spike
</details>

<details>
<summary><b>4. DEEP_RESEARCH (5 Seed Examples)</b></summary>

- **Example 1 (Retail & Finance):** Digital payment surcharge compliance
```json
{
  "output_type": "DEEP_RESEARCH",
  "target_sources": ["LOCAL_DB", "WEB_SEARCH"],
  "search_queries": [
    "2026 digital payment surcharge compliance regulations",
    "POS credit card fee pass-through state limits"
  ],
  "sources": [
    {
      "title": "State Department of Revenue Bulletin 2026-04",
      "type": "WEB_SEARCH",
      "record_id": "https://tax.state.gov/bulletin-2026-04",
      "relevance": "High"
    }
  ],
  "response": "Under updated 2026 regulations, credit card surcharge pass-throughs must not exceed actual merchant processing fees (capped at 3.0%)..."
}
```
- **Example 2 (Pharmacy):** DEA controlled substance disposal check
- **Example 3 (Hospitality):** Municipal Food Safety regulations
- **Example 4 (Logistics):** Regional diesel fuel surcharge index
- **Example 5 (Tech Services):** Enterprise SLA downtime penalty clauses
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
    { "staff_id": "EMP_104", "name": "David Kim", "role": "Floor Associate", "day": "Monday", "shift": "10:00 - 18:30" }
  ]
}
```
- **Example 2 (Hospitality):** Kitchen brigade roster
- **Example 3 (Pharmacy):** Pharmacist-in-Charge coverage
- **Example 4 (Logistics):** Warehouse dispatch schedules
- **Example 5 (Tech Services):** Tier-2 support 24/7 on-call rotation
</details>

<details>
<summary><b>6. PRODUCTIVITY_CHART (5 Seed Examples)</b></summary>

- **Example 1 (Staff & Retail):** Cashier scanning speed & transaction count
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
- **Example 2 (Tech Services):** Developer sprint velocity
- **Example 3 (Logistics):** Warehouse picker accuracy
- **Example 4 (Hospitality):** Server table turnover
- **Example 5 (Pharmacy):** Technician prescription fill throughput
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
- **Example 2 (Inventory):** Graphics card stock write-off
- **Example 3 (Finance):** Duplicate invoice submission
- **Example 4 (Pharmacy):** Controlled substance discrepancy
- **Example 5 (Staff & Access):** Unscheduled early clock-in
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
- **Example 2 (POS & Maintenance):** Service POS Register hardware
- **Example 3 (Finance):** Finalize Q2 Sales Tax Submission
- **Example 4 (Staff):** Assistant Manager onboarding checklist
- **Example 5 (Hospitality):** Kitchen exhaust hood sanitation
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
- **Example 2 (POS):** Pull daily drawer reconciliation
- **Example 3 (Inventory):** Check SKU stock level
- **Example 4 (Staff):** Retrieve department overtime hours
- **Example 5 (Documents):** Search supplier contracts
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
- **Example 2 (POS & Inventory):** Apply permanent markdown
- **Example 3 (Staff & Security):** Revoke user SSO credentials
- **Example 4 (Finance & POS):** Process reservation refund
- **Example 5 (Inventory):** Purge historical inventory logs
</details>

---

## 🚀 GPU Server Deployment & Quickstart

### 1. Setup Environment
Ensure you are running on a server with an NVIDIA GPU (e.g., RTX 4090).
```bash
git clone https://github.com/clementcyberknight/distillation-pipeline.git africa-deep
cd africa-deep
```

### 2. Install CUDA-Accelerated Dependencies
To fully utilize the GPU, you MUST install the CUDA-compiled wheel for `llama-cpp-python` (e.g., cu121 for CUDA 12.1).
```bash
pip install --upgrade pip
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121 --no-cache-dir
pip install -r requirements.txt
```

### 3. Download Teacher Model Weights
Download the `qwen2.5-7b-instruct-q4_k_m.gguf` model to the server:
```bash
bash scripts/download_model.sh
```

### 4. Run Parallel Pipeline (RTX 4090 / 24-Core EPYC)
To achieve 15x-25x throughput, we use an orchestrator bash script that splits the schemas into 4 background Python processes, safely writing to isolated split files and merging them atomically.
```bash
chmod +x run_parallel.sh
./run_parallel.sh
```
*Monitor progress via `tail -f logs/worker_*.log` and GPU usage via `watch -n 1 nvidia-smi`.*

### 5. CPU Server Deployment (Optional)
If you are deploying on a standard CPU VPS instead of an RTX 4090, do **not** run `run_parallel.sh` as 4 concurrent models will cause an Out-Of-Memory crash.
Instead, use the `--device cpu` flag directly with `run_pipeline.py`. This safely disables Flash Attention, forces `n_gpu_layers=0`, and optimizes threads/batch sizes for CPU limits:
```bash
python run_pipeline.py --device cpu --samples-per-schema 50
```

### 6. Local Dry-Run / Testing
You can verify the entire pipeline locally without GPU weights using `--mock`:
```bash
python run_pipeline.py --mock --device cpu --samples-per-schema 5 --include-seeds
```

---

## ⚙️ High-End Hardware Tuning Guide (RTX 4090 / EPYC 7443)

The architecture is configured to saturate a 24GB VRAM GPU alongside a massive 48-thread CPU via 4 concurrent generator processes.

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| **`n_gpu_layers`** | `100` | Forces 100% of the Qwen2.5-7B neural network matrix multiplications onto the RTX 4090's Tensor cores, maximizing compute efficiency. |
| **`flash_attn`** | `True` | Enabled in `src/generator.py` to reduce the KV Cache memory footprint by 50%. This is absolutely critical to avoid CUDA Out-Of-Memory (OOM) crashes when packing 4 simultaneous 7B models into 24GB VRAM. |
| **`n_threads`** | `6` per worker | $4 \text{ workers} \times 6 \text{ threads} = 24 \text{ total threads}$. Matches the physical core count of the AMD EPYC 7443 CPU, reducing thread contention and context-switching overhead since the CPU is only doing JSON I/O and GBNF parsing. |
| **`n_batch`** | `2048` | Dramatically speeds up token evaluation and prompt processing speed for the extensive few-shot seed prompt structures. |
| **`n_ctx`** | `4096` | Accommodates the long ChatML few-shot prompts and detailed multi-turn schema definitions. |
| **Concurrency Strategy** | 4 Isolated Workers | Schemas are divided among 4 separate Python processes launched via `run_parallel.sh`. Each worker writes to its own `data_splits/dataset_wX.jsonl` to prevent filesystem race conditions and torn JSON lines, then merges at the end. |

---

## 📊 Dataset Output Format

The final merged `distillation_dataset.jsonl` contains line-delimited JSON objects perfectly structured for direct SFT fine-tuning with `unsloth` or HuggingFace `trl`:

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
