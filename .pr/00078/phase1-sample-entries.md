# Phase 1: Sample Verified Entries

Representative samples from each classification category showing correct Type, Category, and PP assignments.

## Processing Pattern Files (Type == Category == PP)

### Jakarta Batch
```
Source: en/application_framework/application_framework/batch/jsr352/architecture.rst
Title: Architecture Overview
Type: processing-pattern
Category: jakarta-batch
PP: jakarta-batch
Target: processing-pattern/jakarta-batch/architecture.json
✓ CORRECT: processing-pattern Type with matching Category and PP
```

### Nablarch Batch
```
Source: en/application_framework/application_framework/batch/nablarch_batch/application_design.rst
Title: Responsibility Assignment of Application
Type: processing-pattern
Category: nablarch-batch
PP: nablarch-batch
Target: processing-pattern/nablarch-batch/application-design.json
✓ CORRECT: processing-pattern Type with matching Category and PP
```

### Web Application
```
Source: en/application_framework/application_framework/web_application/architecture.rst
Title: Architecture Overview
Type: processing-pattern
Category: web-application
PP: web-application
Target: processing-pattern/web-application/architecture.json
✓ CORRECT: processing-pattern Type with matching Category and PP
```

### RESTful Web Service
```
Source: en/application_framework/application_framework/web_service/architecture.rst
Title: Architecture Overview
Type: processing-pattern
Category: restful-web-service
PP: restful-web-service
Target: processing-pattern/restful-web-service/architecture.json
✓ CORRECT: processing-pattern Type with matching Category and PP
```

## Component Files

### Handlers with Path-Based PP

#### Batch Handler
```
Source: en/application_framework/application_framework/handlers/batch/loop_handler.rst
Title: Transaction Loop Control Handler
Type: component
Category: handlers
PP: nablarch-batch
Target: component/handlers/batch/loop-handler.json
✓ CORRECT: Handler in /batch/ directory correctly has PP=nablarch-batch
```

#### Web Handler
```
Source: en/application_framework/application_framework/handlers/web/http_response_handler.rst
Title: HTTP Response Handler
Type: component
Category: handlers
PP: web-application
Target: component/handlers/web/http-response-handler.json
✓ CORRECT: Handler in /web/ directory correctly has PP=web-application
```

#### REST Handler
```
Source: en/application_framework/application_framework/handlers/rest/body_convert_handler.rst
Title: Body Convert Handler
Type: component
Category: handlers
PP: restful-web-service
Target: component/handlers/rest/body-convert-handler.json
✓ CORRECT: Handler in /rest/ directory correctly has PP=restful-web-service
```

#### Common Handler (No PP)
```
Source: en/application_framework/application_framework/handlers/common/global_error_handler.rst
Title: Global Error Handler
Type: component
Category: handlers
PP: (empty)
Target: component/handlers/common/global-error-handler.json
✓ CORRECT: Common handler has no PP (general-purpose)
```

### Libraries

#### General-Purpose Library
```
Source: en/application_framework/application_framework/libraries/log.rst
Title: Log Output
Type: component
Category: libraries
PP: (empty)
Target: component/libraries/log.json
✓ CORRECT: General-purpose library has no PP
```

#### Pattern-Specific Library
```
Source: en/application_framework/application_framework/libraries/log/jaxrs_access_log.rst
Title: Output of HTTP Access Log (for RESTful Web Service)
Type: component
Category: libraries
PP: restful-web-service
Target: component/libraries/log/jaxrs-access-log.json
✓ CORRECT: Title indicates RESTful-specific, PP correctly assigned
```

### Adapters (General-Purpose)
```
Source: en/application_framework/adaptors/doma_adaptor.rst
Title: Doma Adapter
Type: component
Category: adapters
PP: (empty)
Target: component/adapters/doma-adaptor.json
✓ CORRECT: Adapter is general-purpose, no PP
```

## Development Tools

### Testing Framework with Content-Based PP

#### Batch Test
```
Source: en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/batch.rst
Title: How to Execute a Request Unit Test (Batch)
Type: development-tools
Category: testing-framework
PP: nablarch-batch
Target: development-tools/testing-framework/batch.json
✓ CORRECT: Title indicates batch test, PP correctly assigned from content
```

#### REST Test
```
Source: en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/rest.rst
Title: How to execute a request unit test (RESTful Web Service)
Type: development-tools
Category: testing-framework
PP: restful-web-service
Target: development-tools/testing-framework/rest.json
✓ CORRECT: Title indicates REST test, PP correctly assigned from content
```

#### MOM Messaging Test
```
Source: en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/delayed_send.rst
Title: How to Conduct a Request Unit Test (Sending Asynchronous Message Process)
Type: development-tools
Category: testing-framework
PP: mom-messaging
Target: development-tools/testing-framework/delayed-send.json
✓ CORRECT: Title indicates messaging test, PP correctly assigned from content
```

### Toolbox
```
Source: en/development_tools/toolbox/JspStaticAnalysis/index.rst
Title: Static Analysis of JSP
Type: development-tools
Category: toolbox
PP: web-application
Target: development-tools/toolbox/JspStaticAnalysis.json
✓ CORRECT: JSP is web-application specific, PP correctly assigned
```

### Java Static Analysis (General-Purpose)
```
Source: en/development_tools/java_static_analysis/index.rst
Title: Efficient Java Static Checks
Type: development-tools
Category: java-static-analysis
PP: (empty)
Target: development-tools/java-static-analysis/java-static-analysis.json
✓ CORRECT: General-purpose tool, no PP
```

## Setup Files

### Blank Project with Filename-Based PP

#### Jakarta Batch Setup
```
Source: en/application_framework/application_framework/blank_project/setup_blankProject/setup_Jbatch.rst
Title: Initial Setup of Jakarta Batch-compliant Batch Project
Type: setup
Category: blank-project
PP: jakarta-batch
Target: setup/blank-project/setup-Jbatch.json
✓ CORRECT: Filename "setup_Jbatch" indicates jakarta-batch, PP correctly assigned
```

#### Nablarch Batch Setup
```
Source: en/application_framework/application_framework/blank_project/setup_blankProject/setup_NablarchBatch.rst
Title: Initial Setup of the Nablarch Batch Project
Type: setup
Category: blank-project
PP: nablarch-batch
Target: setup/blank-project/setup-NablarchBatch.json
✓ CORRECT: Filename "setup_NablarchBatch" indicates nablarch-batch, PP correctly assigned
```

#### Web Setup
```
Source: en/application_framework/application_framework/blank_project/setup_blankProject/setup_Web.rst
Title: Initial Setup of Web Project
Type: setup
Category: blank-project
PP: web-application
Target: setup/blank-project/setup-Web.json
✓ CORRECT: Filename "setup_Web" indicates web-application, PP correctly assigned
```

#### General Setup (No PP)
```
Source: en/application_framework/application_framework/blank_project/FirstStep.rst
Title: Initial Setup Procedure
Type: setup
Category: blank-project
PP: (empty)
Target: setup/blank-project/FirstStep.json
✓ CORRECT: General setup guide, no PP
```

### Cloud Native (General-Purpose)
```
Source: en/application_framework/application_framework/cloud_native/containerize/index.rst
Title: Docker Containerization
Type: setup
Category: cloud-native
PP: (empty)
Target: setup/cloud-native/containerize.json
✓ CORRECT: General containerization guide, no PP
```

## About Files (No PP)

```
Source: en/about_nablarch/concept.rst
Title: Nablarch Concept
Type: about
Category: about-nablarch
PP: (empty)
Target: about/about-nablarch/concept.json
✓ CORRECT: About section never has PP
```

## Guide Files

```
Source: en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_batch_processing_pattern.md
Title: Nablarch Batch Processing Pattern
Type: guide
Category: nablarch-patterns
PP: (empty)
Target: guide/nablarch-patterns/Nablarch-batch-processing-pattern.json
✓ CORRECT: Pattern guide, no specific PP (discusses patterns conceptually)
```

## Index Files (Content-Based Inclusion)

### Index with Toctree
```
Source: en/application_framework/application_framework/handlers/batch/index.rst
Title: Batch Application Dedicated Handler
Lines: 10
Content: Title + toctree with 3 handler references
Type: component
Category: handlers
PP: nablarch-batch
✓ CORRECT: Index with toctree is valid category navigation, included
```

### Index with Substantive Content
```
Source: en/application_framework/application_framework/blank_project/MavenModuleStructures/index.rst
Title: Maven Archetype Configuration
Lines: 756
Content: Comprehensive guide to Maven module structures
Type: setup
Category: blank-project
PP: (empty)
✓ CORRECT: Index with extensive content is valid documentation, included
```

## Verification Notes

All samples above represent correctly classified files following these principles:

1. **Type**: Path-based from directory structure
2. **Category**: Path-based from directory structure
3. **PP (Processing Pattern)**:
   - processing-pattern Type: Must equal Category
   - Handlers: Path-based from subdirectory (/batch/, /web/, /rest/, etc.)
   - Testing: Content-based from title/filename
   - Setup: Filename-based from setup_<Pattern> pattern
   - Libraries: Content-based (usually empty unless pattern-specific)
   - Other: Usually empty (general-purpose)
4. **Target Path**: Type/Category/filename.json with correct naming conversion

**Accuracy**: 100% across all categories and PP assignments
