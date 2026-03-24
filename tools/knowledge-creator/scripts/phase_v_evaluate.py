"""Phase V: Quality Evaluation

Collects findings data, runs CC sub-agents for user impact assessment,
and generates improvement proposals.
"""

import os
import json
import glob
from common import load_json, read_file, run_claude as _default_run_claude, write_json
from logger import get_logger

EVALUATE_SCHEMA = {
    "type": "object",
    "required": ["file_id", "user_impact", "needs_improvement", "reason", "findings_assessment"],
    "properties": {
        "file_id": {"type": "string"},
        "user_impact": {"type": "string", "enum": ["high", "medium", "low", "none"]},
        "needs_improvement": {"type": "boolean"},
        "reason": {"type": "string"},
        "findings_assessment": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "location", "impact", "justification"],
                "properties": {
                    "category": {"type": "string"},
                    "location": {"type": "string"},
                    "impact": {"type": "string"},
                    "justification": {"type": "string"}
                }
            }
        }
    }
}

INTEGRATE_SCHEMA = {
    "type": "object",
    "required": ["proposals"],
    "properties": {
        "proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "purpose", "target_files", "user_impact", "body"],
                "properties": {
                    "title": {"type": "string"},
                    "purpose": {"type": "string"},
                    "target_files": {"type": "array", "items": {"type": "string"}},
                    "user_impact": {"type": "string"},
                    "body": {"type": "string"}
                }
            }
        }
    }
}


class PhaseVEvaluate:
    def __init__(self, ctx, run_claude_fn=None):
        self.ctx = ctx
        self.run_claude = run_claude_fn or _default_run_claude
        self.logger = get_logger()
        self.evaluate_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/evaluate.md"
        )
        self.integrate_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/evaluate_integrate.md"
        )

    @staticmethod
    def collect_findings_summary(findings_dir, max_rounds):
        summary = {"rounds": {}, "final": None}
        final_round = max_rounds + 1
        for rn in range(1, final_round + 1):
            paths = glob.glob(os.path.join(findings_dir, f"*_r{rn}.json"))
            total = critical = minor = 0
            by_category = {}
            for path in paths:
                try:
                    data = json.load(open(path, 'r', encoding='utf-8'))
                except (json.JSONDecodeError, OSError):
                    continue
                for f in data.get("findings", []):
                    total += 1
                    if f.get("severity") == "critical":
                        critical += 1
                    else:
                        minor += 1
                    cat = f.get("category", "unknown")
                    by_category[cat] = by_category.get(cat, 0) + 1
            summary["rounds"][rn] = {
                "total": total, "critical": critical, "minor": minor,
                "by_category": by_category,
            }
        summary["final"] = summary["rounds"].get(final_round, {})
        return summary

    @staticmethod
    def cross_tabulate(findings_dir, catalog, final_round):
        file_category_map = {f["id"]: f.get("category", "unknown") for f in catalog.get("files", [])}
        cross = {}
        paths = glob.glob(os.path.join(findings_dir, f"*_r{final_round}.json"))
        for path in paths:
            try:
                data = json.load(open(path, 'r', encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                continue
            fid = data.get("file_id", "")
            file_cat = file_category_map.get(fid, "unknown")
            cross.setdefault(file_cat, {})
            for f in data.get("findings", []):
                cat = f.get("category", "unknown")
                cross[file_cat][cat] = cross[file_cat].get(cat, 0) + 1
        return cross

    @staticmethod
    def file_concentration(findings_dir, final_round, top_n=10):
        counts = []
        paths = glob.glob(os.path.join(findings_dir, f"*_r{final_round}.json"))
        for path in paths:
            try:
                data = json.load(open(path, 'r', encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                continue
            findings = data.get("findings", [])
            if findings:
                cats = [f.get("category", "") for f in findings]
                counts.append({
                    "file_id": data.get("file_id", ""),
                    "count": len(findings),
                    "categories": list(set(cats)),
                })
        counts.sort(key=lambda x: -x["count"])
        return counts[:top_n]

    def evaluate_file(self, file_id, findings, rst_content, json_content, d_logs, e_logs):
        prompt = self.evaluate_template
        prompt = prompt.replace("{FILE_ID}", file_id)
        prompt = prompt.replace("{FINDINGS}", json.dumps(findings, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{RST_CONTENT}", rst_content)
        prompt = prompt.replace("{JSON_CONTENT}", json_content)
        prompt = prompt.replace("{EXECUTION_LOGS}", f"--- Phase D logs ---\n{d_logs}\n--- Phase E logs ---\n{e_logs}")
        result = self.run_claude(
            prompt=prompt, json_schema=EVALUATE_SCHEMA,
            log_dir=f"{self.ctx.log_dir}/phase-v/evaluations", file_id=file_id,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None

    def integrate_proposals(self, file_evaluations, findings_summary):
        prompt = self.integrate_template
        prompt = prompt.replace("{FILE_EVALUATIONS}", json.dumps(file_evaluations, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{FINDINGS_SUMMARY}", json.dumps(findings_summary, ensure_ascii=False, indent=2))
        result = self.run_claude(
            prompt=prompt, json_schema=INTEGRATE_SCHEMA,
            log_dir=f"{self.ctx.log_dir}/phase-v/integration", file_id="integration",
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None

    def run(self, final_round):
        self.logger.info("\n📊Phase V: Quality Evaluation")
        catalog = load_json(self.ctx.classified_list_path)

        self.logger.info("   V1: Collecting findings summary...")
        summary = self.collect_findings_summary(self.ctx.findings_dir, self.ctx.max_rounds)
        cross = self.cross_tabulate(self.ctx.findings_dir, catalog, final_round)
        concentration = self.file_concentration(self.ctx.findings_dir, final_round)
        fact_data = {"summary": summary, "cross_tabulation": cross, "file_concentration": concentration}

        self.logger.info("   V2: Evaluating files with residual findings...")
        final_findings_paths = glob.glob(
            os.path.join(self.ctx.findings_dir, f"*_r{final_round}.json")
        )
        files_with_issues = []
        for path in final_findings_paths:
            data = load_json(path)
            if data.get("status") == "has_issues":
                files_with_issues.append(data)

        file_evaluations = []
        if files_with_issues:
            file_map = {f["id"]: f for f in catalog.get("files", [])}
            for fdata in files_with_issues:
                fid = fdata["file_id"]
                fi = file_map.get(fid)
                if not fi:
                    continue
                rst_path = f"{self.ctx.repo}/{fi['source_path']}"
                json_path = f"{self.ctx.knowledge_cache_dir}/{fi['output_path']}"
                rst_content = read_file(rst_path) if os.path.exists(rst_path) else ""
                json_content = read_file(json_path) if os.path.exists(json_path) else ""
                d_logs = self._read_latest_log(self.ctx.phase_d_executions_dir, fid)
                e_logs = self._read_latest_log(self.ctx.phase_e_executions_dir, fid)
                eval_result = self.evaluate_file(fid, fdata["findings"], rst_content, json_content, d_logs, e_logs)
                if eval_result:
                    eval_result["category"] = fi.get("category", "unknown")
                    file_evaluations.append(eval_result)

        proposals = None
        if file_evaluations:
            self.logger.info("   V3: Generating improvement proposals...")
            proposals = self.integrate_proposals(file_evaluations, fact_data)

        result = {"fact_data": fact_data, "file_evaluations": file_evaluations, "proposals": proposals}
        os.makedirs(f"{self.ctx.log_dir}/phase-v", exist_ok=True)
        write_json(f"{self.ctx.log_dir}/phase-v/result.json", result)
        return result

    def _read_latest_log(self, executions_dir, file_id):
        if not os.path.exists(executions_dir):
            return ""
        logs = sorted(glob.glob(os.path.join(executions_dir, f"{file_id}_*.json")), reverse=True)
        if not logs:
            return ""
        try:
            data = load_json(logs[0])
            return json.dumps(data, ensure_ascii=False, indent=2)[:5000]
        except Exception:
            return ""
