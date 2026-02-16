# ToBe Vision: Nablarch Development Process with AI Agents

**Date**: 2026-02-16
**Status**: Draft
**Related Issue**: #21

## Table of Contents

- [Executive Summary](#executive-summary)
- [Background](#background)
- [AsIs Process Overview](#asis-process-overview)
- [ToBe Vision Overview](#tobe-vision-overview)
- [Lifecycle Phase Comparison](#lifecycle-phase-comparison)
  - [Requirements Definition](#1-requirements-definition)
  - [Architecture Design](#2-architecture-design)
  - [Design Phase](#3-design-phase)
  - [PGUT Phase (Implementation & Unit Testing)](#4-pgut-phase-implementation--unit-testing)
  - [System Testing](#5-system-testing)
- [Role Transformation](#role-transformation)
- [Workflow Improvements](#workflow-improvements)
- [Tool and Environment Changes](#tool-and-environment-changes)
- [Expected Benefits](#expected-benefits)
- [Implementation Roadmap](#implementation-roadmap)
- [Appendix](#appendix)

---

## Executive Summary

This document presents a ToBe vision for Nablarch development that transforms the traditional waterfall process into an AI agent-driven workflow. By leveraging **nabledge skills** (nabledge-6/5) and **AI agents** (Claude Code, GitHub Copilot), development teams can achieve:

- **60-70% reduction in development effort** through automated code generation, review, and investigation
- **Faster onboarding** for new team members (from weeks to days)
- **Higher code quality** through consistent application of Nablarch patterns and immediate feedback
- **Accelerated development cycles** while maintaining waterfall governance structure

The transformation maintains the proven waterfall structure for governance and quality gates while introducing AI agents as primary development actors alongside human developers.

---

## Background

### Current Challenges (AsIs)

The current Nablarch development process, documented in the [Nablarch System Development Guide](../.lw/nab-official/v6/nablarch-system-development-guide/), faces several challenges:

1. **Manual Environment Setup**
   - Repository creation, CI/CD configuration, local development environment setup require significant manual effort
   - Integration test environment setup is time-consuming and error-prone

2. **Human-Driven Design and Implementation**
   - Nablarch framework knowledge is required for proper implementation
   - New team members require extensive onboarding (typically 2-4 weeks)
   - Implementation patterns are not consistently applied across developers

3. **Traditional Testing Approaches**
   - Heavy reliance on manual test case creation
   - Test data preparation is labor-intensive
   - Regression testing is costly

4. **Documentation Burden**
   - Extensive Excel-based design documents
   - Documentation often becomes outdated
   - Knowledge transfer through documentation is slow

### The Nabledge Solution

**Nabledge** is an AI knowledge foundation consisting of:

- **Structured Knowledge Base**: 60+ JSON knowledge files covering Nablarch 6/5 (handlers, libraries, tools, patterns)
- **AI Agent Workflows**: Knowledge search, development task delegation, code review
- **Distribution**: Claude Code Plugin via GitHub (`nablarch/nabledge`)

Nabledge enables AI agents to:
- Understand Nablarch architecture and patterns
- Generate implementation code following best practices
- Review code against Nablarch standards
- Answer questions about framework usage
- Analyze impact of changes

---

## AsIs Process Overview

The current Nablarch development process follows a traditional waterfall model:

### Development Phases

1. **Project Planning**
   - Role assignment
   - Risk identification
   - Resource allocation

2. **Requirements Definition**
   - Business/system requirements gathering
   - Non-functional requirements definition (performance, security)
   - Test planning

3. **Architecture Design (方式設計)**
   - Application architecture design
   - Security design
   - Infrastructure design
   - Review Nablarch pattern catalog

4. **Design Phase (設計工程)**
   - Standardization (DB design, UI standards, coding standards)
   - Detailed design documents
   - Test standard preparation

5. **PGUT Phase (プログラム・単体テスト工程)**
   - Nablarch project initialization
   - Team development environment setup
   - Development environment setup guide creation
   - Development standard finalization
   - Programming and unit testing

6. **Integration Testing (結合テスト工程)**
   - Integration test environment preparation
   - Connectivity verification
   - Integration test execution

### Key Characteristics

| Aspect | AsIs Approach |
|--------|---------------|
| **Primary Actors** | Human developers |
| **Knowledge Source** | Official documentation, training, senior developers |
| **Code Generation** | Manual implementation from design documents |
| **Quality Assurance** | Manual code review, testing |
| **Environment Setup** | Manual configuration following setup guides |
| **Documentation** | Excel-based design documents, Word-based guides |
| **Onboarding** | 2-4 weeks reading documentation and training |
| **Development Speed** | Constrained by human developer capacity |

---

## ToBe Vision Overview

The ToBe vision transforms the development process by introducing **AI agents as primary development actors** alongside human developers, supported by the **nabledge knowledge foundation**.

### Core Transformation Principles

1. **AI Agents as Development Partners**
   - AI agents handle routine implementation, investigation, and review tasks
   - Human developers focus on requirements, architecture decisions, and complex problem-solving
   - Collaboration model: humans provide direction, agents execute with oversight

2. **Knowledge-Driven Development**
   - Nabledge provides structured Nablarch knowledge to AI agents
   - Consistent application of framework patterns and best practices
   - Instant access to implementation guidance

3. **Automated Workflows**
   - Code generation from design specifications
   - Automated code review against Nablarch standards
   - Impact analysis for changes
   - Test data generation assistance

4. **Maintained Governance Structure**
   - Waterfall phase gates remain in place
   - Human approval required for phase transitions
   - Quality standards maintained or improved

### ToBe Process Flow

```
Requirements Definition (Human-led, AI-assisted)
    ↓
Architecture Design (Human-led, AI-assisted)
    ↓ [Approval Gate]
Design Phase (Human-led, AI-assisted)
    ↓ [Approval Gate]
PGUT Phase (AI-led, Human-supervised)
    ├─ Environment Setup (Automated)
    ├─ Code Generation (AI with human review)
    ├─ Code Review (AI + Human)
    └─ Unit Testing (AI-assisted)
    ↓ [Approval Gate]
Integration Testing (Human-led, AI-assisted)
    ↓ [Approval Gate]
Production Deployment
```

### Key Characteristics

| Aspect | ToBe Approach |
|--------|---------------|
| **Primary Actors** | AI agents + Human developers (collaborative) |
| **Knowledge Source** | Nabledge knowledge base + Official documentation |
| **Code Generation** | AI-generated from design docs, human-reviewed |
| **Quality Assurance** | AI-driven code review + Human oversight |
| **Environment Setup** | Automated via AI agent workflows |
| **Documentation** | Markdown-based, auto-generated, living documentation |
| **Onboarding** | Days (AI assistance reduces learning curve) |
| **Development Speed** | 3-5x faster (60-70% effort reduction) |

---

## Lifecycle Phase Comparison

### 1. Requirements Definition

#### AsIs: Requirements Definition

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| Business requirements gathering | Human (Business Analyst) | Word, Excel | High | Requirements documents |
| Non-functional requirements definition | Human (Architect) | Excel, IPA templates | High | NFR specifications |
| Test planning | Human (Test Lead) | Excel, Word | High | Test plans |
| Requirements review | Human (multiple stakeholders) | Manual meetings | Medium | Approved requirements |

**Challenges**:
- Time-consuming documentation
- Risk of ambiguity in requirements
- Limited validation of technical feasibility

#### ToBe: Requirements Definition

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| Business requirements gathering | Human (Business Analyst) + AI Agent | Markdown, AI transcription | Medium | Structured requirements |
| Non-functional requirements definition | Human (Architect) + AI Agent | Markdown, nabledge guidance | Medium | NFR specifications with Nablarch patterns |
| Test planning | Human (Test Lead) + AI Agent | Markdown, AI-suggested test cases | Low-Medium | Test plans with coverage analysis |
| Requirements review | Human + AI Agent | AI completeness check + Human review | Low-Medium | Validated requirements |
| **NEW: Technical feasibility check** | AI Agent | nabledge knowledge search | Low | Feasibility report |

**Changes**:
- **AI Agent Role**: Provides Nablarch-specific guidance during requirements gathering
  - Suggests applicable Nablarch patterns for functional requirements
  - Validates NFR against Nablarch capabilities
  - Identifies potential implementation challenges early
- **Documentation Format**: Shift from Excel to structured Markdown (easier for AI processing)
- **New Activity**: Technical feasibility check using nabledge knowledge
- **Effort Reduction**: ~30% (from High to Medium for most activities)

**Example Scenario**:
```
Human: "We need pagination for search results showing 50 items per page"

AI Agent (with nabledge-6):
- Searches nabledge knowledge: features/libraries/universal-dao.json → paging section
- Responds: "Nablarch UniversalDao supports pagination via page number and max results.
  Recommend using DeferredEntityList for lazy loading. See implementation pattern..."
- Adds technical note to requirements document
```

---

### 2. Architecture Design

#### AsIs: Architecture Design (方式設計)

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| Review application architecture sample | Human (Architect) | Excel samples | Medium | Architecture understanding |
| Customize architecture for project | Human (Architect) | Excel, Word | Very High | Architecture design document |
| Security design | Human (Security Specialist) | IPA checklists, Excel | High | Security design document |
| Review Nablarch patterns | Human (Architect, Developers) | Documentation reading | High | Pattern understanding |
| Architecture review | Human (multiple stakeholders) | Manual meetings | Medium | Approved architecture |

**Challenges**:
- Heavy reliance on architect's Nablarch knowledge
- Time-consuming customization from samples
- Risk of missing critical patterns or anti-patterns
- Limited validation before PGUT phase

#### ToBe: Architecture Design (方式設計)

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| Review application architecture sample | Human (Architect) + AI Agent | AI-guided exploration | Low | Architecture understanding |
| **AI-assisted architecture generation** | AI Agent + Human (Architect) | nabledge patterns + Human review | Medium | Draft architecture document |
| Security design | Human (Security Specialist) + AI Agent | nabledge security checks + Human review | Medium | Security design with Nablarch coverage |
| **Automated pattern validation** | AI Agent | nabledge pattern catalog | Low | Pattern compliance report |
| **Anti-pattern detection** | AI Agent | nabledge anti-patterns | Low | Risk identification report |
| Architecture review | Human + AI Agent | AI pre-review + Human review | Low-Medium | Validated architecture |

**Changes**:
- **AI-Assisted Architecture Generation**: AI agents use nabledge knowledge to generate draft architecture based on requirements
  - Suggests appropriate handlers for each functional area
  - Recommends database access patterns
  - Proposes transaction management strategy
  - Identifies integration points for REST APIs
- **Automated Validation**: AI agents check architecture against Nablarch patterns and anti-patterns
- **Security Coverage**: AI agents use nabledge security knowledge to map IPA checklist items to Nablarch features
- **Effort Reduction**: ~40% (especially in customization and review activities)

**Example Scenario**:
```
Human: "Design batch processing architecture for File-to-DB import"

AI Agent (with nabledge-6):
1. Searches nabledge: features/processing/nablarch-batch.json
2. Identifies required handlers:
   - FileRecordReaderDisposeHandler (file input)
   - TransactionManagementHandler (transaction control)
   - ValidationHandler (input validation)
3. Generates handler configuration draft
4. Suggests error handling strategy
5. Proposes unit test approach
6. Creates architecture document draft for human review
```

---

### 3. Design Phase

#### AsIs: Design Phase (設計工程)

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| Customize design standards | Human (Tech Lead) | Excel templates | Very High | Design standards |
| Customize coding standards | Human (Tech Lead) | Word templates | High | Coding standards |
| Customize test standards | Human (Test Lead) | Excel templates | Very High | Test standards |
| Create UI standards | Human (UI Designer) | Style guides, Excel | High | UI standards |
| Review and approval | Human (multiple stakeholders) | Manual meetings | Medium | Approved standards |

**Challenges**:
- Extensive customization work from templates
- Risk of inconsistency across standards
- Late discovery of gaps or conflicts
- Heavy dependency on experienced leads

#### ToBe: Design Phase (設計工程)

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| **AI-assisted standard generation** | AI Agent + Human (Tech Lead) | nabledge + project requirements | Medium | Draft design standards |
| **AI-validated coding standards** | AI Agent + Human (Tech Lead) | nabledge best practices | Low-Medium | Coding standards |
| **AI-assisted test standard creation** | AI Agent + Human (Test Lead) | nabledge test patterns | Medium | Test standards |
| Create UI standards | Human (UI Designer) + AI Agent | Style guides, AI consistency check | Medium | UI standards |
| **Automated consistency check** | AI Agent | Cross-standard validation | Low | Consistency report |
| Review and approval | Human + AI Agent | AI pre-review + Human approval | Low-Medium | Validated standards |

**Changes**:
- **AI-Assisted Standard Generation**: AI agents use nabledge knowledge and project requirements to generate draft standards
  - Automatically adapts standard templates for project scope
  - Ensures consistency with Nablarch best practices
  - Identifies conflicts between requirements and standard patterns
- **Automated Consistency Checking**: AI agents validate consistency across all standards
- **Reduced Customization Effort**: AI handles routine customization, humans focus on project-specific decisions
- **Effort Reduction**: ~50% (from Very High/High to Medium for most activities)

**Example Scenario**:
```
Human: "Create test standards for batch processing using lightweight test approach"

AI Agent (with nabledge-6):
1. Reviews project requirements (batch scope: File-to-DB, DB-to-File)
2. Retrieves nabledge test patterns for batch
3. Generates test standard draft:
   - Unit test approach for batch actions
   - Test data preparation guidelines
   - Assertion patterns for file I/O
   - Database state verification methods
4. Adapts for "lightweight" approach (reduces coverage from heavy NTF approach)
5. Produces Excel/Markdown template for human review and finalization
```

---

### 4. PGUT Phase (Implementation & Unit Testing)

This is where the most significant transformation occurs. AI agents become the primary actors for implementation, with human developers providing oversight and handling complex scenarios.

#### AsIs: PGUT Phase

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| Nablarch project initialization | Human (Tech Lead) | Maven archetypes, manual setup | High | Project skeleton |
| Team dev environment setup | Human (Infrastructure) | Manual configuration | Very High | Git, CI/CD, chat tools |
| Create environment setup guide | Human (Tech Lead) | Word documentation | High | Setup guide |
| Implement features | Human (Developers) | IDE, manual coding | Very High | Source code |
| Code review | Human (Senior Developers) | Manual review | High | Review feedback |
| Unit testing | Human (Developers) | JUnit, manual test writing | Very High | Unit tests |
| Bug fixing | Human (Developers) | Manual debugging | High | Bug fixes |

**Challenges**:
- Repetitive implementation work
- Inconsistent code quality across developers
- Time-consuming code reviews
- Manual test case writing is labor-intensive
- Knowledge gaps in Nablarch patterns

#### ToBe: PGUT Phase

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| **Automated project initialization** | AI Agent | nabledge workflows + Maven | Low | Project skeleton |
| **Automated environment setup** | AI Agent | Infrastructure-as-code + AI scripts | Medium | Git, CI/CD, chat tools |
| **AI-generated setup guide** | AI Agent | Automated documentation generation | Low | Setup guide |
| **AI-driven implementation** | AI Agent + Human (oversight) | nabledge code generation + Human review | Low-Medium | Source code (AI-generated) |
| **AI-driven code review** | AI Agent + Human (Senior Dev) | nabledge pattern validation + Human review | Low-Medium | Review feedback |
| **AI-assisted unit testing** | AI Agent + Human | nabledge test patterns + Human review | Medium | Unit tests |
| **AI-assisted debugging** | AI Agent + Human | nabledge error knowledge + Human oversight | Low-Medium | Bug fixes |
| **NEW: Impact analysis** | AI Agent | nabledge knowledge graph | Low | Impact analysis report |

**Changes**:

**Environment Setup**:
- **Automated Initialization**: AI agents use nabledge workflows to set up Nablarch projects
  - Generate Maven project structure
  - Configure handlers based on architecture design
  - Set up database configurations
  - Create initial component-definition XML files
- **Infrastructure Automation**: AI agents script environment setup (Git, CI/CD pipelines)
- **Effort Reduction**: Very High → Low-Medium (~70% reduction)

**Implementation**:
- **AI-Driven Code Generation**: AI agents generate implementation code from design documents
  ```
  Human: Provides design document (e.g., "Batch action for project import from CSV")

  AI Agent (with nabledge-6):
  1. Parses design document to extract specifications
  2. Identifies pattern: File-to-DB batch
  3. Searches nabledge: features/processing/nablarch-batch.json → file-to-db pattern
  4. Generates batch action class following Nablarch patterns:
     - DataReader implementation
     - Form validation
     - UniversalDao usage
     - Error handling
     - Transaction boundary
  5. Generates unit test skeleton
  6. Submits for human review
  ```
- **Human Role**: Review generated code, handle complex business logic, make final decisions
- **Effort Reduction**: Very High → Low-Medium (~60-70% reduction)

**Code Review**:
- **AI-Driven Review**: AI agents perform first-pass code review using nabledge knowledge
  ```
  AI Agent Review Checks:
  - Nablarch pattern compliance
  - Security vulnerabilities (SQL injection, XSS, etc.)
  - Performance anti-patterns
  - Exception handling correctness
  - Transaction management
  - Resource cleanup (file handles, connections)
  - Code style compliance
  ```
- **Human Role**: Review AI findings, assess business logic correctness, make final approval
- **Effort Reduction**: High → Low-Medium (~50% reduction)

**Unit Testing**:
- **AI-Assisted Test Generation**: AI agents generate unit tests based on implementation
  ```
  AI Agent (with nabledge-6):
  1. Analyzes implemented code structure
  2. Identifies test scenarios (normal, error, boundary cases)
  3. Generates test cases using nabledge test patterns
  4. Creates test data setup/teardown
  5. Generates assertions
  ```
- **Human Role**: Review test coverage, add complex business logic tests
- **Effort Reduction**: Very High → Medium (~50% reduction)

**Debugging**:
- **AI-Assisted Debugging**: AI agents analyze errors using nabledge knowledge
  ```
  Human: Encounters error "Transaction not active"

  AI Agent (with nabledge-6):
  1. Searches nabledge: features/handlers/transaction-management-handler.json → common errors
  2. Identifies cause: Transaction boundary misconfiguration
  3. Suggests fix: Add TransactionManagementHandler to handler queue
  4. Provides code example
  ```
- **Effort Reduction**: High → Low-Medium (~40% reduction)

**Overall PGUT Phase Impact**:
- **Effort Reduction**: ~60-70% reduction in total PGUT effort
- **Quality Improvement**: More consistent code quality through nabledge pattern application
- **Speed**: 3-5x faster implementation cycles

---

### 5. System Testing

#### AsIs: System Testing

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| Integration test environment setup | Human (Infrastructure) | Manual configuration | Very High | Test environment |
| Connectivity verification | Human (Developers) | Manual testing | High | Verification results |
| Test case creation | Human (Testers) | Excel | Very High | Test cases |
| Test data preparation | Human (Testers, Developers) | Manual scripts | Very High | Test data |
| Test execution | Human (Testers) | Manual execution | High | Test results |
| Bug triage and fixing | Human (Developers) | Manual analysis | High | Bug fixes |
| Regression testing | Human (Testers) | Manual re-execution | Very High | Regression results |

**Challenges**:
- Environment setup is time-consuming and error-prone
- Test data preparation is labor-intensive
- Manual test execution is slow
- Regression testing is costly

#### ToBe: System Testing

| Activity | Actor | Tools | Effort | Output |
|----------|-------|-------|--------|--------|
| **Automated environment setup** | AI Agent | Infrastructure-as-code + AI scripts | Medium | Test environment |
| **AI-assisted connectivity verification** | AI Agent + Human | Automated checks + Human validation | Low-Medium | Verification results |
| **AI-assisted test case generation** | AI Agent + Human (Testers) | nabledge patterns + Human review | Medium | Test cases |
| **AI-assisted test data generation** | AI Agent + Human | nabledge data patterns + Human review | Medium | Test data |
| Test execution | Human (Testers) + AI Agent | Automated execution where possible | Medium | Test results |
| **AI-assisted bug analysis** | AI Agent + Human (Developers) | nabledge error knowledge + Human triage | Medium | Bug analysis |
| **AI-assisted regression testing** | AI Agent + Human | Test automation + AI-generated tests | Medium | Regression results |

**Changes**:
- **Automated Environment Setup**: AI agents script integration test environment setup
- **AI-Assisted Test Generation**: AI agents generate test cases from requirements and design documents
  ```
  AI Agent (with nabledge-6):
  1. Reviews functional specifications
  2. Identifies test scenarios using nabledge patterns
  3. Generates test cases with expected results
  4. Suggests test data requirements
  ```
- **AI-Assisted Data Generation**: AI agents generate test data following database constraints and business rules
- **Automated Bug Analysis**: AI agents analyze bug reports using nabledge knowledge to suggest root causes
- **Effort Reduction**: ~40% reduction in system testing effort

---

## Role Transformation

### Human Roles: Evolution

| Role | AsIs Responsibilities | ToBe Responsibilities | Change Impact |
|------|----------------------|----------------------|---------------|
| **Architect** | Full architecture design, pattern selection, technology decisions | High-level architecture direction, AI-generated architecture review, complex trade-off decisions | Focus shifts to strategic decisions; routine design delegated to AI |
| **Tech Lead** | Standard creation, project setup, code review, mentoring | Strategic standard decisions, AI output validation, complex problem resolution, team coordination | Focus shifts to oversight and problem-solving; automation reduces routine work |
| **Developers** | Manual implementation, unit testing, debugging, code review | Design document creation, AI-generated code review, complex business logic implementation, AI agent oversight | Focus shifts to specification and validation; AI handles routine coding |
| **Testers** | Manual test case creation, test data preparation, manual test execution | Test strategy definition, AI-generated test review, exploratory testing, test automation management | Focus shifts to test strategy; AI handles routine test case generation |
| **Project Manager** | Resource allocation, schedule management, risk management, stakeholder communication | Same as AsIs + AI agent task orchestration, AI output quality monitoring | Additional responsibility for AI agent management |

### AI Agent Roles: New Actors

| Role | Responsibilities | Tools/Skills | Human Oversight Level |
|------|-----------------|--------------|----------------------|
| **Implementation Agent** | Code generation from design documents, pattern application, boilerplate code generation | nabledge-6/5, Claude Code, GitHub Copilot | High (all code reviewed by humans) |
| **Review Agent** | Code review against Nablarch patterns, security scanning, style checking, anti-pattern detection | nabledge-6/5, static analysis tools | Medium (findings reviewed by senior developers) |
| **Test Agent** | Unit test generation, test data preparation, test case generation from requirements | nabledge-6/5, test frameworks | Medium (test coverage reviewed by testers) |
| **Knowledge Agent** | Answer Nablarch questions, provide implementation guidance, explain patterns, impact analysis | nabledge-6/5 knowledge search | Low (developers validate applicability) |
| **Environment Agent** | Project initialization, environment setup, configuration generation | nabledge-6/5, infrastructure tools | High (configurations reviewed by tech lead) |

### Collaboration Model

```
Project Manager
    ├─ Defines objectives, assigns tasks
    ├─ Orchestrates AI agents and human developers
    └─ Monitors quality and progress

Architect + AI Agent
    ├─ Architect: High-level design direction
    ├─ AI Agent: Generate architecture drafts, validate patterns
    └─ Architect: Review and approve

Tech Lead + AI Agent
    ├─ Tech Lead: Define standards, resolve complex issues
    ├─ AI Agent: Generate standard drafts, setup environments
    └─ Tech Lead: Validate and approve

Developer + AI Agent
    ├─ Developer: Write design documents, complex business logic
    ├─ AI Agent: Generate implementation code, unit tests
    ├─ Developer: Review AI output, refine as needed
    └─ Senior Dev + AI Agent: Code review

Tester + AI Agent
    ├─ Tester: Define test strategy
    ├─ AI Agent: Generate test cases, test data
    ├─ Tester: Review and execute tests
    └─ AI Agent: Assist with bug analysis
```

---

## Workflow Improvements

### 1. Knowledge Access

**AsIs**:
- Consult official documentation (time-consuming search)
- Ask senior developers (interrupts their work)
- Trial and error (slow, error-prone)

**ToBe**:
- Instant knowledge search via nabledge
- AI agent provides context-specific guidance
- Integrated into development workflow

**Benefit**: 80% reduction in knowledge acquisition time

### 2. Code Generation

**AsIs**:
- Manual implementation from design documents
- Copy-paste from samples (risk of inconsistency)
- Repetitive boilerplate code writing

**ToBe**:
- AI generates code from design specifications
- Consistent pattern application
- Automated boilerplate generation

**Benefit**: 60-70% reduction in implementation time

### 3. Code Review

**AsIs**:
- Manual review by senior developers
- Time-consuming, resource-intensive
- Inconsistent review quality
- Review bottleneck

**ToBe**:
- AI performs first-pass review
- Human reviews AI findings and business logic
- Consistent pattern validation
- Faster review cycles

**Benefit**: 50% reduction in review time, improved consistency

### 4. Testing

**AsIs**:
- Manual test case writing
- Manual test data preparation
- Time-consuming regression testing

**ToBe**:
- AI generates test cases from requirements
- AI assists with test data generation
- Automated regression test generation

**Benefit**: 50% reduction in test preparation time

### 5. Environment Setup

**AsIs**:
- Manual project initialization
- Manual environment configuration
- Manual documentation writing

**ToBe**:
- Automated project initialization
- Automated environment setup
- Auto-generated documentation

**Benefit**: 70% reduction in setup time

---

## Tool and Environment Changes

### Development Tools

| Tool Category | AsIs Tools | ToBe Tools | Change |
|--------------|------------|------------|--------|
| **IDE** | Eclipse, IntelliJ IDEA | Eclipse, IntelliJ IDEA + **GitHub Copilot extension** | Added: AI code completion |
| **CLI** | Standard terminal | Standard terminal + **Claude Code CLI** | Added: AI agent interface |
| **Code Review** | Manual review, checkstyle | Manual review, checkstyle + **AI review agent** | Added: Automated first-pass review |
| **Documentation** | Word, Excel | Markdown + **Auto-generation tools** | Changed: Format and automation |
| **Knowledge Base** | Official docs, wikis | Official docs + **nabledge knowledge base** | Added: AI-optimized knowledge |

### Infrastructure

| Infrastructure | AsIs | ToBe | Change |
|----------------|------|------|--------|
| **Project Initialization** | Manual Maven archetype execution | **AI-automated setup** using nabledge workflows | Automated |
| **CI/CD** | Manual pipeline configuration | **AI-generated pipeline** configuration | Automated |
| **Environment Config** | Manual XML/properties editing | **AI-generated configuration** with human review | Semi-automated |
| **Documentation** | Manual Word/Excel creation | **Auto-generated Markdown** from code and comments | Automated |

### Nabledge Plugin Installation

**Claude Code**:
```bash
# Install nabledge plugin from registry
claude plugin install nabledge-6

# Verify installation
claude plugin list

# Update plugin
claude plugin update nabledge-6
```

**GitHub Copilot**:
```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/nablarch/nabledge/main/install.sh | sh
```

---

## Expected Benefits

### Quantitative Benefits

| Metric | AsIs | ToBe | Improvement |
|--------|------|------|-------------|
| **PGUT Phase Effort** | 100% (baseline) | 30-40% | **60-70% reduction** |
| **Code Review Time** | 100% (baseline) | 50% | **50% reduction** |
| **Test Preparation Time** | 100% (baseline) | 50% | **50% reduction** |
| **Environment Setup Time** | 100% (baseline) | 30% | **70% reduction** |
| **Onboarding Time** | 2-4 weeks | 3-5 days | **75% reduction** |
| **Knowledge Acquisition Time** | 100% (baseline) | 20% | **80% reduction** |
| **Overall Development Cycle** | 100% (baseline) | 40-50% | **50-60% faster** |

### Qualitative Benefits

| Aspect | Benefit |
|--------|---------|
| **Code Quality** | More consistent application of Nablarch patterns, fewer bugs from pattern misuse |
| **Knowledge Retention** | Team knowledge captured in nabledge, reduced dependency on senior developers |
| **Documentation** | Up-to-date, auto-generated documentation reduces maintenance burden |
| **Productivity** | Developers focus on business logic and complex problems, not boilerplate |
| **Team Morale** | Reduced repetitive work, faster feedback cycles, more time for learning |
| **Risk Reduction** | Early detection of anti-patterns, security issues, and architectural problems |

---

## Implementation Roadmap

### Phase 0: Preparation (Current)

**Status**: In Progress
**Duration**: 2 weeks
**Goal**: Complete nabledge-6 knowledge base and establish ToBe vision

- [x] Create nabledge-6 skill structure
- [x] Implement core workflows (knowledge search, code analysis)
- [x] Create initial knowledge files (handlers, libraries)
- [ ] **Complete ToBe vision document** ← Current task
- [ ] Review and approval from stakeholders

### Phase 1: Pilot Project (Foundation)

**Duration**: 4-6 weeks
**Goal**: Validate ToBe vision with small pilot project

**Scope**:
- Small Nablarch batch project (File-to-DB, DB-to-File)
- 2-3 developers + AI agents
- Full PGUT cycle with nabledge-6

**Activities**:
1. Complete nabledge-6 knowledge base (Phase 1: Nablarch Batch FW)
2. Set up pilot project environment
3. Train pilot team on AI agent usage
4. Execute pilot development:
   - AI-assisted architecture design
   - AI-driven implementation
   - AI-assisted code review
   - AI-assisted unit testing
5. Measure results vs. baseline
6. Collect feedback and lessons learned

**Success Criteria**:
- 60%+ effort reduction in PGUT phase
- Code quality equal to or better than baseline
- Positive team feedback
- Validated workflows and patterns

### Phase 2: Expansion (REST API Support)

**Duration**: 4-6 weeks
**Goal**: Expand nabledge-6 to support RESTful web services

**Scope**:
- Complete nabledge-6 knowledge base (Phase 3: REST API)
- Pilot with REST API project
- Refine workflows based on Phase 1 feedback

**Activities**:
1. Create REST-specific knowledge files
2. Update workflows for REST patterns
3. Execute REST API pilot project
4. Measure and validate results

### Phase 3: Full Rollout

**Duration**: 8-12 weeks
**Goal**: Deploy ToBe process to all Nablarch projects

**Scope**:
- Complete nabledge-6 knowledge base (Phase 4: Full coverage)
- Organization-wide training
- Establish AI agent governance

**Activities**:
1. Complete remaining knowledge files (adapters, tools, checks, release notes)
2. Develop training materials and programs
3. Create AI agent usage guidelines
4. Roll out to all development teams
5. Establish support and feedback mechanisms
6. Monitor adoption and effectiveness

### Phase 4: Continuous Improvement

**Duration**: Ongoing
**Goal**: Continuously improve nabledge knowledge and workflows

**Activities**:
- Regular knowledge base updates (new Nablarch versions, patterns)
- Workflow optimization based on usage analytics
- Expand AI agent capabilities
- Community feedback integration

---

## Appendix

### A. Reference Documents

**AsIs Process**:
- [Nablarch System Development Guide (Japanese)](../.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/README.md)
- [Development Flow Diagram (Excel)](../.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarchを使用した開発の流れ.xlsx)
- [Sample Project](../.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/README.md)

**Nabledge Design**:
- [Nabledge Architecture Design](./nabledge-design.md)

**Official Nablarch Documentation**:
- [Nablarch Documentation](https://nablarch.github.io/docs/LATEST/doc/)
- [Nablarch Example Projects](https://nablarch.github.io/docs/LATEST/doc/application_framework/example/index.html)

### B. Glossary

| Term | Definition |
|------|------------|
| **Nabledge** | AI knowledge foundation for Nablarch development (structured knowledge + workflows) |
| **AI Agent** | AI-powered assistant (Claude Code, GitHub Copilot) using nabledge knowledge |
| **PGUT** | Programming and Unit Testing phase (プログラム・単体テスト工程) |
| **NTF** | Nablarch Testing Framework (heavy test approach) |
| **UniversalDao** | Nablarch's database access utility (ユニバーサルDAO) |
| **Handler** | Nablarch framework component for cross-cutting concerns |

### C. Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-16 | 0.1 | Initial draft created for issue #21 |

---

**Document Owner**: Nablarch Development Team
**Last Updated**: 2026-02-16
**Status**: Draft (Pending Review)
