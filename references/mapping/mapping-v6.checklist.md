# Verification Checklist: mapping-v6.md

**Generated**: 2026-02-24
**Total Mapping Rows**: 272
**Excluded Files**: 66
**Classification Checks**: 272
**Target Path Checks**: 272

---

## Excluded Files Verification

Files in source directory not included in mapping. Verify these should be excluded:

| # | Source Path | Reason | Status |
|---|---|---|---|
| 1 | application_framework/application_framework/handlers/index.rst | | |
| 2 | application_framework/application_framework/handlers/standalone/index.rst | | |
| 3 | application_framework/application_framework/handlers/standalone/main.rst | | |
| 4 | application_framework/application_framework/handlers/standalone/request_thread_loop_handler.rst | | |
| 5 | application_framework/application_framework/handlers/standalone/retry_handler.rst | | |
| 6 | application_framework/application_framework/handlers/standalone/status_code_convert_handler.rst | | |
| 7 | application_framework/application_framework/handlers/web_interceptor/InjectForm.rst | | |
| 8 | application_framework/application_framework/handlers/web_interceptor/index.rst | | |
| 9 | application_framework/application_framework/handlers/web_interceptor/on_double_submission.rst | | |
| 10 | application_framework/application_framework/handlers/web_interceptor/on_error.rst | | |
| 11 | application_framework/application_framework/handlers/web_interceptor/on_errors.rst | | |
| 12 | application_framework/application_framework/handlers/web_interceptor/use_token.rst | | |
| 13 | application_framework/application_framework/index.rst | | |
| 14 | application_framework/application_framework/messaging/index.rst | | |
| 15 | application_framework/application_framework/nablarch/architecture.rst | | |
| 16 | application_framework/application_framework/nablarch/big_picture.rst | | |
| 17 | application_framework/application_framework/nablarch/index.rst | | |
| 18 | application_framework/application_framework/nablarch/platform.rst | | |
| 19 | application_framework/application_framework/nablarch/policy.rst | | |
| 20 | application_framework/application_framework/web/application_design.rst | | |
| 21 | application_framework/application_framework/web/architecture.rst | | |
| 22 | application_framework/application_framework/web/feature_details.rst | | |
| 23 | application_framework/application_framework/web/feature_details/error_message.rst | | |
| 24 | application_framework/application_framework/web/feature_details/forward_error_page.rst | | |
| 25 | application_framework/application_framework/web/feature_details/jsp_session.rst | | |
| 26 | application_framework/application_framework/web/feature_details/nablarch_servlet_context_listener.rst | | |
| 27 | application_framework/application_framework/web/feature_details/view/other.rst | | |
| 28 | application_framework/application_framework/web/feature_details/web_front_controller.rst | | |
| 29 | application_framework/application_framework/web/getting_started/client_create/client_create1.rst | | |
| 30 | application_framework/application_framework/web/getting_started/client_create/client_create2.rst | | |
| 31 | application_framework/application_framework/web/getting_started/client_create/client_create3.rst | | |
| 32 | application_framework/application_framework/web/getting_started/client_create/client_create4.rst | | |
| 33 | application_framework/application_framework/web/getting_started/client_create/index.rst | | |
| 34 | application_framework/application_framework/web/getting_started/index.rst | | |
| 35 | application_framework/application_framework/web/getting_started/popup/index.rst | | |
| 36 | application_framework/application_framework/web/getting_started/project_bulk_update/index.rst | | |
| 37 | application_framework/application_framework/web/getting_started/project_delete/index.rst | | |
| 38 | application_framework/application_framework/web/getting_started/project_download/index.rst | | |
| 39 | application_framework/application_framework/web/getting_started/project_search/index.rst | | |
| 40 | application_framework/application_framework/web/getting_started/project_update/index.rst | | |
| 41 | application_framework/application_framework/web/getting_started/project_upload/index.rst | | |
| 42 | application_framework/application_framework/web/index.rst | | |
| 43 | application_framework/index.rst | | |
| 44 | biz_samples/01/0101_PBKDF2PasswordEncryptor.rst | | |
| 45 | biz_samples/01/index.rst | | |
| 46 | biz_samples/03/index.rst | | |
| 47 | biz_samples/04/0401_ExtendedDataFormatter.rst | | |
| 48 | biz_samples/04/0402_ExtendedFieldType.rst | | |
| 49 | biz_samples/04/index.rst | | |
| 50 | biz_samples/05/index.rst | | |
| 51 | biz_samples/08/index.rst | | |
| 52 | biz_samples/09/index.rst | | |
| 53 | biz_samples/10/contents/OnlineAccessLogStatistics.rst | | |
| 54 | biz_samples/10/index.rst | | |
| 55 | biz_samples/11/index.rst | | |
| 56 | biz_samples/12/index.rst | | |
| 57 | biz_samples/13/index.rst | | |
| 58 | biz_samples/index.rst | | |
| 59 | development_tools/index.rst | | |
| 60 | examples/index.rst | | |
| 61 | external_contents/index.rst | | |
| 62 | index.rst | | |
| 63 | jakarta_ee/index.rst | | |
| 64 | migration/index.rst | | |
| 65 | nablarch_api/index.rst | | |
| 66 | terms_of_use/index.rst | | |

**Instructions**:
- Read each excluded file to understand its content
- Determine why it was excluded (out of scope, duplicate, etc.)
- Mark '✓ Correctly excluded' or '✗ Should be included'
- Document reason for exclusion

---

## Classification Verification

For each row, read the RST source file and verify:
1. Type matches the content scope
2. Category correctly categorizes the technical area
3. Processing Pattern is assigned appropriately

| # | Source Path | Type | Category | PP | Check Reason | Judgment |
|---|---|---|---|---|---|---|
| 1 | Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx | check | security-check |  | complete verification | |
| 2 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md | guide | nablarch-patterns |  | complete verification | |
| 3 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_anti-pattern.md | guide | nablarch-patterns |  | complete verification | |
| 4 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_batch_processing_pattern.md | guide | nablarch-patterns |  | complete verification | |
| 5 | en/about_nablarch/concept.rst | about | about-nablarch |  | complete verification | |
| 6 | en/about_nablarch/index.rst | about | about-nablarch |  | complete verification | |
| 7 | en/about_nablarch/license.rst | about | about-nablarch |  | complete verification | |
| 8 | en/about_nablarch/mvn_module.rst | about | about-nablarch |  | complete verification | |
| 9 | en/about_nablarch/versionup_policy.rst | about | about-nablarch |  | complete verification | |
| 10 | en/application_framework/adaptors/doma_adaptor.rst | component | adapters |  | complete verification | |
| 11 | en/application_framework/adaptors/index.rst | component | adapters |  | complete verification | |
| 12 | en/application_framework/adaptors/jaxrs_adaptor.rst | component | adapters |  | complete verification | |
| 13 | en/application_framework/adaptors/jsr310_adaptor.rst | component | adapters |  | complete verification | |
| 14 | en/application_framework/adaptors/lettuce_adaptor.rst | component | adapters |  | complete verification | |
| 15 | en/application_framework/adaptors/lettuce_adaptor/redishealthchecker_lettuce_adaptor.rst | component | adapters |  | complete verification | |
| 16 | en/application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst | component | adapters |  | complete verification | |
| 17 | en/application_framework/adaptors/log_adaptor.rst | component | adapters |  | complete verification | |
| 18 | en/application_framework/adaptors/mail_sender_freemarker_adaptor.rst | component | adapters |  | complete verification | |
| 19 | en/application_framework/adaptors/mail_sender_thymeleaf_adaptor.rst | component | adapters |  | complete verification | |
| 20 | en/application_framework/adaptors/mail_sender_velocity_adaptor.rst | component | adapters |  | complete verification | |
| 21 | en/application_framework/adaptors/micrometer_adaptor.rst | component | adapters |  | complete verification | |
| 22 | en/application_framework/adaptors/router_adaptor.rst | component | adapters |  | complete verification | |
| 23 | en/application_framework/adaptors/slf4j_adaptor.rst | component | adapters |  | complete verification | |
| 24 | en/application_framework/adaptors/web_thymeleaf_adaptor.rst | component | adapters |  | complete verification | |
| 25 | en/application_framework/adaptors/webspheremq_adaptor.rst | component | adapters |  | complete verification | |
| 26 | en/application_framework/application_framework/batch/functional_comparison.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 27 | en/application_framework/application_framework/batch/index.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 28 | en/application_framework/application_framework/batch/jsr352/application_design.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 29 | en/application_framework/application_framework/batch/jsr352/architecture.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 30 | en/application_framework/application_framework/batch/jsr352/feature_details.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 31 | en/application_framework/application_framework/batch/jsr352/feature_details/database_reader.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 32 | en/application_framework/application_framework/batch/jsr352/feature_details/operation_policy.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 33 | en/application_framework/application_framework/batch/jsr352/feature_details/operator_notice_log.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 34 | en/application_framework/application_framework/batch/jsr352/feature_details/pessimistic_lock.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 35 | en/application_framework/application_framework/batch/jsr352/feature_details/progress_log.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 36 | en/application_framework/application_framework/batch/jsr352/feature_details/run_batch_application.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 37 | en/application_framework/application_framework/batch/jsr352/getting_started/batchlet/index.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 38 | en/application_framework/application_framework/batch/jsr352/getting_started/chunk/index.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 39 | en/application_framework/application_framework/batch/jsr352/getting_started/getting_started.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 40 | en/application_framework/application_framework/batch/jsr352/index.rst | processing-pattern | jakarta-batch | jakarta-batch | complete verification | |
| 41 | en/application_framework/application_framework/batch/nablarch_batch/application_design.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 42 | en/application_framework/application_framework/batch/nablarch_batch/architecture.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 43 | en/application_framework/application_framework/batch/nablarch_batch/feature_details.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 44 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_error_process.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 45 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_multiple_process.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 46 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_pessimistic_lock.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 47 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_retention_state.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 48 | en/application_framework/application_framework/batch/nablarch_batch/getting_started/getting_started.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 49 | en/application_framework/application_framework/batch/nablarch_batch/getting_started/nablarch_batch/index.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 50 | en/application_framework/application_framework/batch/nablarch_batch/index.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 51 | en/application_framework/application_framework/blank_project/CustomizeDB.rst | setup | blank-project |  | complete verification | |
| 52 | en/application_framework/application_framework/blank_project/FirstStep.rst | setup | blank-project |  | complete verification | |
| 53 | en/application_framework/application_framework/blank_project/FirstStepContainer.rst | setup | blank-project |  | complete verification | |
| 54 | en/application_framework/application_framework/blank_project/MavenModuleStructures/index.rst | setup | blank-project |  | complete verification | |
| 55 | en/application_framework/application_framework/blank_project/ModifySettings.rst | setup | blank-project |  | complete verification | |
| 56 | en/application_framework/application_framework/blank_project/addin_gsp.rst | setup | blank-project |  | complete verification | |
| 57 | en/application_framework/application_framework/blank_project/beforeFirstStep.rst | setup | blank-project |  | complete verification | |
| 58 | en/application_framework/application_framework/blank_project/firstStep_appendix/ResiBatchReboot.rst | setup | blank-project |  | complete verification | |
| 59 | en/application_framework/application_framework/blank_project/firstStep_appendix/firststep_complement.rst | setup | blank-project |  | complete verification | |
| 60 | en/application_framework/application_framework/blank_project/index.rst | setup | blank-project |  | complete verification | |
| 61 | en/application_framework/application_framework/blank_project/maven.rst | setup | blank-project |  | complete verification | |
| 62 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_Java21.rst | setup | blank-project |  | complete verification | |
| 63 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_Jbatch.rst | setup | blank-project | jakarta-batch | complete verification | |
| 64 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_NablarchBatch.rst | setup | blank-project | nablarch-batch | complete verification | |
| 65 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_NablarchBatch_Dbless.rst | setup | blank-project | nablarch-batch | complete verification | |
| 66 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_Web.rst | setup | blank-project | web-application | complete verification | |
| 67 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_WebService.rst | setup | blank-project | restful-web-service | complete verification | |
| 68 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerBatch.rst | setup | blank-project |  | complete verification | |
| 69 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerBatch_Dbless.rst | setup | blank-project |  | complete verification | |
| 70 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWeb.rst | setup | blank-project | web-application | complete verification | |
| 71 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWebService.rst | setup | blank-project | restful-web-service | complete verification | |
| 72 | en/application_framework/application_framework/cloud_native/containerize/index.rst | setup | cloud-native |  | complete verification | |
| 73 | en/application_framework/application_framework/cloud_native/distributed_tracing/aws_distributed_tracing.rst | setup | cloud-native |  | complete verification | |
| 74 | en/application_framework/application_framework/cloud_native/distributed_tracing/azure_distributed_tracing.rst | setup | cloud-native |  | complete verification | |
| 75 | en/application_framework/application_framework/cloud_native/distributed_tracing/index.rst | setup | cloud-native |  | complete verification | |
| 76 | en/application_framework/application_framework/cloud_native/index.rst | setup | cloud-native |  | complete verification | |
| 77 | en/application_framework/application_framework/configuration/index.rst | setup | configuration |  | complete verification | |
| 78 | en/application_framework/application_framework/handlers/batch/dbless_loop_handler.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 79 | en/application_framework/application_framework/handlers/batch/index.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 80 | en/application_framework/application_framework/handlers/batch/loop_handler.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 81 | en/application_framework/application_framework/handlers/batch/process_resident_handler.rst | processing-pattern | nablarch-batch | nablarch-batch | complete verification | |
| 82 | en/application_framework/application_framework/handlers/common/ServiceAvailabilityCheckHandler.rst | component | handlers |  | complete verification | |
| 83 | en/application_framework/application_framework/handlers/common/database_connection_management_handler.rst | component | handlers |  | complete verification | |
| 84 | en/application_framework/application_framework/handlers/common/file_record_writer_dispose_handler.rst | component | handlers |  | complete verification | |
| 85 | en/application_framework/application_framework/handlers/common/global_error_handler.rst | component | handlers |  | complete verification | |
| 86 | en/application_framework/application_framework/handlers/common/index.rst | component | handlers |  | complete verification | |
| 87 | en/application_framework/application_framework/handlers/common/permission_check_handler.rst | component | handlers |  | complete verification | |
| 88 | en/application_framework/application_framework/handlers/common/request_handler_entry.rst | component | handlers |  | complete verification | |
| 89 | en/application_framework/application_framework/handlers/common/request_path_java_package_mapping.rst | component | handlers |  | complete verification | |
| 90 | en/application_framework/application_framework/handlers/common/thread_context_clear_handler.rst | component | handlers |  | complete verification | |
| 91 | en/application_framework/application_framework/handlers/common/thread_context_handler.rst | component | handlers |  | complete verification | |
| 92 | en/application_framework/application_framework/handlers/common/transaction_management_handler.rst | component | handlers |  | complete verification | |
| 93 | en/application_framework/application_framework/handlers/http_messaging/http_messaging_error_handler.rst | component | handlers | http-messaging | complete verification | |
| 94 | en/application_framework/application_framework/handlers/http_messaging/http_messaging_request_parsing_handler.rst | component | handlers | http-messaging | complete verification | |
| 95 | en/application_framework/application_framework/handlers/http_messaging/http_messaging_response_building_handler.rst | component | handlers | http-messaging | complete verification | |
| 96 | en/application_framework/application_framework/handlers/http_messaging/index.rst | component | handlers | http-messaging | complete verification | |
| 97 | en/application_framework/application_framework/handlers/mom_messaging/index.rst | component | handlers | mom-messaging | complete verification | |
| 98 | en/application_framework/application_framework/handlers/mom_messaging/message_reply_handler.rst | component | handlers | mom-messaging | complete verification | |
| 99 | en/application_framework/application_framework/handlers/mom_messaging/message_resend_handler.rst | component | handlers | mom-messaging | complete verification | |
| 100 | en/application_framework/application_framework/handlers/mom_messaging/messaging_context_handler.rst | component | handlers | mom-messaging | complete verification | |
| 101 | en/application_framework/application_framework/handlers/rest/body_convert_handler.rst | component | handlers | restful-web-service | complete verification | |
| 102 | en/application_framework/application_framework/handlers/rest/cors_preflight_request_handler.rst | component | handlers | restful-web-service | complete verification | |
| 103 | en/application_framework/application_framework/handlers/rest/index.rst | component | handlers | restful-web-service | complete verification | |
| 104 | en/application_framework/application_framework/handlers/rest/jaxrs_access_log_handler.rst | component | handlers | restful-web-service | complete verification | |
| 105 | en/application_framework/application_framework/handlers/rest/jaxrs_bean_validation_handler.rst | component | handlers | restful-web-service | complete verification | |
| 106 | en/application_framework/application_framework/handlers/rest/jaxrs_response_handler.rst | component | handlers | restful-web-service | complete verification | |
| 107 | en/application_framework/application_framework/handlers/standalone/data_read_handler.rst | component | handlers | nablarch-batch | complete verification | |
| 108 | en/application_framework/application_framework/handlers/standalone/duplicate_process_check_handler.rst | component | handlers | nablarch-batch | complete verification | |
| 109 | en/application_framework/application_framework/handlers/standalone/multi_thread_execution_handler.rst | component | handlers | nablarch-batch | complete verification | |
| 110 | en/application_framework/application_framework/handlers/standalone/process_stop_handler.rst | component | handlers | nablarch-batch | complete verification | |
| 111 | en/application_framework/application_framework/handlers/web/HttpErrorHandler.rst | component | handlers | web-application | complete verification | |
| 112 | en/application_framework/application_framework/handlers/web/SessionStoreHandler.rst | component | handlers | web-application | complete verification | |
| 113 | en/application_framework/application_framework/handlers/web/csrf_token_verification_handler.rst | component | handlers | web-application | complete verification | |
| 114 | en/application_framework/application_framework/handlers/web/forwarding_handler.rst | component | handlers | web-application | complete verification | |
| 115 | en/application_framework/application_framework/handlers/web/health_check_endpoint_handler.rst | component | handlers | web-application | complete verification | |
| 116 | en/application_framework/application_framework/handlers/web/hot_deploy_handler.rst | component | handlers | web-application | complete verification | |
| 117 | en/application_framework/application_framework/handlers/web/http_access_log_handler.rst | component | handlers | web-application | complete verification | |
| 118 | en/application_framework/application_framework/handlers/web/http_character_encoding_handler.rst | component | handlers | web-application | complete verification | |
| 119 | en/application_framework/application_framework/handlers/web/http_request_java_package_mapping.rst | component | handlers | web-application | complete verification | |
| 120 | en/application_framework/application_framework/handlers/web/http_response_handler.rst | component | handlers | web-application | complete verification | |
| 121 | en/application_framework/application_framework/handlers/web/http_rewrite_handler.rst | component | handlers | web-application | complete verification | |
| 122 | en/application_framework/application_framework/handlers/web/index.rst | component | handlers | web-application | complete verification | |
| 123 | en/application_framework/application_framework/handlers/web/keitai_access_handler.rst | component | handlers | web-application | complete verification | |
| 124 | en/application_framework/application_framework/handlers/web/multipart_handler.rst | component | handlers | web-application | complete verification | |
| 125 | en/application_framework/application_framework/handlers/web/nablarch_tag_handler.rst | component | handlers | web-application | complete verification | |
| 126 | en/application_framework/application_framework/handlers/web/normalize_handler.rst | component | handlers | web-application | complete verification | |
| 127 | en/application_framework/application_framework/handlers/web/post_resubmit_prevent_handler.rst | component | handlers | web-application | complete verification | |
| 128 | en/application_framework/application_framework/handlers/web/resource_mapping.rst | component | handlers | web-application | complete verification | |
| 129 | en/application_framework/application_framework/handlers/web/secure_handler.rst | component | handlers | web-application | complete verification | |
| 130 | en/application_framework/application_framework/handlers/web/session_concurrent_access_handler.rst | component | handlers | web-application | complete verification | |
| 131 | en/application_framework/application_framework/libraries/authorization/permission_check.rst | component | libraries |  | complete verification | |
| 132 | en/application_framework/application_framework/libraries/authorization/role_check.rst | component | libraries |  | complete verification | |
| 133 | en/application_framework/application_framework/libraries/bean_util.rst | component | libraries |  | complete verification | |
| 134 | en/application_framework/application_framework/libraries/code.rst | component | libraries |  | complete verification | |
| 135 | en/application_framework/application_framework/libraries/data_converter.rst | component | libraries |  | complete verification | |
| 136 | en/application_framework/application_framework/libraries/data_io/data_bind.rst | component | libraries |  | complete verification | |
| 137 | en/application_framework/application_framework/libraries/data_io/data_format.rst | component | libraries |  | complete verification | |
| 138 | en/application_framework/application_framework/libraries/data_io/data_format/format_definition.rst | component | libraries |  | complete verification | |
| 139 | en/application_framework/application_framework/libraries/data_io/data_format/multi_format_example.rst | component | libraries |  | complete verification | |
| 140 | en/application_framework/application_framework/libraries/data_io/functional_comparison.rst | component | libraries |  | complete verification | |
| 141 | en/application_framework/application_framework/libraries/database/database.rst | component | libraries |  | complete verification | |
| 142 | en/application_framework/application_framework/libraries/database/functional_comparison.rst | component | libraries |  | complete verification | |
| 143 | en/application_framework/application_framework/libraries/database/generator.rst | component | libraries |  | complete verification | |
| 144 | en/application_framework/application_framework/libraries/database/universal_dao.rst | component | libraries |  | complete verification | |
| 145 | en/application_framework/application_framework/libraries/database_management.rst | component | libraries |  | complete verification | |
| 146 | en/application_framework/application_framework/libraries/date.rst | component | libraries |  | complete verification | |
| 147 | en/application_framework/application_framework/libraries/db_double_submit.rst | component | libraries |  | complete verification | |
| 148 | en/application_framework/application_framework/libraries/exclusive_control.rst | component | libraries |  | complete verification | |
| 149 | en/application_framework/application_framework/libraries/file_path_management.rst | component | libraries |  | complete verification | |
| 150 | en/application_framework/application_framework/libraries/format.rst | component | libraries |  | complete verification | |
| 151 | en/application_framework/application_framework/libraries/index.rst | component | libraries |  | complete verification | |
| 152 | en/application_framework/application_framework/libraries/log.rst | component | libraries |  | complete verification | |
| 153 | en/application_framework/application_framework/libraries/log/failure_log.rst | component | libraries |  | complete verification | |
| 154 | en/application_framework/application_framework/libraries/log/http_access_log.rst | component | libraries |  | complete verification | |
| 155 | en/application_framework/application_framework/libraries/log/jaxrs_access_log.rst | component | libraries |  | complete verification | |
| 156 | en/application_framework/application_framework/libraries/log/messaging_log.rst | component | libraries |  | complete verification | |
| 157 | en/application_framework/application_framework/libraries/log/performance_log.rst | component | libraries |  | complete verification | |
| 158 | en/application_framework/application_framework/libraries/log/sql_log.rst | component | libraries |  | complete verification | |
| 159 | en/application_framework/application_framework/libraries/mail.rst | component | libraries |  | complete verification | |
| 160 | en/application_framework/application_framework/libraries/message.rst | component | libraries |  | complete verification | |
| 161 | en/application_framework/application_framework/libraries/permission_check.rst | component | libraries |  | complete verification | |
| 162 | en/application_framework/application_framework/libraries/repository.rst | component | libraries |  | complete verification | |
| 163 | en/application_framework/application_framework/libraries/service_availability.rst | component | libraries |  | complete verification | |
| 164 | en/application_framework/application_framework/libraries/session_store.rst | component | libraries |  | complete verification | |
| 165 | en/application_framework/application_framework/libraries/session_store/create_example.rst | component | libraries |  | complete verification | |
| 166 | en/application_framework/application_framework/libraries/session_store/update_example.rst | component | libraries |  | complete verification | |
| 167 | en/application_framework/application_framework/libraries/stateless_web_app.rst | component | libraries |  | complete verification | |
| 168 | en/application_framework/application_framework/libraries/static_data_cache.rst | component | libraries |  | complete verification | |
| 169 | en/application_framework/application_framework/libraries/system_messaging.rst | component | libraries |  | complete verification | |
| 170 | en/application_framework/application_framework/libraries/system_messaging/http_system_messaging.rst | component | libraries |  | complete verification | |
| 171 | en/application_framework/application_framework/libraries/system_messaging/mom_system_messaging.rst | component | libraries |  | complete verification | |
| 172 | en/application_framework/application_framework/libraries/tag.rst | component | libraries |  | complete verification | |
| 173 | en/application_framework/application_framework/libraries/tag/tag_reference.rst | component | libraries |  | complete verification | |
| 174 | en/application_framework/application_framework/libraries/transaction.rst | component | libraries |  | complete verification | |
| 175 | en/application_framework/application_framework/libraries/utility.rst | component | libraries |  | complete verification | |
| 176 | en/application_framework/application_framework/libraries/validation.rst | component | libraries |  | complete verification | |
| 177 | en/application_framework/application_framework/libraries/validation/bean_validation.rst | component | libraries |  | complete verification | |
| 178 | en/application_framework/application_framework/libraries/validation/functional_comparison.rst | component | libraries |  | complete verification | |
| 179 | en/application_framework/application_framework/libraries/validation/nablarch_validation.rst | component | libraries |  | complete verification | |
| 180 | en/application_framework/application_framework/messaging/db/application_design.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 181 | en/application_framework/application_framework/messaging/db/architecture.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 182 | en/application_framework/application_framework/messaging/db/feature_details.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 183 | en/application_framework/application_framework/messaging/db/feature_details/error_processing.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 184 | en/application_framework/application_framework/messaging/db/feature_details/multiple_process.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 185 | en/application_framework/application_framework/messaging/db/getting_started.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 186 | en/application_framework/application_framework/messaging/db/getting_started/table_queue.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 187 | en/application_framework/application_framework/messaging/db/index.rst | processing-pattern | db-messaging | db-messaging | complete verification | |
| 188 | en/application_framework/application_framework/messaging/mom/application_design.rst | processing-pattern | mom-messaging | mom-messaging | complete verification | |
| 189 | en/application_framework/application_framework/messaging/mom/architecture.rst | processing-pattern | mom-messaging | mom-messaging | complete verification | |
| 190 | en/application_framework/application_framework/messaging/mom/feature_details.rst | processing-pattern | mom-messaging | mom-messaging | complete verification | |
| 191 | en/application_framework/application_framework/messaging/mom/getting_started.rst | processing-pattern | mom-messaging | mom-messaging | complete verification | |
| 192 | en/application_framework/application_framework/messaging/mom/index.rst | processing-pattern | mom-messaging | mom-messaging | complete verification | |
| 193 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeAvailableCharacters.rst | setup | setting-guide |  | complete verification | |
| 194 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeMessageIDAndMessage.rst | setup | setting-guide |  | complete verification | |
| 195 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeSystemTableName.rst | setup | setting-guide |  | complete verification | |
| 196 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/config_key_naming.rst | setup | setting-guide |  | complete verification | |
| 197 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/index.rst | setup | setting-guide |  | complete verification | |
| 198 | en/application_framework/application_framework/setting_guide/ManagingEnvironmentalConfiguration/index.rst | setup | setting-guide |  | complete verification | |
| 199 | en/application_framework/application_framework/setting_guide/index.rst | setup | setting-guide |  | complete verification | |
| 200 | en/application_framework/application_framework/web_service/functional_comparison.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 201 | en/application_framework/application_framework/web_service/http_messaging/application_design.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 202 | en/application_framework/application_framework/web_service/http_messaging/architecture.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 203 | en/application_framework/application_framework/web_service/http_messaging/feature_details.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 204 | en/application_framework/application_framework/web_service/http_messaging/getting_started/getting_started.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 205 | en/application_framework/application_framework/web_service/http_messaging/getting_started/save/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 206 | en/application_framework/application_framework/web_service/http_messaging/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 207 | en/application_framework/application_framework/web_service/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 208 | en/application_framework/application_framework/web_service/rest/application_design.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 209 | en/application_framework/application_framework/web_service/rest/architecture.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 210 | en/application_framework/application_framework/web_service/rest/feature_details.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 211 | en/application_framework/application_framework/web_service/rest/feature_details/resource_signature.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 212 | en/application_framework/application_framework/web_service/rest/getting_started/create/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 213 | en/application_framework/application_framework/web_service/rest/getting_started/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 214 | en/application_framework/application_framework/web_service/rest/getting_started/search/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 215 | en/application_framework/application_framework/web_service/rest/getting_started/update/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 216 | en/application_framework/application_framework/web_service/rest/index.rst | processing-pattern | restful-web-service | restful-web-service | complete verification | |
| 217 | en/development_tools/java_static_analysis/index.rst | development-tools | java-static-analysis |  | complete verification | |
| 218 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/01_entityUnitTestWithBeanValidation.rst | development-tools | testing-framework |  | complete verification | |
| 219 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/02_entityUnitTestWithNablarchValidation.rst | development-tools | testing-framework |  | complete verification | |
| 220 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/index.rst | development-tools | testing-framework |  | complete verification | |
| 221 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/02_componentUnitTest.rst | development-tools | testing-framework |  | complete verification | |
| 222 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/index.rst | development-tools | testing-framework |  | complete verification | |
| 223 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/batch.rst | development-tools | testing-framework |  | complete verification | |
| 224 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/delayed_receive.rst | development-tools | testing-framework |  | complete verification | |
| 225 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/delayed_send.rst | development-tools | testing-framework |  | complete verification | |
| 226 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/duplicate_form_submission.rst | development-tools | testing-framework |  | complete verification | |
| 227 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/fileupload.rst | development-tools | testing-framework |  | complete verification | |
| 228 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/http_real.rst | development-tools | testing-framework |  | complete verification | |
| 229 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/http_send_sync.rst | development-tools | testing-framework |  | complete verification | |
| 230 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/index.rst | development-tools | testing-framework |  | complete verification | |
| 231 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/mail.rst | development-tools | testing-framework |  | complete verification | |
| 232 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/real.rst | development-tools | testing-framework |  | complete verification | |
| 233 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/rest.rst | development-tools | testing-framework |  | complete verification | |
| 234 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/send_sync.rst | development-tools | testing-framework |  | complete verification | |
| 235 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/batch.rst | development-tools | testing-framework |  | complete verification | |
| 236 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/delayed_receive.rst | development-tools | testing-framework |  | complete verification | |
| 237 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/delayed_send.rst | development-tools | testing-framework |  | complete verification | |
| 238 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/http_send_sync.rst | development-tools | testing-framework |  | complete verification | |
| 239 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/index.rst | development-tools | testing-framework |  | complete verification | |
| 240 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/real.rst | development-tools | testing-framework |  | complete verification | |
| 241 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/rest.rst | development-tools | testing-framework |  | complete verification | |
| 242 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/send_sync.rst | development-tools | testing-framework |  | complete verification | |
| 243 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/index.rst | development-tools | testing-framework |  | complete verification | |
| 244 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/01_Abstract.rst | development-tools | testing-framework |  | complete verification | |
| 245 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/02_DbAccessTest.rst | development-tools | testing-framework |  | complete verification | |
| 246 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/02_RequestUnitTest.rst | development-tools | testing-framework |  | complete verification | |
| 247 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/03_Tips.rst | development-tools | testing-framework |  | complete verification | |
| 248 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/04_MasterDataRestore.rst | development-tools | testing-framework |  | complete verification | |
| 249 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/JUnit5_Extension.rst | development-tools | testing-framework |  | complete verification | |
| 250 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_batch.rst | development-tools | testing-framework |  | complete verification | |
| 251 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_http_send_sync.rst | development-tools | testing-framework |  | complete verification | |
| 252 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_real.rst | development-tools | testing-framework |  | complete verification | |
| 253 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_rest.rst | development-tools | testing-framework |  | complete verification | |
| 254 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_send_sync.rst | development-tools | testing-framework |  | complete verification | |
| 255 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/index.rst | development-tools | testing-framework |  | complete verification | |
| 256 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/01_HttpDumpTool.rst | development-tools | testing-framework |  | complete verification | |
| 257 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/02_SetUpHttpDumpTool.rst | development-tools | testing-framework |  | complete verification | |
| 258 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/index.rst | development-tools | testing-framework |  | complete verification | |
| 259 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/01_MasterDataSetupTool.rst | development-tools | testing-framework |  | complete verification | |
| 260 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/02_ConfigMasterDataSetupTool.rst | development-tools | testing-framework |  | complete verification | |
| 261 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/index.rst | development-tools | testing-framework |  | complete verification | |
| 262 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/03_HtmlCheckTool/index.rst | development-tools | testing-framework |  | complete verification | |
| 263 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/index.rst | development-tools | testing-framework |  | complete verification | |
| 264 | en/development_tools/testing_framework/index.rst | development-tools | testing-framework |  | complete verification | |
| 265 | en/development_tools/toolbox/JspStaticAnalysis/01_JspStaticAnalysis.rst | development-tools | toolbox |  | complete verification | |
| 266 | en/development_tools/toolbox/JspStaticAnalysis/02_JspStaticAnalysisInstall.rst | development-tools | toolbox |  | complete verification | |
| 267 | en/development_tools/toolbox/JspStaticAnalysis/index.rst | development-tools | toolbox |  | complete verification | |
| 268 | en/development_tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.rst | development-tools | toolbox |  | complete verification | |
| 269 | en/development_tools/toolbox/SqlExecutor/SqlExecutor.rst | development-tools | toolbox |  | complete verification | |
| 270 | en/development_tools/toolbox/index.rst | development-tools | toolbox |  | complete verification | |
| 271 | ja/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/double_transmission.rst | development-tools | testing-framework |  | complete verification | |
| 272 | ja/releases/index.rst | about | release-notes |  | complete verification | |

**Instructions**:
- Read the first 50 lines of the RST file at `{source_dir}/{source_path}`
- Check if classification matches the content
- Mark ✓ if correct, ✗ if incorrect (note correct classification)

---

## Target Path Verification

For each row, verify:
1. Target path starts with Type
2. Filename correctly converts `_` to `-`
3. Extension changed from `.rst`/`.md` to `.json`
4. Subdirectories preserved where appropriate

| # | Source Path | Target Path | Check Reason | Judgment |
|---|---|---|---|---|
| 1 | Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx | check/security-check/Nablarch機能のセキュリティ対応表.xlsx | complete verification | |
| 2 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md | guide/nablarch-patterns/Asynchronous-operation-in-Nablarch.json | complete verification | |
| 3 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_anti-pattern.md | guide/nablarch-patterns/Nablarch-anti-pattern.json | complete verification | |
| 4 | en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_batch_processing_pattern.md | guide/nablarch-patterns/Nablarch-batch-processing-pattern.json | complete verification | |
| 5 | en/about_nablarch/concept.rst | about/about-nablarch/concept.json | complete verification | |
| 6 | en/about_nablarch/index.rst | about/about-nablarch/about-nablarch.json | complete verification | |
| 7 | en/about_nablarch/license.rst | about/about-nablarch/license.json | complete verification | |
| 8 | en/about_nablarch/mvn_module.rst | about/about-nablarch/mvn-module.json | complete verification | |
| 9 | en/about_nablarch/versionup_policy.rst | about/about-nablarch/versionup-policy.json | complete verification | |
| 10 | en/application_framework/adaptors/doma_adaptor.rst | component/adapters/doma-adaptor.json | complete verification | |
| 11 | en/application_framework/adaptors/index.rst | component/adapters/adaptors.json | complete verification | |
| 12 | en/application_framework/adaptors/jaxrs_adaptor.rst | component/adapters/jaxrs-adaptor.json | complete verification | |
| 13 | en/application_framework/adaptors/jsr310_adaptor.rst | component/adapters/jsr310-adaptor.json | complete verification | |
| 14 | en/application_framework/adaptors/lettuce_adaptor.rst | component/adapters/lettuce-adaptor.json | complete verification | |
| 15 | en/application_framework/adaptors/lettuce_adaptor/redishealthchecker_lettuce_adaptor.rst | component/adapters/lettuce_adaptor/redishealthchecker-lettuce-adaptor.json | complete verification | |
| 16 | en/application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst | component/adapters/lettuce_adaptor/redisstore-lettuce-adaptor.json | complete verification | |
| 17 | en/application_framework/adaptors/log_adaptor.rst | component/adapters/log-adaptor.json | complete verification | |
| 18 | en/application_framework/adaptors/mail_sender_freemarker_adaptor.rst | component/adapters/mail-sender-freemarker-adaptor.json | complete verification | |
| 19 | en/application_framework/adaptors/mail_sender_thymeleaf_adaptor.rst | component/adapters/mail-sender-thymeleaf-adaptor.json | complete verification | |
| 20 | en/application_framework/adaptors/mail_sender_velocity_adaptor.rst | component/adapters/mail-sender-velocity-adaptor.json | complete verification | |
| 21 | en/application_framework/adaptors/micrometer_adaptor.rst | component/adapters/micrometer-adaptor.json | complete verification | |
| 22 | en/application_framework/adaptors/router_adaptor.rst | component/adapters/router-adaptor.json | complete verification | |
| 23 | en/application_framework/adaptors/slf4j_adaptor.rst | component/adapters/slf4j-adaptor.json | complete verification | |
| 24 | en/application_framework/adaptors/web_thymeleaf_adaptor.rst | component/adapters/web-thymeleaf-adaptor.json | complete verification | |
| 25 | en/application_framework/adaptors/webspheremq_adaptor.rst | component/adapters/webspheremq-adaptor.json | complete verification | |
| 26 | en/application_framework/application_framework/batch/functional_comparison.rst | processing-pattern/nablarch-batch/functional-comparison.json | complete verification | |
| 27 | en/application_framework/application_framework/batch/index.rst | processing-pattern/nablarch-batch/batch.json | complete verification | |
| 28 | en/application_framework/application_framework/batch/jsr352/application_design.rst | processing-pattern/jakarta-batch/application-design.json | complete verification | |
| 29 | en/application_framework/application_framework/batch/jsr352/architecture.rst | processing-pattern/jakarta-batch/architecture.json | complete verification | |
| 30 | en/application_framework/application_framework/batch/jsr352/feature_details.rst | processing-pattern/jakarta-batch/feature-details.json | complete verification | |
| 31 | en/application_framework/application_framework/batch/jsr352/feature_details/database_reader.rst | processing-pattern/jakarta-batch/database-reader.json | complete verification | |
| 32 | en/application_framework/application_framework/batch/jsr352/feature_details/operation_policy.rst | processing-pattern/jakarta-batch/operation-policy.json | complete verification | |
| 33 | en/application_framework/application_framework/batch/jsr352/feature_details/operator_notice_log.rst | processing-pattern/jakarta-batch/operator-notice-log.json | complete verification | |
| 34 | en/application_framework/application_framework/batch/jsr352/feature_details/pessimistic_lock.rst | processing-pattern/jakarta-batch/pessimistic-lock.json | complete verification | |
| 35 | en/application_framework/application_framework/batch/jsr352/feature_details/progress_log.rst | processing-pattern/jakarta-batch/progress-log.json | complete verification | |
| 36 | en/application_framework/application_framework/batch/jsr352/feature_details/run_batch_application.rst | processing-pattern/jakarta-batch/run-batch-application.json | complete verification | |
| 37 | en/application_framework/application_framework/batch/jsr352/getting_started/batchlet/index.rst | processing-pattern/jakarta-batch/getting-started-batchlet.json | complete verification | |
| 38 | en/application_framework/application_framework/batch/jsr352/getting_started/chunk/index.rst | processing-pattern/jakarta-batch/getting-started-chunk.json | complete verification | |
| 39 | en/application_framework/application_framework/batch/jsr352/getting_started/getting_started.rst | processing-pattern/jakarta-batch/getting-started.json | complete verification | |
| 40 | en/application_framework/application_framework/batch/jsr352/index.rst | processing-pattern/jakarta-batch/jsr352.json | complete verification | |
| 41 | en/application_framework/application_framework/batch/nablarch_batch/application_design.rst | processing-pattern/nablarch-batch/application-design.json | complete verification | |
| 42 | en/application_framework/application_framework/batch/nablarch_batch/architecture.rst | processing-pattern/nablarch-batch/architecture.json | complete verification | |
| 43 | en/application_framework/application_framework/batch/nablarch_batch/feature_details.rst | processing-pattern/nablarch-batch/feature-details.json | complete verification | |
| 44 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_error_process.rst | processing-pattern/nablarch-batch/nablarch-batch-error-process.json | complete verification | |
| 45 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_multiple_process.rst | processing-pattern/nablarch-batch/nablarch-batch-multiple-process.json | complete verification | |
| 46 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_pessimistic_lock.rst | processing-pattern/nablarch-batch/nablarch-batch-pessimistic-lock.json | complete verification | |
| 47 | en/application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_retention_state.rst | processing-pattern/nablarch-batch/nablarch-batch-retention-state.json | complete verification | |
| 48 | en/application_framework/application_framework/batch/nablarch_batch/getting_started/getting_started.rst | processing-pattern/nablarch-batch/getting-started.json | complete verification | |
| 49 | en/application_framework/application_framework/batch/nablarch_batch/getting_started/nablarch_batch/index.rst | processing-pattern/nablarch-batch/getting-started-nablarch-batch.json | complete verification | |
| 50 | en/application_framework/application_framework/batch/nablarch_batch/index.rst | processing-pattern/nablarch-batch/nablarch-batch.json | complete verification | |
| 51 | en/application_framework/application_framework/blank_project/CustomizeDB.rst | setup/blank-project/CustomizeDB.json | complete verification | |
| 52 | en/application_framework/application_framework/blank_project/FirstStep.rst | setup/blank-project/FirstStep.json | complete verification | |
| 53 | en/application_framework/application_framework/blank_project/FirstStepContainer.rst | setup/blank-project/FirstStepContainer.json | complete verification | |
| 54 | en/application_framework/application_framework/blank_project/MavenModuleStructures/index.rst | setup/blank-project/MavenModuleStructures.json | complete verification | |
| 55 | en/application_framework/application_framework/blank_project/ModifySettings.rst | setup/blank-project/ModifySettings.json | complete verification | |
| 56 | en/application_framework/application_framework/blank_project/addin_gsp.rst | setup/blank-project/addin-gsp.json | complete verification | |
| 57 | en/application_framework/application_framework/blank_project/beforeFirstStep.rst | setup/blank-project/beforeFirstStep.json | complete verification | |
| 58 | en/application_framework/application_framework/blank_project/firstStep_appendix/ResiBatchReboot.rst | setup/blank-project/ResiBatchReboot.json | complete verification | |
| 59 | en/application_framework/application_framework/blank_project/firstStep_appendix/firststep_complement.rst | setup/blank-project/firststep-complement.json | complete verification | |
| 60 | en/application_framework/application_framework/blank_project/index.rst | setup/blank-project/blank-project.json | complete verification | |
| 61 | en/application_framework/application_framework/blank_project/maven.rst | setup/blank-project/maven.json | complete verification | |
| 62 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_Java21.rst | setup/blank-project/setup-Java21.json | complete verification | |
| 63 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_Jbatch.rst | setup/blank-project/setup-Jbatch.json | complete verification | |
| 64 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_NablarchBatch.rst | setup/blank-project/setup-NablarchBatch.json | complete verification | |
| 65 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_NablarchBatch_Dbless.rst | setup/blank-project/setup-NablarchBatch-Dbless.json | complete verification | |
| 66 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_Web.rst | setup/blank-project/setup-Web.json | complete verification | |
| 67 | en/application_framework/application_framework/blank_project/setup_blankProject/setup_WebService.rst | setup/blank-project/setup-WebService.json | complete verification | |
| 68 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerBatch.rst | setup/blank-project/setup-ContainerBatch.json | complete verification | |
| 69 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerBatch_Dbless.rst | setup/blank-project/setup-ContainerBatch-Dbless.json | complete verification | |
| 70 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWeb.rst | setup/blank-project/setup-ContainerWeb.json | complete verification | |
| 71 | en/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWebService.rst | setup/blank-project/setup-ContainerWebService.json | complete verification | |
| 72 | en/application_framework/application_framework/cloud_native/containerize/index.rst | setup/cloud-native/containerize.json | complete verification | |
| 73 | en/application_framework/application_framework/cloud_native/distributed_tracing/aws_distributed_tracing.rst | setup/cloud-native/aws-distributed-tracing.json | complete verification | |
| 74 | en/application_framework/application_framework/cloud_native/distributed_tracing/azure_distributed_tracing.rst | setup/cloud-native/azure-distributed-tracing.json | complete verification | |
| 75 | en/application_framework/application_framework/cloud_native/distributed_tracing/index.rst | setup/cloud-native/distributed-tracing.json | complete verification | |
| 76 | en/application_framework/application_framework/cloud_native/index.rst | setup/cloud-native/cloud-native.json | complete verification | |
| 77 | en/application_framework/application_framework/configuration/index.rst | setup/configuration/configuration.json | complete verification | |
| 78 | en/application_framework/application_framework/handlers/batch/dbless_loop_handler.rst | processing-pattern/nablarch-batch/dbless-loop-handler.json | complete verification | |
| 79 | en/application_framework/application_framework/handlers/batch/index.rst | processing-pattern/nablarch-batch/handlers-batch.json | complete verification | |
| 80 | en/application_framework/application_framework/handlers/batch/loop_handler.rst | processing-pattern/nablarch-batch/loop-handler.json | complete verification | |
| 81 | en/application_framework/application_framework/handlers/batch/process_resident_handler.rst | processing-pattern/nablarch-batch/process-resident-handler.json | complete verification | |
| 82 | en/application_framework/application_framework/handlers/common/ServiceAvailabilityCheckHandler.rst | component/handlers/common/ServiceAvailabilityCheckHandler.json | complete verification | |
| 83 | en/application_framework/application_framework/handlers/common/database_connection_management_handler.rst | component/handlers/common/database-connection-management-handler.json | complete verification | |
| 84 | en/application_framework/application_framework/handlers/common/file_record_writer_dispose_handler.rst | component/handlers/common/file-record-writer-dispose-handler.json | complete verification | |
| 85 | en/application_framework/application_framework/handlers/common/global_error_handler.rst | component/handlers/common/global-error-handler.json | complete verification | |
| 86 | en/application_framework/application_framework/handlers/common/index.rst | component/handlers/common/common.json | complete verification | |
| 87 | en/application_framework/application_framework/handlers/common/permission_check_handler.rst | component/handlers/common/permission-check-handler.json | complete verification | |
| 88 | en/application_framework/application_framework/handlers/common/request_handler_entry.rst | component/handlers/common/request-handler-entry.json | complete verification | |
| 89 | en/application_framework/application_framework/handlers/common/request_path_java_package_mapping.rst | component/handlers/common/request-path-java-package-mapping.json | complete verification | |
| 90 | en/application_framework/application_framework/handlers/common/thread_context_clear_handler.rst | component/handlers/common/thread-context-clear-handler.json | complete verification | |
| 91 | en/application_framework/application_framework/handlers/common/thread_context_handler.rst | component/handlers/common/thread-context-handler.json | complete verification | |
| 92 | en/application_framework/application_framework/handlers/common/transaction_management_handler.rst | component/handlers/common/transaction-management-handler.json | complete verification | |
| 93 | en/application_framework/application_framework/handlers/http_messaging/http_messaging_error_handler.rst | component/handlers/http_messaging/http-messaging-error-handler.json | complete verification | |
| 94 | en/application_framework/application_framework/handlers/http_messaging/http_messaging_request_parsing_handler.rst | component/handlers/http_messaging/http-messaging-request-parsing-handler.json | complete verification | |
| 95 | en/application_framework/application_framework/handlers/http_messaging/http_messaging_response_building_handler.rst | component/handlers/http_messaging/http-messaging-response-building-handler.json | complete verification | |
| 96 | en/application_framework/application_framework/handlers/http_messaging/index.rst | component/handlers/http_messaging/http-messaging.json | complete verification | |
| 97 | en/application_framework/application_framework/handlers/mom_messaging/index.rst | component/handlers/mom_messaging/mom-messaging.json | complete verification | |
| 98 | en/application_framework/application_framework/handlers/mom_messaging/message_reply_handler.rst | component/handlers/mom_messaging/message-reply-handler.json | complete verification | |
| 99 | en/application_framework/application_framework/handlers/mom_messaging/message_resend_handler.rst | component/handlers/mom_messaging/message-resend-handler.json | complete verification | |
| 100 | en/application_framework/application_framework/handlers/mom_messaging/messaging_context_handler.rst | component/handlers/mom_messaging/messaging-context-handler.json | complete verification | |
| 101 | en/application_framework/application_framework/handlers/rest/body_convert_handler.rst | component/handlers/rest/body-convert-handler.json | complete verification | |
| 102 | en/application_framework/application_framework/handlers/rest/cors_preflight_request_handler.rst | component/handlers/rest/cors-preflight-request-handler.json | complete verification | |
| 103 | en/application_framework/application_framework/handlers/rest/index.rst | component/handlers/rest/rest.json | complete verification | |
| 104 | en/application_framework/application_framework/handlers/rest/jaxrs_access_log_handler.rst | component/handlers/rest/jaxrs-access-log-handler.json | complete verification | |
| 105 | en/application_framework/application_framework/handlers/rest/jaxrs_bean_validation_handler.rst | component/handlers/rest/jaxrs-bean-validation-handler.json | complete verification | |
| 106 | en/application_framework/application_framework/handlers/rest/jaxrs_response_handler.rst | component/handlers/rest/jaxrs-response-handler.json | complete verification | |
| 107 | en/application_framework/application_framework/handlers/standalone/data_read_handler.rst | component/handlers/standalone/data-read-handler.json | complete verification | |
| 108 | en/application_framework/application_framework/handlers/standalone/duplicate_process_check_handler.rst | component/handlers/standalone/duplicate-process-check-handler.json | complete verification | |
| 109 | en/application_framework/application_framework/handlers/standalone/multi_thread_execution_handler.rst | component/handlers/standalone/multi-thread-execution-handler.json | complete verification | |
| 110 | en/application_framework/application_framework/handlers/standalone/process_stop_handler.rst | component/handlers/standalone/process-stop-handler.json | complete verification | |
| 111 | en/application_framework/application_framework/handlers/web/HttpErrorHandler.rst | component/handlers/web/HttpErrorHandler.json | complete verification | |
| 112 | en/application_framework/application_framework/handlers/web/SessionStoreHandler.rst | component/handlers/web/SessionStoreHandler.json | complete verification | |
| 113 | en/application_framework/application_framework/handlers/web/csrf_token_verification_handler.rst | component/handlers/web/csrf-token-verification-handler.json | complete verification | |
| 114 | en/application_framework/application_framework/handlers/web/forwarding_handler.rst | component/handlers/web/forwarding-handler.json | complete verification | |
| 115 | en/application_framework/application_framework/handlers/web/health_check_endpoint_handler.rst | component/handlers/web/health-check-endpoint-handler.json | complete verification | |
| 116 | en/application_framework/application_framework/handlers/web/hot_deploy_handler.rst | component/handlers/web/hot-deploy-handler.json | complete verification | |
| 117 | en/application_framework/application_framework/handlers/web/http_access_log_handler.rst | component/handlers/web/http-access-log-handler.json | complete verification | |
| 118 | en/application_framework/application_framework/handlers/web/http_character_encoding_handler.rst | component/handlers/web/http-character-encoding-handler.json | complete verification | |
| 119 | en/application_framework/application_framework/handlers/web/http_request_java_package_mapping.rst | component/handlers/web/http-request-java-package-mapping.json | complete verification | |
| 120 | en/application_framework/application_framework/handlers/web/http_response_handler.rst | component/handlers/web/http-response-handler.json | complete verification | |
| 121 | en/application_framework/application_framework/handlers/web/http_rewrite_handler.rst | component/handlers/web/http-rewrite-handler.json | complete verification | |
| 122 | en/application_framework/application_framework/handlers/web/index.rst | component/handlers/web/web.json | complete verification | |
| 123 | en/application_framework/application_framework/handlers/web/keitai_access_handler.rst | component/handlers/web/keitai-access-handler.json | complete verification | |
| 124 | en/application_framework/application_framework/handlers/web/multipart_handler.rst | component/handlers/web/multipart-handler.json | complete verification | |
| 125 | en/application_framework/application_framework/handlers/web/nablarch_tag_handler.rst | component/handlers/web/nablarch-tag-handler.json | complete verification | |
| 126 | en/application_framework/application_framework/handlers/web/normalize_handler.rst | component/handlers/web/normalize-handler.json | complete verification | |
| 127 | en/application_framework/application_framework/handlers/web/post_resubmit_prevent_handler.rst | component/handlers/web/post-resubmit-prevent-handler.json | complete verification | |
| 128 | en/application_framework/application_framework/handlers/web/resource_mapping.rst | component/handlers/web/resource-mapping.json | complete verification | |
| 129 | en/application_framework/application_framework/handlers/web/secure_handler.rst | component/handlers/web/secure-handler.json | complete verification | |
| 130 | en/application_framework/application_framework/handlers/web/session_concurrent_access_handler.rst | component/handlers/web/session-concurrent-access-handler.json | complete verification | |
| 131 | en/application_framework/application_framework/libraries/authorization/permission_check.rst | component/libraries/authorization/permission-check.json | complete verification | |
| 132 | en/application_framework/application_framework/libraries/authorization/role_check.rst | component/libraries/authorization/role-check.json | complete verification | |
| 133 | en/application_framework/application_framework/libraries/bean_util.rst | component/libraries/bean-util.json | complete verification | |
| 134 | en/application_framework/application_framework/libraries/code.rst | component/libraries/code.json | complete verification | |
| 135 | en/application_framework/application_framework/libraries/data_converter.rst | component/libraries/data-converter.json | complete verification | |
| 136 | en/application_framework/application_framework/libraries/data_io/data_bind.rst | component/libraries/data_io/data-bind.json | complete verification | |
| 137 | en/application_framework/application_framework/libraries/data_io/data_format.rst | component/libraries/data_io/data-format.json | complete verification | |
| 138 | en/application_framework/application_framework/libraries/data_io/data_format/format_definition.rst | component/libraries/data_io/data_format/format-definition.json | complete verification | |
| 139 | en/application_framework/application_framework/libraries/data_io/data_format/multi_format_example.rst | component/libraries/data_io/data_format/multi-format-example.json | complete verification | |
| 140 | en/application_framework/application_framework/libraries/data_io/functional_comparison.rst | component/libraries/data_io/functional-comparison.json | complete verification | |
| 141 | en/application_framework/application_framework/libraries/database/database.rst | component/libraries/database/database.json | complete verification | |
| 142 | en/application_framework/application_framework/libraries/database/functional_comparison.rst | component/libraries/database/functional-comparison.json | complete verification | |
| 143 | en/application_framework/application_framework/libraries/database/generator.rst | component/libraries/database/generator.json | complete verification | |
| 144 | en/application_framework/application_framework/libraries/database/universal_dao.rst | component/libraries/database/universal-dao.json | complete verification | |
| 145 | en/application_framework/application_framework/libraries/database_management.rst | component/libraries/database-management.json | complete verification | |
| 146 | en/application_framework/application_framework/libraries/date.rst | component/libraries/date.json | complete verification | |
| 147 | en/application_framework/application_framework/libraries/db_double_submit.rst | component/libraries/db-double-submit.json | complete verification | |
| 148 | en/application_framework/application_framework/libraries/exclusive_control.rst | component/libraries/exclusive-control.json | complete verification | |
| 149 | en/application_framework/application_framework/libraries/file_path_management.rst | component/libraries/file-path-management.json | complete verification | |
| 150 | en/application_framework/application_framework/libraries/format.rst | component/libraries/format.json | complete verification | |
| 151 | en/application_framework/application_framework/libraries/index.rst | component/libraries/libraries.json | complete verification | |
| 152 | en/application_framework/application_framework/libraries/log.rst | component/libraries/log.json | complete verification | |
| 153 | en/application_framework/application_framework/libraries/log/failure_log.rst | component/libraries/log/failure-log.json | complete verification | |
| 154 | en/application_framework/application_framework/libraries/log/http_access_log.rst | component/libraries/log/http-access-log.json | complete verification | |
| 155 | en/application_framework/application_framework/libraries/log/jaxrs_access_log.rst | component/libraries/log/jaxrs-access-log.json | complete verification | |
| 156 | en/application_framework/application_framework/libraries/log/messaging_log.rst | component/libraries/log/messaging-log.json | complete verification | |
| 157 | en/application_framework/application_framework/libraries/log/performance_log.rst | component/libraries/log/performance-log.json | complete verification | |
| 158 | en/application_framework/application_framework/libraries/log/sql_log.rst | component/libraries/log/sql-log.json | complete verification | |
| 159 | en/application_framework/application_framework/libraries/mail.rst | component/libraries/mail.json | complete verification | |
| 160 | en/application_framework/application_framework/libraries/message.rst | component/libraries/message.json | complete verification | |
| 161 | en/application_framework/application_framework/libraries/permission_check.rst | component/libraries/permission-check.json | complete verification | |
| 162 | en/application_framework/application_framework/libraries/repository.rst | component/libraries/repository.json | complete verification | |
| 163 | en/application_framework/application_framework/libraries/service_availability.rst | component/libraries/service-availability.json | complete verification | |
| 164 | en/application_framework/application_framework/libraries/session_store.rst | component/libraries/session-store.json | complete verification | |
| 165 | en/application_framework/application_framework/libraries/session_store/create_example.rst | component/libraries/session_store/create-example.json | complete verification | |
| 166 | en/application_framework/application_framework/libraries/session_store/update_example.rst | component/libraries/session_store/update-example.json | complete verification | |
| 167 | en/application_framework/application_framework/libraries/stateless_web_app.rst | component/libraries/stateless-web-app.json | complete verification | |
| 168 | en/application_framework/application_framework/libraries/static_data_cache.rst | component/libraries/static-data-cache.json | complete verification | |
| 169 | en/application_framework/application_framework/libraries/system_messaging.rst | component/libraries/system-messaging.json | complete verification | |
| 170 | en/application_framework/application_framework/libraries/system_messaging/http_system_messaging.rst | component/libraries/system_messaging/http-system-messaging.json | complete verification | |
| 171 | en/application_framework/application_framework/libraries/system_messaging/mom_system_messaging.rst | component/libraries/system_messaging/mom-system-messaging.json | complete verification | |
| 172 | en/application_framework/application_framework/libraries/tag.rst | component/libraries/tag.json | complete verification | |
| 173 | en/application_framework/application_framework/libraries/tag/tag_reference.rst | component/libraries/tag/tag-reference.json | complete verification | |
| 174 | en/application_framework/application_framework/libraries/transaction.rst | component/libraries/transaction.json | complete verification | |
| 175 | en/application_framework/application_framework/libraries/utility.rst | component/libraries/utility.json | complete verification | |
| 176 | en/application_framework/application_framework/libraries/validation.rst | component/libraries/validation.json | complete verification | |
| 177 | en/application_framework/application_framework/libraries/validation/bean_validation.rst | component/libraries/validation/bean-validation.json | complete verification | |
| 178 | en/application_framework/application_framework/libraries/validation/functional_comparison.rst | component/libraries/validation/functional-comparison.json | complete verification | |
| 179 | en/application_framework/application_framework/libraries/validation/nablarch_validation.rst | component/libraries/validation/nablarch-validation.json | complete verification | |
| 180 | en/application_framework/application_framework/messaging/db/application_design.rst | processing-pattern/db-messaging/application-design.json | complete verification | |
| 181 | en/application_framework/application_framework/messaging/db/architecture.rst | processing-pattern/db-messaging/architecture.json | complete verification | |
| 182 | en/application_framework/application_framework/messaging/db/feature_details.rst | processing-pattern/db-messaging/feature-details.json | complete verification | |
| 183 | en/application_framework/application_framework/messaging/db/feature_details/error_processing.rst | processing-pattern/db-messaging/error-processing.json | complete verification | |
| 184 | en/application_framework/application_framework/messaging/db/feature_details/multiple_process.rst | processing-pattern/db-messaging/multiple-process.json | complete verification | |
| 185 | en/application_framework/application_framework/messaging/db/getting_started.rst | processing-pattern/db-messaging/getting-started.json | complete verification | |
| 186 | en/application_framework/application_framework/messaging/db/getting_started/table_queue.rst | processing-pattern/db-messaging/table-queue.json | complete verification | |
| 187 | en/application_framework/application_framework/messaging/db/index.rst | processing-pattern/db-messaging/db.json | complete verification | |
| 188 | en/application_framework/application_framework/messaging/mom/application_design.rst | processing-pattern/mom-messaging/application-design.json | complete verification | |
| 189 | en/application_framework/application_framework/messaging/mom/architecture.rst | processing-pattern/mom-messaging/architecture.json | complete verification | |
| 190 | en/application_framework/application_framework/messaging/mom/feature_details.rst | processing-pattern/mom-messaging/feature-details.json | complete verification | |
| 191 | en/application_framework/application_framework/messaging/mom/getting_started.rst | processing-pattern/mom-messaging/getting-started.json | complete verification | |
| 192 | en/application_framework/application_framework/messaging/mom/index.rst | processing-pattern/mom-messaging/mom.json | complete verification | |
| 193 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeAvailableCharacters.rst | setup/setting-guide/CustomizeAvailableCharacters.json | complete verification | |
| 194 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeMessageIDAndMessage.rst | setup/setting-guide/CustomizeMessageIDAndMessage.json | complete verification | |
| 195 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/CustomizeSystemTableName.rst | setup/setting-guide/CustomizeSystemTableName.json | complete verification | |
| 196 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/config_key_naming.rst | setup/setting-guide/config-key-naming.json | complete verification | |
| 197 | en/application_framework/application_framework/setting_guide/CustomizingConfigurations/index.rst | setup/setting-guide/CustomizingConfigurations.json | complete verification | |
| 198 | en/application_framework/application_framework/setting_guide/ManagingEnvironmentalConfiguration/index.rst | setup/setting-guide/ManagingEnvironmentalConfiguration.json | complete verification | |
| 199 | en/application_framework/application_framework/setting_guide/index.rst | setup/setting-guide/setting-guide.json | complete verification | |
| 200 | en/application_framework/application_framework/web_service/functional_comparison.rst | processing-pattern/restful-web-service/functional-comparison.json | complete verification | |
| 201 | en/application_framework/application_framework/web_service/http_messaging/application_design.rst | processing-pattern/restful-web-service/http_messaging/application-design.json | complete verification | |
| 202 | en/application_framework/application_framework/web_service/http_messaging/architecture.rst | processing-pattern/restful-web-service/http_messaging/architecture.json | complete verification | |
| 203 | en/application_framework/application_framework/web_service/http_messaging/feature_details.rst | processing-pattern/restful-web-service/http_messaging/feature-details.json | complete verification | |
| 204 | en/application_framework/application_framework/web_service/http_messaging/getting_started/getting_started.rst | processing-pattern/restful-web-service/http_messaging/getting-started.json | complete verification | |
| 205 | en/application_framework/application_framework/web_service/http_messaging/getting_started/save/index.rst | processing-pattern/restful-web-service/http_messaging/save.json | complete verification | |
| 206 | en/application_framework/application_framework/web_service/http_messaging/index.rst | processing-pattern/restful-web-service/http_messaging/http-messaging.json | complete verification | |
| 207 | en/application_framework/application_framework/web_service/index.rst | processing-pattern/restful-web-service/web-service.json | complete verification | |
| 208 | en/application_framework/application_framework/web_service/rest/application_design.rst | processing-pattern/restful-web-service/rest/application-design.json | complete verification | |
| 209 | en/application_framework/application_framework/web_service/rest/architecture.rst | processing-pattern/restful-web-service/rest/architecture.json | complete verification | |
| 210 | en/application_framework/application_framework/web_service/rest/feature_details.rst | processing-pattern/restful-web-service/rest/feature-details.json | complete verification | |
| 211 | en/application_framework/application_framework/web_service/rest/feature_details/resource_signature.rst | processing-pattern/restful-web-service/rest/resource-signature.json | complete verification | |
| 212 | en/application_framework/application_framework/web_service/rest/getting_started/create/index.rst | processing-pattern/restful-web-service/rest/create.json | complete verification | |
| 213 | en/application_framework/application_framework/web_service/rest/getting_started/index.rst | processing-pattern/restful-web-service/rest/getting-started.json | complete verification | |
| 214 | en/application_framework/application_framework/web_service/rest/getting_started/search/index.rst | processing-pattern/restful-web-service/rest/search.json | complete verification | |
| 215 | en/application_framework/application_framework/web_service/rest/getting_started/update/index.rst | processing-pattern/restful-web-service/rest/update.json | complete verification | |
| 216 | en/application_framework/application_framework/web_service/rest/index.rst | processing-pattern/restful-web-service/rest/rest.json | complete verification | |
| 217 | en/development_tools/java_static_analysis/index.rst | development-tools/java-static-analysis/java-static-analysis.json | complete verification | |
| 218 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/01_entityUnitTestWithBeanValidation.rst | development-tools/testing-framework/01_ClassUnitTest/01_entityUnitTest/01-entityUnitTestWithBeanValidation.json | complete verification | |
| 219 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/02_entityUnitTestWithNablarchValidation.rst | development-tools/testing-framework/01_ClassUnitTest/01_entityUnitTest/02-entityUnitTestWithNablarchValidation.json | complete verification | |
| 220 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/index.rst | development-tools/testing-framework/01_ClassUnitTest/01_entityUnitTest/01-entityUnitTest.json | complete verification | |
| 221 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/02_componentUnitTest.rst | development-tools/testing-framework/05_UnitTestGuide/01_ClassUnitTest/02-componentUnitTest.json | complete verification | |
| 222 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/index.rst | development-tools/testing-framework/05_UnitTestGuide/01_ClassUnitTest/01-ClassUnitTest.json | complete verification | |
| 223 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/batch.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/batch.json | complete verification | |
| 224 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/delayed_receive.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/delayed-receive.json | complete verification | |
| 225 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/delayed_send.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/delayed-send.json | complete verification | |
| 226 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/duplicate_form_submission.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/duplicate-form-submission.json | complete verification | |
| 227 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/fileupload.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/fileupload.json | complete verification | |
| 228 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/http_real.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/http-real.json | complete verification | |
| 229 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/http_send_sync.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/http-send-sync.json | complete verification | |
| 230 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/index.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/02-RequestUnitTest.json | complete verification | |
| 231 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/mail.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/mail.json | complete verification | |
| 232 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/real.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/real.json | complete verification | |
| 233 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/rest.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/rest.json | complete verification | |
| 234 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/send_sync.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/send-sync.json | complete verification | |
| 235 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/batch.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/batch.json | complete verification | |
| 236 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/delayed_receive.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/delayed-receive.json | complete verification | |
| 237 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/delayed_send.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/delayed-send.json | complete verification | |
| 238 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/http_send_sync.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/http-send-sync.json | complete verification | |
| 239 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/index.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/03-DealUnitTest.json | complete verification | |
| 240 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/real.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/real.json | complete verification | |
| 241 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/rest.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/rest.json | complete verification | |
| 242 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/03_DealUnitTest/send_sync.rst | development-tools/testing-framework/05_UnitTestGuide/03_DealUnitTest/send-sync.json | complete verification | |
| 243 | en/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/index.rst | development-tools/testing-framework/05_UnitTestGuide/05-UnitTestGuide.json | complete verification | |
| 244 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/01_Abstract.rst | development-tools/testing-framework/06_TestFWGuide/01-Abstract.json | complete verification | |
| 245 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/02_DbAccessTest.rst | development-tools/testing-framework/06_TestFWGuide/02-DbAccessTest.json | complete verification | |
| 246 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/02_RequestUnitTest.rst | development-tools/testing-framework/06_TestFWGuide/02-RequestUnitTest.json | complete verification | |
| 247 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/03_Tips.rst | development-tools/testing-framework/06_TestFWGuide/03-Tips.json | complete verification | |
| 248 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/04_MasterDataRestore.rst | development-tools/testing-framework/06_TestFWGuide/04-MasterDataRestore.json | complete verification | |
| 249 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/JUnit5_Extension.rst | development-tools/testing-framework/06_TestFWGuide/JUnit5-Extension.json | complete verification | |
| 250 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_batch.rst | development-tools/testing-framework/06_TestFWGuide/RequestUnitTest-batch.json | complete verification | |
| 251 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_http_send_sync.rst | development-tools/testing-framework/06_TestFWGuide/RequestUnitTest-http-send-sync.json | complete verification | |
| 252 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_real.rst | development-tools/testing-framework/06_TestFWGuide/RequestUnitTest-real.json | complete verification | |
| 253 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_rest.rst | development-tools/testing-framework/06_TestFWGuide/RequestUnitTest-rest.json | complete verification | |
| 254 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_send_sync.rst | development-tools/testing-framework/06_TestFWGuide/RequestUnitTest-send-sync.json | complete verification | |
| 255 | en/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/index.rst | development-tools/testing-framework/06_TestFWGuide/06-TestFWGuide.json | complete verification | |
| 256 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/01_HttpDumpTool.rst | development-tools/testing-framework/08_TestTools/01_HttpDumpTool/01-HttpDumpTool-overview.json | complete verification | |
| 257 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/02_SetUpHttpDumpTool.rst | development-tools/testing-framework/08_TestTools/01_HttpDumpTool/02-SetUpHttpDumpTool.json | complete verification | |
| 258 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/01_HttpDumpTool/index.rst | development-tools/testing-framework/08_TestTools/01_HttpDumpTool/01-HttpDumpTool.json | complete verification | |
| 259 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/01_MasterDataSetupTool.rst | development-tools/testing-framework/08_TestTools/02_MasterDataSetup/01-MasterDataSetupTool.json | complete verification | |
| 260 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/02_ConfigMasterDataSetupTool.rst | development-tools/testing-framework/08_TestTools/02_MasterDataSetup/02-ConfigMasterDataSetupTool.json | complete verification | |
| 261 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/02_MasterDataSetup/index.rst | development-tools/testing-framework/08_TestTools/02_MasterDataSetup/02-MasterDataSetup.json | complete verification | |
| 262 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/03_HtmlCheckTool/index.rst | development-tools/testing-framework/08_TestTools/03_HtmlCheckTool/03-HtmlCheckTool.json | complete verification | |
| 263 | en/development_tools/testing_framework/guide/development_guide/08_TestTools/index.rst | development-tools/testing-framework/08_TestTools/08-TestTools.json | complete verification | |
| 264 | en/development_tools/testing_framework/index.rst | development-tools/testing-framework/testing-framework.json | complete verification | |
| 265 | en/development_tools/toolbox/JspStaticAnalysis/01_JspStaticAnalysis.rst | development-tools/toolbox/JspStaticAnalysis/01-JspStaticAnalysis.json | complete verification | |
| 266 | en/development_tools/toolbox/JspStaticAnalysis/02_JspStaticAnalysisInstall.rst | development-tools/toolbox/JspStaticAnalysis/02-JspStaticAnalysisInstall.json | complete verification | |
| 267 | en/development_tools/toolbox/JspStaticAnalysis/index.rst | development-tools/toolbox/JspStaticAnalysis/JspStaticAnalysis.json | complete verification | |
| 268 | en/development_tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.rst | development-tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.json | complete verification | |
| 269 | en/development_tools/toolbox/SqlExecutor/SqlExecutor.rst | development-tools/toolbox/SqlExecutor/SqlExecutor.json | complete verification | |
| 270 | en/development_tools/toolbox/index.rst | development-tools/toolbox/toolbox.json | complete verification | |
| 271 | ja/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/double_transmission.rst | development-tools/testing-framework/05_UnitTestGuide/02_RequestUnitTest/double-transmission.json | complete verification | |
| 272 | ja/releases/index.rst | about/release-notes/releases.json | complete verification | |

**Instructions**:
- Verify path conversion rules are followed
- Mark ✓ if correct, ✗ if incorrect (note correct path)

