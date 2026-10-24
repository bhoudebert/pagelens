# Multimodal PDF Search Specification

## PDF ingestion

### Requirement: traceable regions

The system MUST render each accepted PDF page and persist searchable regions with the
source path, document identity, one-based page number, page-relative bounding box, and
preview path.

#### Scenario: ingest a vector drawing

- **WHEN** a PDF contains a vector drawing rather than an embedded raster image
- **THEN** the drawing participates in search through the rendered page region

### Requirement: idempotent replacement

Re-ingesting an unchanged source MUST NOT create duplicate searchable regions. Re-ingesting
a changed source MUST replace the previous document version atomically.

## Multimodal retrieval

### Requirement: text and image queries

The system MUST accept text, one or more reference images, or both. It MUST reject a query
that supplies neither. Text and images MUST be encoded using compatible encoders from the
same retrieval model.

#### Scenario: visual evidence has no label

- **GIVEN** a page region depicts the requested object but has no associated text
- **WHEN** the text encoder places the query near that region's image vector
- **THEN** the region can appear as a candidate

### Requirement: grounded results

Every result MUST include its PDF path, page, region, score, and preview. The CLI MUST NOT
represent vector similarity as proof of exact product identity.

## Optional verification

### Requirement: evidence-aware verification

When verification is enabled, the vision model MUST receive the candidate crop, complete
source page, query, associated text, and evidence policy. Its structured response MUST
distinguish confirmed, rejected, and uncertain candidates and SHOULD extract metadata only
when supported by supplied evidence.

#### Scenario: visual evidence excludes text-only mentions

- **GIVEN** verification uses the `visual` evidence policy
- **WHEN** a page names the requested object but does not depict it
- **THEN** the verifier MUST NOT confirm the page

#### Scenario: any evidence includes text-only mentions

- **GIVEN** verification uses the `any` evidence policy
- **WHEN** a page explicitly names the requested object without depicting it
- **THEN** the verifier MAY confirm the page from that text

#### Scenario: broad object category

- **WHEN** the query is `pump`
- **THEN** water pumps and fuel pumps MAY satisfy the category
- **AND** a `water pump` query MUST NOT be confirmed from a fuel pump alone

## Evaluation

### Requirement: machine-readable ground truth

The repository MUST provide synthetic page-level scenarios covering visual-only objects,
text-only references, broad categories, exact references, small objects, and hard
negatives. Evaluation MUST report missing required pairs and, during verified evaluation,
forbidden confirmed pairs.

