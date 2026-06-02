"""Unit tests for scripts.common.javadoc_fqcn.class_fqcn.

TDD: tests written first (RED), then implement (GREEN).
"""
from __future__ import annotations

import pytest


class TestClassFqcn:
    """class_fqcn() normalises a raw :java:extdoc: FQCN to a class-level FQCN."""

    def _fn(self, fqcn):
        from scripts.common.javadoc_fqcn import class_fqcn
        return class_fqcn(fqcn)

    # --- plain class (no change) ---

    def test_plain_class(self):
        assert self._fn("nablarch.common.dao.UniversalDao") == \
            "nablarch.common.dao.UniversalDao"

    def test_short_class(self):
        assert self._fn("nablarch.fw.Result") == "nablarch.fw.Result"

    # --- Step 1: #method suffix ---

    def test_hash_method_suffix(self):
        assert self._fn("nablarch.common.dao.UniversalDao#findById") == \
            "nablarch.common.dao.UniversalDao"

    # --- Step 2: .<init>(...) constructor ---

    def test_init_constructor(self):
        assert self._fn(
            "nablarch.fw.messaging.MessageSenderSettings.<init>(java.lang.String)"
        ) == "nablarch.fw.messaging.MessageSenderSettings"

    # --- Step 3: method-level RST dot-notation (lowercase method name + parens) ---

    def test_method_dot_no_args(self):
        assert self._fn("nablarch.common.dao.UniversalDao.exists()") == \
            "nablarch.common.dao.UniversalDao"

    def test_method_dot_single_arg(self):
        assert self._fn(
            "nablarch.common.dao.UniversalDao.batchDelete(java.util.List)"
        ) == "nablarch.common.dao.UniversalDao"

    def test_method_dot_multi_arg(self):
        assert self._fn(
            "nablarch.common.dao.UniversalDao.findAllBySqlFile(java.lang.Class,java.lang.String,java.lang.Object)"
        ) == "nablarch.common.dao.UniversalDao"

    def test_method_dot_varargs(self):
        assert self._fn(
            "nablarch.core.validation.ee.ValidatorUtil.validate(java.lang.Object,java.lang.String...)"
        ) == "nablarch.core.validation.ee.ValidatorUtil"

    def test_method_dot_array_arg(self):
        # java.lang.String[] — bracket in args, not a paren-before-method issue
        assert self._fn(
            "nablarch.common.code.schema.CodePatternSchema.setPatternColumnNames(java.lang.String[])"
        ) == "nablarch.common.code.schema.CodePatternSchema"

    def test_method_dot_deeply_nested(self):
        # method in deeply nested package
        assert self._fn(
            "nablarch.core.validation.validator.unicode.SystemCharValidator.setAllowSurrogatePair(boolean)"
        ) == "nablarch.core.validation.validator.unicode.SystemCharValidator"

    def test_method_with_generic_type_arg(self):
        # Generic type param 'D' — uppercase segment before '(' is not a class here
        # nablarch.fw.action.BatchActionBase.transactionFailure(D,nablarch.fw.ExecutionContext)
        # prefix before '(': ...BatchActionBase.transactionFailure
        # last segment: 'transactionFailure' -> lowercase start -> strip to BatchActionBase
        assert self._fn(
            "nablarch.fw.action.BatchActionBase.transactionFailure(D,nablarch.fw.ExecutionContext)"
        ) == "nablarch.fw.action.BatchActionBase"

    # --- Step 4: inner class (both last two segments uppercase) ---

    def test_inner_class_simple(self):
        assert self._fn("nablarch.fw.Result.Error") == "nablarch.fw.Result"

    def test_inner_class_multi_status(self):
        assert self._fn("nablarch.fw.Result.MultiStatus") == "nablarch.fw.Result"

    def test_inner_class_builder(self):
        assert self._fn("nablarch.core.beans.CopyOptions.Builder") == \
            "nablarch.core.beans.CopyOptions"

    def test_inner_class_no_more_record(self):
        assert self._fn("nablarch.fw.DataReader.NoMoreRecord") == \
            "nablarch.fw.DataReader"

    def test_inner_class_process_stop(self):
        assert self._fn("nablarch.fw.handler.ProcessStopHandler.ProcessStop") == \
            "nablarch.fw.handler.ProcessStopHandler"

    def test_inner_class_with_method(self):
        # Double inner class + method:
        # BulkValidator.ErrorHandlingBulkValidator.validateWith(...)
        # After Step 3 (method strip): BulkValidator.ErrorHandlingBulkValidator
        # After Step 4 (inner strip): BulkValidator
        assert self._fn(
            "nablarch.fw.web.upload.util.BulkValidator.ErrorHandlingBulkValidator.validateWith(java.lang.Class,java.lang.String)"
        ) == "nablarch.fw.web.upload.util.BulkValidator"

    # --- Step 5: package-level (last segment lowercase, no parens) -> None ---

    def test_package_level_returns_none(self):
        assert self._fn("nablarch.common.code.validator") is None

    def test_package_level_ee_returns_none(self):
        assert self._fn("nablarch.common.code.validator.ee") is None

    def test_package_level_multi_segment(self):
        assert self._fn("nablarch.core.dataformat.convertor.datatype") is None

    # --- JDK standard classes pass through unchanged (not None) ---

    def test_java_class_passes_through(self):
        # java.* / jakarta.* / javax.* are NOT None — caller filters them separately
        assert self._fn("java.lang.String") == "java.lang.String"

    def test_jakarta_class_passes_through(self):
        assert self._fn("jakarta.servlet.http.HttpServletRequest") == \
            "jakarta.servlet.http.HttpServletRequest"
