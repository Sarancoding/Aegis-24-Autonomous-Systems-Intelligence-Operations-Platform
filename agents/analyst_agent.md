# Analyst Agent Profile

## Role: Compliance Analyst

**Primary Responsibility:** Audit report generation, PDF creation, test result visualization, and quality evaluation against standards.

---

## Core Competencies

### 1. Audit Report Generation
- Parse red team results and execution traces
- Generate compliance audit Markdown reports
- Compare outputs against `brain/examples/good_audit_report.md`

### 2. PDF Creation
- Convert Markdown reports to PDF format
- Ensure proper formatting and pagination
- Include digital signatures for integrity

### 3. Test Result Visualization
- Create pass/fail matrices
- Generate charts for metrics dashboards
- Highlight critical failures prominently

### 4. Quality Evaluation
- Judge outputs vs. good examples
- Score reports on completeness and accuracy
- Feed misses back for correction

---

## Report Generation Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│   Red Team  │ --> │    Trace     │ --> │    Audit    │ --> │    PDF     │
│   Results   │     │    Data      │     │   Report    │     │  Export    │
│   (JSON)    │     │  (Phoenix)   │     │  (Markdown) │     │            │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
                           │                    │
                           ▼                    ▼
                    [Validate Completeness]  [Quality Check vs
                                              good_audit_report.md]
```

---

## Implementation

### Audit Report Generator
```python
from datetime import datetime
import json

class AuditReportGenerator:
    """Generate compliance audit reports."""
    
    def __init__(self, example_report_path: str = "brain/examples/good_audit_report.md"):
        with open(example_report_path) as f:
            self.example_report = f.read()
    
    def generate_report(
        self,
        redteam_results: dict,
        trace_data: list,
        lineage_data: dict
    ) -> str:
        """Generate full audit report in Markdown."""
        
        report_id = f"AUDIT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        report = f"""# Aegis-24 Compliance Audit Report

**Report ID:** {report_id}
**Generated:** {datetime.utcnow().isoformat()}Z
**Audit Period:** {self._get_audit_period(trace_data)}
**Auditor:** Automated Compliance Analyst Agent v1.0
**Review Status:** {'PASSED' if self._check_all_passed(redteam_results) else 'FAILED'}

---

## Executive Summary

{self._generate_executive_summary(redteam_results)}

---

## 1. Red Team Exercise Results

{self._generate_redteam_section(redteam_results)}

---

## 2. PII Protection Analysis

{self._generate_pii_section(trace_data)}

---

## 3. Sandbox Security Verification

{self._generate_sandbox_section(trace_data)}

---

## 4. Token Cost Attribution

{self._generate_cost_section(trace_data)}

---

## 5. Data Lineage Tracking

{self._generate_lineage_section(lineage_data)}

---

## 6. Guardrail Performance

{self._generate_guardrail_section(redteam_results)}

---

## 7. Recommendations

{self._generate_recommendations(redteam_results, trace_data)}

---

## 8. Certification

**System Status:** {'✅ PRODUCTION READY' if self._check_all_passed(redteam_results) else '❌ NOT READY'}

**Certified By:** Compliance Analyst Agent v1.0
**Certification Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
**Next Audit Due:** {(datetime.utcnow().timedelta(days=30)).strftime('%Y-%m-%d')}

**Digital Signature:** `{self._generate_signature(report_id)}`

---

*This report was generated automatically by Aegis-24 Compliance Analyst Agent.*
*For questions, contact: compliance@aegis24.internal*
"""
        
        return report
    
    def _check_all_passed(self, results: dict) -> bool:
        """Check if all security gates passed."""
        return (
            results.get('adversarial_blocked', 0) == results.get('adversarial_total', 0) and
            results.get('pii_leaks', 0) == 0 and
            results.get('sandbox_escapes', 0) == 0
        )
```

### PDF Generator
```python
from markdown import markdown
from weasyprint import HTML, CSS

def convert_markdown_to_pdf(markdown_content: str, output_path: str):
    """Convert Markdown content to PDF."""
    
    # Convert Markdown to HTML
    html_content = markdown(markdown_content, extensions=['tables', 'fenced_code'])
    
    # Add styling
    css = CSS(string="""
        @page {
            size: letter;
            margin: 1in;
        }
        body {
            font-family: Georgia, serif;
            font-size: 11pt;
            line-height: 1.5;
        }
        h1, h2, h3 {
            font-family: Arial, sans-serif;
            color: #333;
        }
        pre, code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .pass { color: green; }
        .fail { color: red; }
    """)
    
    # Generate PDF
    HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
    
    return output_path
```

### Quality Evaluator
```python
class ReportQualityEvaluator:
    """Evaluate audit report quality against standards."""
    
    QUALITY_CRITERIA = [
        "clear_pass_fail_status",
        "executive_summary_present",
        "trace_ids_referenced",
        "token_cost_attribution",
        "citation_verification",
        "data_lineage_shown",
        "redteam_results_200_plus",
        "pii_detection_stats",
        "sandbox_escape_analysis",
        "guardrail_performance",
        "recommendations_section",
        "digital_signature",
        "timestamp_utc",
        "version_information"
    ]
    
    def evaluate(self, report: str, example_report: str) -> dict:
        """Evaluate report quality."""
        
        scores = {}
        for criterion in self.QUALITY_CRITERIA:
            scores[criterion] = self._check_criterion(report, example_report, criterion)
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            "scores": scores,
            "overall_score": overall_score,
            "passed": overall_score >= 0.9,
            "missing": [k for k, v in scores.items() if not v]
        }
    
    def _check_criterion(self, report: str, example: str, criterion: str) -> bool:
        """Check single quality criterion."""
        # Implementation depends on specific criterion
        pass
```

---

## Configuration Files

### config/agents.yaml (Analyst Section)
```yaml
analyst_agent:
  report_generation:
    model: "gpt-4-turbo-preview"
    temperature: 0.3
    max_tokens: 5000
  
  pdf_export:
    format: "letter"
    include_toc: true
    embed_fonts: true
  
  quality_check:
    min_score: 0.9
    criteria_file: "brain/examples/good_audit_report.md"
```

---

## Performance Requirements

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Report Accuracy | 100% | <99% |
| PDF Generation Time | <10s | >30s |
| Quality Score | >0.9 | <0.8 |
| Completeness | 100% | <95% |

---

## Testing Requirements

### Unit Tests
- `test_report_generation_structure()`
- `test_pdf_conversion()`
- `test_quality_evaluation()`

### Integration Tests
- `test_full_report_pipeline()`
- `test_comparison_with_example()`

---

## Dependencies

```txt
markdown>=3.5.0
weasyprint>=60.0
```

---

*Version: 1.0.0*
*Last Updated: $(date)*
