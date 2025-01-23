# EASA Safety Recommendations Template
**Document Reference:** EASA/REC/2024/001  
**Effective Date:** 2024-01-01  
**Compliance Basis:** Regulation (EU) 376/2014

## Priority Matrix
| Level       | Response Time     | Required Actions                  |
|-------------|-------------------|-----------------------------------|
| Critical    | 72 hours          | Immediate ground action           |
| High        | 30 days           | Corrective action plan required   |
| Medium      | 90 days           | Safety review inclusion           |
| Low         | Next audit cycle  | Monitoring recommended            |

## Risk Categories
{% for category in categories %}
### {{ category.name }} ({{ category.id }})
**Regulatory Basis:** {{ category.easa_reference }}  
**Examples:**  
{% for example in category.examples %}- {{ example }}  
{% endfor %}

**Required Actions:**  
{{ compliance_matrix.priority_levels[category.priority] }}

{% endfor %}

## Mandatory Reporting
{% for requirement in compliance_matrix.reporting_requirements.mandatory_reporting %}- {{ requirement }}  
{% endfor %}