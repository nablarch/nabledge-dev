# Verification Checklist: mapping-v6.md

**Generated**: 2026-02-20
**Total Mapping Rows**: 270
**Classification Checks**: 93
**Target Path Checks**: 123

---

## Classification Verification

For each row, read the RST source file and verify:
1. Type matches the content scope
2. Category correctly categorizes the technical area
3. Processing Pattern is assigned appropriately

| # | Source Path | Type | Category | PP | Check Reason | Judgment |
|---|---|---|---|---|---|---|
| 1 | Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx | check | security-check |  | sampling | |
| 4 | about_nablarch/license.rst | about | about-nablarch |  | sampling | |
| 7 | application_framework/adaptors/doma_adaptor.rst | component | adapters |  | sampling | |
| 10 | application_framework/adaptors/jsr310_adaptor.rst | component | adapters |  | sampling | |
| 13 | application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst | component | adapters |  | sampling | |
| 16 | application_framework/adaptors/mail_sender_thymeleaf_adaptor.rst | component | adapters |  | sampling | |
| 19 | application_framework/adaptors/router_adaptor.rst | component | adapters |  | sampling | |
| 22 | application_framework/adaptors/webspheremq_adaptor.rst | component | adapters |  | sampling | |
| 25 | application_framework/application_framework/batch/jsr352/application_design.rst | processing-pattern | jakarta-batch | jakarta-batch | sampling | |
| 28 | application_framework/application_framework/batch/jsr352/feature_details/database_reader.rst | processing-pattern | jakarta-batch | jakarta-batch | sampling | |
| 31 | application_framework/application_framework/batch/jsr352/feature_details/pessimistic_lock.rst | processing-pattern | jakarta-batch | jakarta-batch | sampling | |
| 34 | application_framework/application_framework/batch/jsr352/getting_started/batchlet/index.rst | processing-pattern | jakarta-batch | jakarta-batch | sampling | |
| 37 | application_framework/application_framework/batch/jsr352/index.rst | processing-pattern | jakarta-batch | jakarta-batch | sampling | |
| 40 | application_framework/application_framework/batch/nablarch_batch/feature_details.rst | processing-pattern | nablarch-batch | nablarch-batch | sampling | |
| 43 | application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_pessimistic_lock.rst | processing-pattern | nablarch-batch | nablarch-batch | sampling | |
| 46 | application_framework/application_framework/batch/nablarch_batch/getting_started/nablarch_batch/index.rst | processing-pattern | nablarch-batch | nablarch-batch | sampling | |
| 49 | application_framework/application_framework/blank_project/FirstStep.rst | setup | blank-project |  | sampling | |
| 52 | application_framework/application_framework/blank_project/ModifySettings.rst | setup | blank-project |  | sampling | |
| 55 | application_framework/application_framework/blank_project/firstStep_appendix/ResiBatchReboot.rst | setup | blank-project |  | sampling | |
| 58 | application_framework/application_framework/blank_project/maven.rst | setup | blank-project |  | sampling | |
| 61 | application_framework/application_framework/blank_project/setup_blankProject/setup_NablarchBatch.rst | setup | blank-project | nablarch-batch | sampling | |
| 64 | application_framework/application_framework/blank_project/setup_blankProject/setup_WebService.rst | setup | blank-project | restful-web-service | sampling | |
| 67 | application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWeb.rst | setup | blank-project | web-application | sampling | |
| 70 | application_framework/application_framework/cloud_native/distributed_tracing/aws_distributed_tracing.rst | setup | cloud-native |  | sampling | |
| 73 | application_framework/application_framework/cloud_native/index.rst | setup | cloud-native |  | sampling | |
| 76 | application_framework/application_framework/handlers/batch/index.rst | processing-pattern | nablarch-batch | nablarch-batch | sampling | |
| 79 | application_framework/application_framework/handlers/common/ServiceAvailabilityCheckHandler.rst | component | handlers |  | sampling | |
| 82 | application_framework/application_framework/handlers/common/global_error_handler.rst | component | handlers |  | sampling | |
| 85 | application_framework/application_framework/handlers/common/request_handler_entry.rst | component | handlers |  | sampling | |
| 88 | application_framework/application_framework/handlers/common/thread_context_handler.rst | component | handlers |  | sampling | |
| 91 | application_framework/application_framework/handlers/http_messaging/http_messaging_request_parsing_handler.rst | component | handlers | http-messaging | sampling | |
| 94 | application_framework/application_framework/handlers/mom_messaging/index.rst | component | handlers | mom-messaging | sampling | |
| 97 | application_framework/application_framework/handlers/mom_messaging/messaging_context_handler.rst | component | handlers | mom-messaging | sampling | |
| 100 | application_framework/application_framework/handlers/rest/index.rst | component | handlers | restful-web-service | sampling | |
| 103 | application_framework/application_framework/handlers/rest/jaxrs_response_handler.rst | component | handlers | restful-web-service | sampling | |
| 104 | application_framework/application_framework/handlers/standalone/data_read_handler.rst | component | handlers | nablarch-batch | standalone handler (needs content verification) | |
| 105 | application_framework/application_framework/handlers/standalone/duplicate_process_check_handler.rst | component | handlers | nablarch-batch | standalone handler (needs content verification) | |
| 106 | application_framework/application_framework/handlers/standalone/multi_thread_execution_handler.rst | component | handlers | nablarch-batch | standalone handler (needs content verification) | |
| 107 | application_framework/application_framework/handlers/standalone/process_stop_handler.rst | component | handlers | nablarch-batch | standalone handler (needs content verification) | |
| 109 | application_framework/application_framework/handlers/web/SessionStoreHandler.rst | component | handlers | web-application | sampling | |
| 112 | application_framework/application_framework/handlers/web/health_check_endpoint_handler.rst | component | handlers | web-application | sampling | |
| 115 | application_framework/application_framework/handlers/web/http_character_encoding_handler.rst | component | handlers | web-application | sampling | |
| 118 | application_framework/application_framework/handlers/web/http_rewrite_handler.rst | component | handlers | web-application | sampling | |
| 121 | application_framework/application_framework/handlers/web/multipart_handler.rst | component | handlers | web-application | sampling | |
| 124 | application_framework/application_framework/handlers/web/post_resubmit_prevent_handler.rst | component | handlers | web-application | sampling | |
| 127 | application_framework/application_framework/handlers/web/session_concurrent_access_handler.rst | component | handlers | web-application | sampling | |
| 130 | application_framework/application_framework/libraries/bean_util.rst | component | libraries |  | sampling | |
| 133 | application_framework/application_framework/libraries/data_io/data_bind.rst | component | libraries |  | sampling | |
| 136 | application_framework/application_framework/libraries/data_io/data_format/multi_format_example.rst | component | libraries |  | sampling | |
| 139 | application_framework/application_framework/libraries/database/functional_comparison.rst | component | libraries |  | sampling | |
| 142 | application_framework/application_framework/libraries/database_management.rst | component | libraries |  | sampling | |
| 145 | application_framework/application_framework/libraries/exclusive_control.rst | component | libraries |  | sampling | |
| 148 | application_framework/application_framework/libraries/index.rst | component | libraries |  | sampling | |
| 151 | application_framework/application_framework/libraries/log/http_access_log.rst | component | libraries |  | sampling | |
| 154 | application_framework/application_framework/libraries/log/performance_log.rst | component | libraries |  | sampling | |
| 157 | application_framework/application_framework/libraries/message.rst | component | libraries |  | sampling | |
| 160 | application_framework/application_framework/libraries/service_availability.rst | component | libraries |  | sampling | |
| 163 | application_framework/application_framework/libraries/session_store/update_example.rst | component | libraries |  | sampling | |
| 166 | application_framework/application_framework/libraries/system_messaging.rst | component | libraries |  | sampling | |
| 169 | application_framework/application_framework/libraries/tag.rst | component | libraries |  | sampling | |
| 172 | application_framework/application_framework/libraries/utility.rst | component | libraries |  | sampling | |
| 175 | application_framework/application_framework/libraries/validation/functional_comparison.rst | component | libraries |  | sampling | |
| 178 | application_framework/application_framework/messaging/db/architecture.rst | processing-pattern | db-messaging | db-messaging | sampling | |
| 181 | application_framework/application_framework/messaging/db/feature_details/multiple_process.rst | processing-pattern | db-messaging | db-messaging | sampling | |
| 184 | application_framework/application_framework/messaging/db/index.rst | processing-pattern | db-messaging | db-messaging | sampling | |
| 187 | application_framework/application_framework/messaging/mom/feature_details.rst | processing-pattern | mom-messaging | mom-messaging | sampling | |
| 190 | application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeAvailableCharacters.rst | setup | setting-guide |  | sampling | |
| 193 | application_framework/application_framework/setting_guide/CustomizingConfigurations/config_key_naming.rst | setup | setting-guide |  | sampling | |
| 196 | application_framework/application_framework/setting_guide/index.rst | setup | setting-guide |  | sampling | |
| 199 | application_framework/application_framework/web_service/http_messaging/architecture.rst | processing-pattern | restful-web-service | restful-web-service | sampling | |
| 202 | application_framework/application_framework/web_service/http_messaging/getting_started/save/index.rst | processing-pattern | restful-web-service | restful-web-service | sampling | |
| 205 | application_framework/application_framework/web_service/rest/application_design.rst | processing-pattern | restful-web-service | restful-web-service | sampling | |
| 208 | application_framework/application_framework/web_service/rest/feature_details/resource_signature.rst | processing-pattern | restful-web-service | restful-web-service | sampling | |
| 211 | application_framework/application_framework/web_service/rest/getting_started/search/index.rst | processing-pattern | restful-web-service | restful-web-service | sampling | |
| 214 | development_tools/java_static_analysis/index.rst | development-tools | java-static-analysis |  | sampling | |
| 217 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/index.rst | development-tools | testing-framework |  | sampling | |
| 220 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/batch.rst | development-tools | testing-framework |  | sampling | |
| 223 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/duplicate_form_submission.rst | development-tools | testing-framework |  | sampling | |
| 226 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/http_send_sync.rst | development-tools | testing-framework |  | sampling | |
| 229 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/real.rst | development-tools | testing-framework |  | sampling | |
| 232 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/batch.rst | development-tools | testing-framework |  | sampling | |
| 235 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/http_send_sync.rst | development-tools | testing-framework |  | sampling | |
| 238 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/rest.rst | development-tools | testing-framework |  | sampling | |
| 241 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/01_Abstract.rst | development-tools | testing-framework |  | sampling | |
| 244 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/03_Tips.rst | development-tools | testing-framework |  | sampling | |
| 247 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_batch.rst | development-tools | testing-framework |  | sampling | |
| 250 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_rest.rst | development-tools | testing-framework |  | sampling | |
| 253 | development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/01_HttpDumpTool.rst | development-tools | testing-framework |  | sampling | |
| 256 | development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/01_MasterDataSetupTool.rst | development-tools | testing-framework |  | sampling | |
| 259 | development_tools/testing_framework/guide/development_guide/08_TestTools/03_HtmlCheckTool/index.rst | development-tools | testing-framework |  | sampling | |
| 262 | development_tools/toolbox/JspStaticAnalysis/01_JspStaticAnalysis.rst | development-tools | toolbox |  | sampling | |
| 265 | development_tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.rst | development-tools | toolbox |  | sampling | |
| 268 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md | guide | nablarch-patterns |  | sampling | |

**Instructions**:
- Read the first 50 lines of the RST file at `{source_dir}/{source_path}`
- Check if classification matches the content
- Mark ✓ if correct, ✗ if incorrect (note correct classification)

---

## Target Path Verification

For each row, verify:
1. Target path starts with Type
2. Filename correctly converts `_` to `-`
3. Extension changed from `.rst` to `.md`
4. Subdirectories preserved where appropriate

| # | Source Path | Target Path | Check Reason | Judgment |
|---|---|---|---|---|
| 1 | Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx | check/security-check/Nablarch機能のセキュリティ対応表.xlsx | sampling | |
| 3 | about_nablarch/index.rst | about/about-nablarch/about-nablarch.md | index.rst naming | |
| 4 | about_nablarch/license.rst | about/about-nablarch/license.md | sampling | |
| 7 | application_framework/adaptors/doma_adaptor.rst | component/adapters/doma-adaptor.md | sampling | |
| 8 | application_framework/adaptors/index.rst | component/adapters/adaptors.md | index.rst naming | |
| 10 | application_framework/adaptors/jsr310_adaptor.rst | component/adapters/jsr310-adaptor.md | sampling | |
| 13 | application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst | component/adapters/lettuce_adaptor/redisstore-lettuce-adaptor.md | sampling | |
| 16 | application_framework/adaptors/mail_sender_thymeleaf_adaptor.rst | component/adapters/mail-sender-thymeleaf-adaptor.md | sampling | |
| 19 | application_framework/adaptors/router_adaptor.rst | component/adapters/router-adaptor.md | sampling | |
| 22 | application_framework/adaptors/webspheremq_adaptor.rst | component/adapters/webspheremq-adaptor.md | sampling | |
| 24 | application_framework/application_framework/batch/index.rst | processing-pattern/nablarch-batch/batch.md | index.rst naming | |
| 25 | application_framework/application_framework/batch/jsr352/application_design.rst | processing-pattern/jakarta-batch/application-design.md | sampling | |
| 28 | application_framework/application_framework/batch/jsr352/feature_details/database_reader.rst | processing-pattern/jakarta-batch/database-reader.md | sampling | |
| 31 | application_framework/application_framework/batch/jsr352/feature_details/pessimistic_lock.rst | processing-pattern/jakarta-batch/pessimistic-lock.md | sampling | |
| 34 | application_framework/application_framework/batch/jsr352/getting_started/batchlet/index.rst | processing-pattern/jakarta-batch/getting-started-batchlet.md | index.rst naming | |
| 35 | application_framework/application_framework/batch/jsr352/getting_started/chunk/index.rst | processing-pattern/jakarta-batch/getting-started-chunk.md | index.rst naming | |
| 37 | application_framework/application_framework/batch/jsr352/index.rst | processing-pattern/jakarta-batch/jsr352.md | index.rst naming | |
| 40 | application_framework/application_framework/batch/nablarch_batch/feature_details.rst | processing-pattern/nablarch-batch/feature-details.md | sampling | |
| 43 | application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_pessimistic_lock.rst | processing-pattern/nablarch-batch/nablarch-batch-pessimistic-lock.md | sampling | |
| 46 | application_framework/application_framework/batch/nablarch_batch/getting_started/nablarch_batch/index.rst | processing-pattern/nablarch-batch/getting-started-nablarch-batch.md | index.rst naming | |
| 47 | application_framework/application_framework/batch/nablarch_batch/index.rst | processing-pattern/nablarch-batch/nablarch-batch.md | index.rst naming | |
| 49 | application_framework/application_framework/blank_project/FirstStep.rst | setup/blank-project/FirstStep.md | sampling | |
| 51 | application_framework/application_framework/blank_project/MavenModuleStructures/index.rst | setup/blank-project/MavenModuleStructures.md | index.rst naming | |
| 52 | application_framework/application_framework/blank_project/ModifySettings.rst | setup/blank-project/ModifySettings.md | sampling | |
| 55 | application_framework/application_framework/blank_project/firstStep_appendix/ResiBatchReboot.rst | setup/blank-project/ResiBatchReboot.md | sampling | |
| 57 | application_framework/application_framework/blank_project/index.rst | setup/blank-project/blank-project.md | index.rst naming | |
| 58 | application_framework/application_framework/blank_project/maven.rst | setup/blank-project/maven.md | sampling | |
| 61 | application_framework/application_framework/blank_project/setup_blankProject/setup_NablarchBatch.rst | setup/blank-project/setup-NablarchBatch.md | sampling | |
| 64 | application_framework/application_framework/blank_project/setup_blankProject/setup_WebService.rst | setup/blank-project/setup-WebService.md | sampling | |
| 67 | application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWeb.rst | setup/blank-project/setup-ContainerWeb.md | sampling | |
| 69 | application_framework/application_framework/cloud_native/containerize/index.rst | setup/cloud-native/containerize.md | index.rst naming | |
| 70 | application_framework/application_framework/cloud_native/distributed_tracing/aws_distributed_tracing.rst | setup/cloud-native/aws-distributed-tracing.md | sampling | |
| 72 | application_framework/application_framework/cloud_native/distributed_tracing/index.rst | setup/cloud-native/distributed-tracing.md | index.rst naming | |
| 73 | application_framework/application_framework/cloud_native/index.rst | setup/cloud-native/cloud-native.md | index.rst naming | |
| 74 | application_framework/application_framework/configuration/index.rst | setup/configuration/configuration.md | index.rst naming | |
| 76 | application_framework/application_framework/handlers/batch/index.rst | processing-pattern/nablarch-batch/handlers-batch.md | index.rst naming | |
| 79 | application_framework/application_framework/handlers/common/ServiceAvailabilityCheckHandler.rst | component/handlers/common/ServiceAvailabilityCheckHandler.md | sampling | |
| 82 | application_framework/application_framework/handlers/common/global_error_handler.rst | component/handlers/common/global-error-handler.md | sampling | |
| 83 | application_framework/application_framework/handlers/common/index.rst | component/handlers/common/common.md | index.rst naming | |
| 85 | application_framework/application_framework/handlers/common/request_handler_entry.rst | component/handlers/common/request-handler-entry.md | sampling | |
| 88 | application_framework/application_framework/handlers/common/thread_context_handler.rst | component/handlers/common/thread-context-handler.md | sampling | |
| 91 | application_framework/application_framework/handlers/http_messaging/http_messaging_request_parsing_handler.rst | component/handlers/http_messaging/http-messaging-request-parsing-handler.md | sampling | |
| 93 | application_framework/application_framework/handlers/http_messaging/index.rst | component/handlers/http_messaging/http-messaging.md | index.rst naming | |
| 94 | application_framework/application_framework/handlers/mom_messaging/index.rst | component/handlers/mom_messaging/mom-messaging.md | index.rst naming | |
| 97 | application_framework/application_framework/handlers/mom_messaging/messaging_context_handler.rst | component/handlers/mom_messaging/messaging-context-handler.md | sampling | |
| 100 | application_framework/application_framework/handlers/rest/index.rst | component/handlers/rest/rest.md | index.rst naming | |
| 103 | application_framework/application_framework/handlers/rest/jaxrs_response_handler.rst | component/handlers/rest/jaxrs-response-handler.md | sampling | |
| 106 | application_framework/application_framework/handlers/standalone/multi_thread_execution_handler.rst | component/handlers/standalone/multi-thread-execution-handler.md | sampling | |
| 109 | application_framework/application_framework/handlers/web/SessionStoreHandler.rst | component/handlers/web/SessionStoreHandler.md | sampling | |
| 112 | application_framework/application_framework/handlers/web/health_check_endpoint_handler.rst | component/handlers/web/health-check-endpoint-handler.md | sampling | |
| 115 | application_framework/application_framework/handlers/web/http_character_encoding_handler.rst | component/handlers/web/http-character-encoding-handler.md | sampling | |
| 118 | application_framework/application_framework/handlers/web/http_rewrite_handler.rst | component/handlers/web/http-rewrite-handler.md | sampling | |
| 119 | application_framework/application_framework/handlers/web/index.rst | component/handlers/web/web.md | index.rst naming | |
| 121 | application_framework/application_framework/handlers/web/multipart_handler.rst | component/handlers/web/multipart-handler.md | sampling | |
| 124 | application_framework/application_framework/handlers/web/post_resubmit_prevent_handler.rst | component/handlers/web/post-resubmit-prevent-handler.md | sampling | |
| 127 | application_framework/application_framework/handlers/web/session_concurrent_access_handler.rst | component/handlers/web/session-concurrent-access-handler.md | sampling | |
| 130 | application_framework/application_framework/libraries/bean_util.rst | component/libraries/bean-util.md | sampling | |
| 133 | application_framework/application_framework/libraries/data_io/data_bind.rst | component/libraries/data_io/data-bind.md | sampling | |
| 136 | application_framework/application_framework/libraries/data_io/data_format/multi_format_example.rst | component/libraries/data_io/data_format/multi-format-example.md | sampling | |
| 139 | application_framework/application_framework/libraries/database/functional_comparison.rst | component/libraries/database/functional-comparison.md | sampling | |
| 142 | application_framework/application_framework/libraries/database_management.rst | component/libraries/database-management.md | sampling | |
| 145 | application_framework/application_framework/libraries/exclusive_control.rst | component/libraries/exclusive-control.md | sampling | |
| 148 | application_framework/application_framework/libraries/index.rst | component/libraries/libraries.md | index.rst naming | |
| 151 | application_framework/application_framework/libraries/log/http_access_log.rst | component/libraries/log/http-access-log.md | sampling | |
| 154 | application_framework/application_framework/libraries/log/performance_log.rst | component/libraries/log/performance-log.md | sampling | |
| 157 | application_framework/application_framework/libraries/message.rst | component/libraries/message.md | sampling | |
| 160 | application_framework/application_framework/libraries/service_availability.rst | component/libraries/service-availability.md | sampling | |
| 163 | application_framework/application_framework/libraries/session_store/update_example.rst | component/libraries/session_store/update-example.md | sampling | |
| 166 | application_framework/application_framework/libraries/system_messaging.rst | component/libraries/system-messaging.md | sampling | |
| 169 | application_framework/application_framework/libraries/tag.rst | component/libraries/tag.md | sampling | |
| 172 | application_framework/application_framework/libraries/utility.rst | component/libraries/utility.md | sampling | |
| 175 | application_framework/application_framework/libraries/validation/functional_comparison.rst | component/libraries/validation/functional-comparison.md | sampling | |
| 178 | application_framework/application_framework/messaging/db/architecture.rst | processing-pattern/db-messaging/architecture.md | sampling | |
| 181 | application_framework/application_framework/messaging/db/feature_details/multiple_process.rst | processing-pattern/db-messaging/multiple-process.md | sampling | |
| 184 | application_framework/application_framework/messaging/db/index.rst | processing-pattern/db-messaging/db.md | index.rst naming | |
| 187 | application_framework/application_framework/messaging/mom/feature_details.rst | processing-pattern/mom-messaging/feature-details.md | sampling | |
| 189 | application_framework/application_framework/messaging/mom/index.rst | processing-pattern/mom-messaging/mom.md | index.rst naming | |
| 190 | application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeAvailableCharacters.rst | setup/setting-guide/CustomizeAvailableCharacters.md | sampling | |
| 193 | application_framework/application_framework/setting_guide/CustomizingConfigurations/config_key_naming.rst | setup/setting-guide/config-key-naming.md | sampling | |
| 194 | application_framework/application_framework/setting_guide/CustomizingConfigurations/index.rst | setup/setting-guide/CustomizingConfigurations.md | index.rst naming | |
| 195 | application_framework/application_framework/setting_guide/ManagingEnvironmentalConfiguration/index.rst | setup/setting-guide/ManagingEnvironmentalConfiguration.md | index.rst naming | |
| 196 | application_framework/application_framework/setting_guide/index.rst | setup/setting-guide/setting-guide.md | index.rst naming | |
| 199 | application_framework/application_framework/web_service/http_messaging/architecture.rst | processing-pattern/restful-web-service/http_messaging/architecture.md | sampling | |
| 202 | application_framework/application_framework/web_service/http_messaging/getting_started/save/index.rst | processing-pattern/restful-web-service/http_messaging/save.md | index.rst naming | |
| 203 | application_framework/application_framework/web_service/http_messaging/index.rst | processing-pattern/restful-web-service/http_messaging/http-messaging.md | index.rst naming | |
| 204 | application_framework/application_framework/web_service/index.rst | processing-pattern/restful-web-service/web-service.md | index.rst naming | |
| 205 | application_framework/application_framework/web_service/rest/application_design.rst | processing-pattern/restful-web-service/rest/application-design.md | sampling | |
| 208 | application_framework/application_framework/web_service/rest/feature_details/resource_signature.rst | processing-pattern/restful-web-service/rest/resource-signature.md | sampling | |
| 209 | application_framework/application_framework/web_service/rest/getting_started/create/index.rst | processing-pattern/restful-web-service/rest/create.md | index.rst naming | |
| 210 | application_framework/application_framework/web_service/rest/getting_started/index.rst | processing-pattern/restful-web-service/rest/getting-started.md | index.rst naming | |
| 211 | application_framework/application_framework/web_service/rest/getting_started/search/index.rst | processing-pattern/restful-web-service/rest/search.md | index.rst naming | |
| 212 | application_framework/application_framework/web_service/rest/getting_started/update/index.rst | processing-pattern/restful-web-service/rest/update.md | index.rst naming | |
| 213 | application_framework/application_framework/web_service/rest/index.rst | processing-pattern/restful-web-service/rest/rest.md | index.rst naming | |
| 214 | development_tools/java_static_analysis/index.rst | development-tools/java-static-analysis/java-static-analysis.md | index.rst naming | |
| 217 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/index.rst | development-tools/testing-framework/01_ClassUnitTest/01_entityUnitTest/01-entityUnitTest.md | index.rst naming | |
| 219 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/index.rst | development-tools/testing-framework/05_UnitTestGuide/01_ClassUnitTest/01-ClassUnitTest.md | index.rst naming | |
| 220 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/batch.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/batch.md | sampling | |
| 223 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/duplicate_form_submission.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/duplicate-form-submission.md | sampling | |
| 226 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/http_send_sync.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/http-send-sync.md | sampling | |
| 227 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/index.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/02-RequestUnitTest.md | index.rst naming | |
| 229 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/real.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/real.md | sampling | |
| 232 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/batch.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/batch.md | sampling | |
| 235 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/http_send_sync.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/http-send-sync.md | sampling | |
| 236 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/index.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/03-DealUnitTest.md | index.rst naming | |
| 238 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/rest.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/rest.md | sampling | |
| 240 | development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/index.rst | development-tools/testing-framework/05_UnitTestGuide/05-UnitTestGuide.md | index.rst naming | |
| 241 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/01_Abstract.rst | development-tools/testing-framework/06_TestFWGuide/01-Abstract.md | sampling | |
| 244 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/03_Tips.rst | development-tools/testing-framework/06_TestFWGuide/03-Tips.md | sampling | |
| 247 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_batch.rst | development-tools/testing-framework/06_TestFWGuide/RequestUnitTest-batch.md | sampling | |
| 250 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_rest.rst | development-tools/testing-framework/06_TestFWGuide/RequestUnitTest-rest.md | sampling | |
| 252 | development_tools/testing_framework/guide/development_guide/06_TestFWGuide/index.rst | development-tools/testing-framework/06_TestFWGuide/06-TestFWGuide.md | index.rst naming | |
| 253 | development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/01_HttpDumpTool.rst | development-tools/testing-framework/08_TestTools/01_HttpDumpTool/01-HttpDumpTool-overview.md | sampling | |
| 255 | development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/index.rst | development-tools/testing-framework/08_TestTools/01_HttpDumpTool/01-HttpDumpTool.md | index.rst naming | |
| 256 | development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/01_MasterDataSetupTool.rst | development-tools/testing-framework/08_TestTools/02_MasterDataSetup/01-MasterDataSetupTool.md | sampling | |
| 258 | development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/index.rst | development-tools/testing-framework/08_TestTools/02_MasterDataSetup/02-MasterDataSetup.md | index.rst naming | |
| 259 | development_tools/testing_framework/guide/development_guide/08_TestTools/03_HtmlCheckTool/index.rst | development-tools/testing-framework/08_TestTools/03_HtmlCheckTool/03-HtmlCheckTool.md | index.rst naming | |
| 260 | development_tools/testing_framework/guide/development_guide/08_TestTools/index.rst | development-tools/testing-framework/08_TestTools/08-TestTools.md | index.rst naming | |
| 261 | development_tools/testing_framework/index.rst | development-tools/testing-framework/testing-framework.md | index.rst naming | |
| 262 | development_tools/toolbox/JspStaticAnalysis/01_JspStaticAnalysis.rst | development-tools/toolbox/JspStaticAnalysis/01-JspStaticAnalysis.md | sampling | |
| 264 | development_tools/toolbox/JspStaticAnalysis/index.rst | development-tools/toolbox/JspStaticAnalysis/JspStaticAnalysis.md | index.rst naming | |
| 265 | development_tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.rst | development-tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.md | sampling | |
| 267 | development_tools/toolbox/index.rst | development-tools/toolbox/toolbox.md | index.rst naming | |
| 268 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md | guide/nablarch-patterns/Asynchronous-operation-in-Nablarch.md | sampling | |

**Instructions**:
- Verify path conversion rules are followed
- Mark ✓ if correct, ✗ if incorrect (note correct path)

