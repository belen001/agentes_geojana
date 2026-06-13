from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from fabrica_agentes_ia.core.evidence import keyword_select, load_evidence, render_pack
from fabrica_agentes_ia.core.natural_language import build_natural_task_package
from fabrica_agentes_ia.harness import validate_run
from fabrica_agentes_ia.orchestrator import Orchestrator


DEFAULT_EVIDENCE = Path("fabrica_agentes_ia") / "knowledge_base" / "evidence.jsonl"
DEFAULT_REPOSITORIES = Path("fabrica_agentes_ia") / "config" / "repositories.json"
DEFAULT_MEMORY = Path("fabrica_agentes_ia") / "memory" / "natural_tasks.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(prog="fabrica-agentes-ia")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan-docs", help="Procesa la carpeta de documentos y crea evidencia.")
    scan.add_argument("--docs", default="documentos")
    scan.add_argument("--run-dir", default=None)

    run = sub.add_parser("run", help="Ejecuta la fabrica sobre una tarea.")
    run.add_argument("--task", required=True, help="Texto de tarea o ruta a archivo .md/.txt")
    run.add_argument("--docs", default="documentos")
    run.add_argument("--evidence", default=None, help="Ruta a evidence.jsonl ya generado.")
    run.add_argument(
        "--use-packaged-context",
        action="store_true",
        help="Usa fabrica_agentes_ia/knowledge_base/evidence.jsonl sin reingestar documentos.",
    )
    run.add_argument("--run-dir", default=None)
    run.add_argument("--max-context-tokens", type=int, default=6000)

    context = sub.add_parser("context", help="Genera un paquete de contexto para otro agente.")
    context.add_argument("--task", required=True, help="Texto de tarea o ruta a archivo .md/.txt")
    context.add_argument("--evidence", default=str(DEFAULT_EVIDENCE))
    context.add_argument("--out", default="selected_context.md")
    context.add_argument("--max-context-tokens", type=int, default=6000)

    ask = sub.add_parser("ask", help="Prepara una tarea escrita en lenguaje natural.")
    ask.add_argument("request", help="Solicitud completa en lenguaje natural.")
    ask.add_argument("--evidence", default=str(DEFAULT_EVIDENCE))
    ask.add_argument("--repositories", default=str(DEFAULT_REPOSITORIES))
    ask.add_argument("--out-dir", default=None)
    ask.add_argument("--repo", default=None, help="Fuerza repositorio objetivo.")
    ask.add_argument("--mode", default=None, help="Fuerza modo: implement, review, plan, test, debug, docs o context.")
    ask.add_argument("--no-memory", action="store_true", help="No registra la solicitud en memory/natural_tasks.jsonl.")
    ask.add_argument("--max-context-tokens", type=int, default=6000)

    check = sub.add_parser("validate", help="Valida trazabilidad, citas y presupuesto.")
    check.add_argument("--run-dir", required=True)

    args = parser.parse_args()

    if args.command == "scan-docs":
        run_dir = _run_dir(args.run_dir)
        evidence_path = Orchestrator(run_dir).scan_documents(Path(args.docs))
        print(json.dumps({"run_dir": str(run_dir), "evidence_path": str(evidence_path)}, indent=2))
        return

    if args.command == "run":
        run_dir = _run_dir(args.run_dir)
        orchestrator = Orchestrator(run_dir)
        evidence_path = _resolve_evidence(args, orchestrator)
        outputs = orchestrator.run_task(_read_task(args.task), evidence_path, args.max_context_tokens)
        validation = validate_run(run_dir)
        print(
            json.dumps(
                {
                    "run_dir": str(run_dir),
                    "agents": [output.agent_name for output in outputs],
                    "validation": validation,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "context":
        task = _read_task(args.task)
        evidence_path = Path(args.evidence)
        evidence = load_evidence(evidence_path)
        selected = keyword_select(task, evidence, max_tokens=args.max_context_tokens)
        out = Path(args.out)
        out.write_text(render_pack(selected), encoding="utf-8")
        print(
            json.dumps(
                {
                    "out": str(out),
                    "evidence_path": str(evidence_path),
                    "selected_evidence_ids": [item.evidence_id for item in selected],
                    "selected_count": len(selected),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "ask":
        out_dir = Path(args.out_dir) if args.out_dir else _run_dir(None) / "natural_task"
        manifest = build_natural_task_package(
            request_text=args.request,
            evidence_path=Path(args.evidence),
            out_dir=out_dir,
            repositories_config=Path(args.repositories),
            max_context_tokens=args.max_context_tokens,
            current_dir=Path.cwd(),
            repo_override=args.repo,
            mode_override=args.mode,
            memory_path=None if args.no_memory else DEFAULT_MEMORY,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

    if args.command == "validate":
        print(json.dumps(validate_run(Path(args.run_dir)), ensure_ascii=False, indent=2))


def _run_dir(value: str | None) -> Path:
    if value:
        return Path(value)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path("fabrica_agentes_ia") / "runs" / stamp


def _read_task(value: str) -> str:
    path = Path(value)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return value


def _resolve_evidence(args: argparse.Namespace, orchestrator: Orchestrator) -> Path:
    if args.evidence:
        evidence_path = Path(args.evidence)
        if not evidence_path.exists():
            raise FileNotFoundError(f"No existe evidence.jsonl: {evidence_path}")
        return evidence_path

    if args.use_packaged_context:
        if not DEFAULT_EVIDENCE.exists():
            raise FileNotFoundError(
                f"No existe la base de conocimiento portable: {DEFAULT_EVIDENCE}. "
                "Ejecuta scan-docs o copia knowledge_base/evidence.jsonl."
            )
        return DEFAULT_EVIDENCE

    return orchestrator.scan_documents(Path(args.docs))


if __name__ == "__main__":
    main()
