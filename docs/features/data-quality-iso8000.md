# Data Quality ISO 8000 Standard Summary

## Overview

**ISO 8000** is the international standard for **data quality** and **master data quality**. It provides a framework for organizations to ensure their data meets consistent quality requirements across systems, processes, and trading partners.

Unlike data management standards (e.g., ISO 15489 for records management), ISO 8000 specifically focuses on **measurable characteristics** of data quality itself.

---

## Core Principles

### 1. Portability
Data must be exchangeable between organizations and systems without quality loss. This ensures data integrity when shared across enterprise boundaries.

### 2. Self-Describing
Data should carry sufficient metadata to be understood independently of the application that created it.

### 3. Fit for Purpose
Data quality is measured against the requirements of its intended use. There is no universal "perfect" quality—quality is contextual.

---

## ISO 8000 Structure

| Part | Name | Focus |
|------|------|-------|
| **ISO 8000-1** | Overview | General concepts and terminology |
| **ISO 8000-2** | Vocabulary | Definitions of key terms |
| **ISO 8000-8** | Information and data quality measures | Quantitative quality metrics |
| **ISO 8000-10x** | Master data quality | Quality requirements for master data |
| **ISO 8000-11x** | Master data quality: Profile | Identifying and describing master data |
| **ISO 8000-12x** | Master data quality: Quality score | Scoring methodology |

---

## Eight Dimensions of Data Quality (ISO 8000-8)

ISO 8000-8 defines the following measurable dimensions:

### 1. **Completeness**
- **Definition**: All required data is present
- **Measures**:
  - Presence rate (% of fields populated)
  - Population rate (% of records with all required fields)
- **Example**: A customer record missing email address has incomplete data

### 2. **Uniqueness**
- **Definition**: Data represents a single, distinct entity without unnecessary duplication
- **Measures**:
  - Duplicate rate (% of duplicate records)
  - Key uniqueness (% of unique primary keys)
- **Example**: Two records for "John Smith" at the same address represent non-unique data

### 3. **Accuracy**
- **Definition**: Data correctly represents the real-world entity or event
- **Measures**:
  - Error rate (% of incorrect values)
  - Deviation rate (% of values outside acceptable tolerance)
- **Example**: A birth date of 1990-01-01 when the actual date is 1985-06-15 is inaccurate

### 4. **Consistency**
- **Definition**: Data is compatible and does not conflict across systems or records
- **Measures**:
  - Conflict rate (% of contradicting values across systems)
  - Format consistency (% of values following standard formats)
- **Example**: Address formatted as "St." in one system and "Street" in another

### 5. **Timeliness**
- **Definition**: Data is available and current when needed
- **Measures**:
  - Latency (time between event and data availability)
  - Freshness (% of data updated within required timeframe)
- **Example**: Inventory data updated daily when real-time updates are required

### 6. **Validity**
- **Definition**: Data conforms to defined formats, business rules, and constraints
- **Measures**:
  - Validation rate (% of values passing business rules)
  - Format compliance (% of values matching expected patterns)
- **Example**: An email field containing "not-an-email" is invalid

### 7. **Accessibility**
- **Definition**: Data can be retrieved and used by authorized users when needed
- **Measures**:
  - Availability rate (% of time data is accessible)
  - Retrieval time (time to access data)
- **Example**: A database that is offline 5% of the month has accessibility issues

### 8. **Integrity**
- **Definition**: Relationships between data elements are maintained correctly
- **Measures**:
  - Referential integrity rate (% of valid foreign key relationships)
  - Orphan record rate (% of records without valid parent relationships)
- **Example**: An order referencing a non-existent customer has integrity issues

---

## Quality Scoring Methodology

ISO 8000-12x defines a scoring approach:

```
Data Quality Score = Σ (Dimension Weight × Dimension Score)
```

### Weighting Example

| Dimension | Weight | Score (0-100) | Weighted Score |
|-----------|--------|---------------|----------------|
| Completeness | 25% | 92 | 23.0 |
| Accuracy | 25% | 88 | 22.0 |
| Uniqueness | 15% | 95 | 14.25 |
| Consistency | 15% | 90 | 13.5 |
| Timeliness | 10% | 85 | 8.5 |
| Validity | 5% | 98 | 4.9 |
| Accessibility | 3% | 99 | 2.97 |
| Integrity | 2% | 97 | 1.94 |
| **Total** | **100%** | — | **91.06** |

### Quality Levels (Example)

| Score Range | Quality Level | Action |
|-------------|---------------|--------|
| 90-100 | Excellent | Monitor and maintain |
| 75-89 | Good | Minor improvements needed |
| 60-74 | Acceptable | Targeted remediation required |
| 40-59 | Poor | Significant improvement required |
| 0-39 | Critical | Immediate remediation required |

---

## Relevance to MasterDataCleaner

### Alignment with Project Goals

MasterDataCleaner's data cleaning capabilities directly map to ISO 8000 dimensions:

| ISO 8000 Dimension | MasterDataCleaner Feature | Operations |
|--------------------|---------------------------|------------|
| **Completeness** | Missing value handling | Fill, Drop, Impute, Forward/Back fill |
| **Uniqueness** | Deduplication | Exact match, Fuzzy match, Merge |
| **Accuracy** | Data correction | Type conversion, Format standardization |
| **Consistency** | Format standardization | Date formats, Number formats, Case normalization |
| **Timeliness** | Data freshness | Date parsing, Timezone normalization |
| **Validity** | Data validation | Regex extraction, Pattern matching, Range validation |
| **Integrity** | Referential checks | Foreign key validation, Relationship preservation |

### Potential Future Enhancements

Based on ISO 8000, MasterDataCleaner could add:

1. **Quality Scoring Dashboard**
   - Automated quality assessment across all dimensions
   - Visual scoring with before/after comparisons
   - Trend tracking over time

2. **Quality Rules Engine**
   - Custom validation rules (business-specific)
   - Rule templates for common patterns
   - Rule inheritance across datasets

3. **Profiling Reports**
   - Detailed dimension-specific profiling
   - Distribution analysis for numeric/categorical data
   - Anomaly detection

4. **Quality Thresholds**
   - Configurable minimum quality thresholds
   - Automatic blocking when thresholds violated
   - Quality gates for data imports

5. **Quality Monitoring**
   - Continuous quality monitoring for live datasets
   - Alerts when quality degrades
   - SLA tracking for data quality commitments

6. **Quality Metadata**
   - Quality scores stored with datasets
   - Quality history and audit trail
   - Quality lineage (tracking improvements over operations)

---

## ISO 8000 vs Other Quality Frameworks

| Framework | Focus | Key Difference |
|-----------|-------|----------------|
| **ISO 8000** | Data quality dimensions & metrics | Quantitative measurement focus |
| **DAMA-DMBOK** | Data management body of knowledge | Broader data governance scope |
| **DQMF** | Data Quality Management Framework | Government-focused implementation |
| **TDQM** | Total Data Quality Management | Academic/research framework |
| **Six Sigma** | Process quality (DMAIC) | Manufacturing origin, adaptable |

ISO 8000 is unique in its focus on **measurable, quantitative data quality dimensions** applicable across industries.

---

## Key Definitions (ISO 8000-2)

| Term | Definition |
|------|------------|
| **Data Quality** | Degree to which data meets requirements for intended use |
| **Master Data** | Data about business entities (customers, products, suppliers) |
| **Data Quality Score** | Quantitative measure of data quality across dimensions |
| **Data Profiling** | Process of analyzing data to assess quality characteristics |
| **Data Cleansing** | Process of detecting and correcting data quality issues |

---

## Implementation Checklist

For MasterDataCleaner to fully align with ISO 8000:

- [ ] Map all cleaning operations to ISO 8000 dimensions
- [ ] Add quality metrics calculation for each dimension
- [ ] Implement quality scoring system
- [ ] Create quality profiling reports
- [ ] Add quality thresholds and validation rules
- [ ] Store quality metadata with datasets
- [ ] Provide quality trend analysis
- [ ] Export quality reports (JSON/CSV)

---

## References

- ISO 8000-1:2022 — Data quality — Part 1: Overview
- ISO 8000-2:2022 — Data quality — Part 2: Vocabulary
- ISO 8000-8:2015 — Data quality — Part 8: Information and data quality measures
- ISO 8000-10:2022 — Data quality — Part 10: Master data quality: Overview
- ISO 8000-11:2022 — Data quality — Part 11: Master data quality: Data quality measures for master data
- ISO 8000-12:2022 — Data quality — Part 12: Master data quality: Quality score

---

## Further Reading

- [ISO TC 154 — Identification and information exchange](https://www.iso.org/committee/50698.html)
- [ISO 8000 Wikipedia](https://en.wikipedia.org/wiki/ISO_8000)
- [EDM Council DCAM](https://edmcouncil.org/frameworks-and-standards/dcam-data-management-capability-assessment-model/)

---

*This summary provides a foundation for aligning MasterDataCleaner with international data quality standards. As the project evolves, ISO 8000 compliance can be used as a benchmark for feature completeness and quality assurance.*
