#!/usr/bin/env python3
"""Lab 38 — heterogeneous multi-robot collaboration mechanism test.

The normal suite isolates three claims:
1. capability-aware task allocation can exploit heterogeneous robots;
2. coordination depends on fresh robot-status communication, not just a central
   scheduler existing on paper;
3. correct capability metadata is causally necessary for the allocation gain.

A second failure suite keeps failure detection fixed and isolates whether the
coordinator releases and reallocates interrupted work after one robot fails.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab38_multi_robot_collaboration"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass
class Job:
    job_id: int
    kind: str
    remaining: float
    status: str = "queued"
    owner: str = ""
    completed_at: int | None = None


@dataclass
class Agent:
    name: str
    rates: dict[str, float]
    active_job: int | None = None
    alive: bool = True


def make_agents(cfg: dict[str, Any]) -> dict[str, Agent]:
    return {
        name: Agent(
            name=name,
            rates={kind: float(rate) for kind, rate in rates.items()},
        )
        for name, rates in cfg["agents"].items()
    }


def make_jobs(cfg: dict[str, Any], count: int) -> list[Job]:
    kinds = [str(kind) for kind in cfg["job_types"]]
    work = float(cfg["work_per_job"])
    return [Job(job_id=i, kind=kinds[i % len(kinds)], remaining=work) for i in range(count)]


def fastest_agent(kind: str, agents: dict[str, Agent], *, alive_only: bool = True) -> str:
    candidates = [
        agent
        for agent in agents.values()
        if (agent.alive or not alive_only)
    ]
    if not candidates:
        raise RuntimeError("No candidate agents")
    return min(candidates, key=lambda agent: (-agent.rates[kind], agent.name)).name


def choose_job(
    agent_name: str,
    jobs: list[Job],
    predicted_rates: dict[str, dict[str, float]],
) -> Job | None:
    queued = [job for job in jobs if job.status == "queued"]
    if not queued:
        return None
    rates = predicted_rates[agent_name]
    return min(
        queued,
        key=lambda job: (job.remaining / rates[job.kind], job.job_id),
    )


def count_jobs(jobs: list[Job], status: str) -> int:
    return sum(job.status == status for job in jobs)


def summary_from_jobs(
    *,
    condition: str,
    scenario: str,
    jobs: list[Job],
    horizon: int,
    counters: dict[str, float],
) -> dict[str, Any]:
    completed = [job for job in jobs if job.status == "done"]
    all_complete = len(completed) == len(jobs)
    last_completion = max((job.completed_at or 0) for job in completed) + 1 if completed else 0
    makespan = last_completion if all_complete else horizon
    sent = counters.get("communication_messages_sent", 0.0)
    transmitted = counters.get("communication_messages_transmitted", 0.0)
    status_samples = counters.get("status_age_samples", 0.0)

    return {
        "condition": condition,
        "scenario": scenario,
        "completed_jobs": len(completed),
        "total_jobs": len(jobs),
        "completion_rate": len(completed) / len(jobs),
        "all_complete": int(all_complete),
        "makespan_steps": makespan,
        "throughput_jobs_per_step": len(completed) / horizon,
        "duplicate_claims": int(counters.get("duplicate_claims", 0.0)),
        "blocked_steps": int(counters.get("blocked_steps", 0.0)),
        "stale_idle_steps": int(counters.get("stale_idle_steps", 0.0)),
        "assignment_rejections": int(counters.get("assignment_rejections", 0.0)),
        "capability_mismatch_assignments": int(
            counters.get("capability_mismatch_assignments", 0.0)
        ),
        "work_steps": int(counters.get("work_steps", 0.0)),
        "idle_steps": int(counters.get("idle_steps", 0.0)),
        "communication_messages_sent": int(sent),
        "communication_messages_transmitted": int(transmitted),
        "communication_delivery_ratio": (transmitted / sent) if sent else 0.0,
        "communication_bytes_transmitted": int(
            counters.get("communication_bytes_transmitted", 0.0)
        ),
        "avg_status_age_steps": (
            counters.get("status_age_sum", 0.0) / status_samples
            if status_samples
            else 0.0
        ),
        "reallocation_count": int(counters.get("reallocation_count", 0.0)),
        "interrupted_job_id": int(counters.get("interrupted_job_id", -1.0)),
        "interrupted_job_recovered": int(
            counters.get("interrupted_job_recovered", 0.0)
        ),
        "recovery_latency_steps": int(counters.get("recovery_latency_steps", -1.0)),
    }


def record_agent_step(
    recorder: RunRecorder,
    *,
    condition: str,
    scenario: str,
    step: int,
    agent: Agent,
    jobs: list[Job],
    event: str,
    selected_job: int | None,
    selected_kind: str,
    shadow_state: str,
    status_age: int,
    counters: dict[str, float],
) -> None:
    recorder.log_step(
        scenario=scenario,
        condition=condition,
        step=step,
        agent=agent.name,
        alive=int(agent.alive),
        event=event,
        selected_job="" if selected_job is None else selected_job,
        selected_kind=selected_kind,
        real_active_job="" if agent.active_job is None else agent.active_job,
        shadow_state=shadow_state,
        status_age=status_age,
        jobs_queued=count_jobs(jobs, "queued"),
        jobs_assigned=count_jobs(jobs, "assigned"),
        jobs_completed=count_jobs(jobs, "done"),
        duplicate_claims=int(counters.get("duplicate_claims", 0.0)),
        blocked_steps=int(counters.get("blocked_steps", 0.0)),
        stale_idle_steps=int(counters.get("stale_idle_steps", 0.0)),
        capability_mismatch_assignments=int(
            counters.get("capability_mismatch_assignments", 0.0)
        ),
        communication_messages_sent=int(
            counters.get("communication_messages_sent", 0.0)
        ),
        communication_messages_transmitted=int(
            counters.get("communication_messages_transmitted", 0.0)
        ),
    )


def progress_agents(
    *,
    agents: dict[str, Agent],
    jobs: list[Job],
    step: int,
    counters: dict[str, float],
    events: dict[str, list[str]],
) -> None:
    for agent in agents.values():
        if not agent.alive:
            continue
        if agent.active_job is None:
            counters["idle_steps"] = counters.get("idle_steps", 0.0) + 1
            continue

        counters["work_steps"] = counters.get("work_steps", 0.0) + 1
        job = jobs[agent.active_job]
        job.remaining -= agent.rates[job.kind]
        events[agent.name].append(f"work:{job.job_id}:{job.kind}")
        if job.remaining <= 1e-12:
            job.status = "done"
            job.owner = ""
            job.completed_at = step
            events[agent.name].append(f"complete:{job.job_id}")
            agent.active_job = None


def run_independent(
    *,
    cfg: dict[str, Any],
    recorder: RunRecorder,
) -> tuple[dict[str, Any], list[Job]]:
    condition = "independent_no_comm"
    scenario = "normal"
    horizon = int(cfg["normal_horizon_steps"])
    agents = make_agents(cfg)
    jobs = make_jobs(cfg, int(cfg["normal_job_count"]))
    counters: dict[str, float] = {}

    for step in range(horizon):
        events = {name: [] for name in agents}
        selected: dict[str, tuple[int | None, str]] = {
            name: (None, "") for name in agents
        }

        # Each idle robot sees the same incomplete job priority list but cannot
        # see peer claims/ownership. Claims are chosen simultaneously.
        claims: dict[str, int] = {}
        for name, agent in agents.items():
            if agent.alive and agent.active_job is None:
                visible = [job for job in jobs if job.status != "done"]
                if visible:
                    claims[name] = min(visible, key=lambda job: job.job_id).job_id

        queued_claims: dict[int, list[str]] = {}
        for name, job_id in claims.items():
            job = jobs[job_id]
            selected[name] = (job_id, job.kind)
            if job.status == "assigned":
                counters["blocked_steps"] = counters.get("blocked_steps", 0.0) + 1
                events[name].append(f"blocked_peer_claim:{job_id}")
                recorder.log_failure(
                    category="duplicate_claim_blocked",
                    step=step,
                    time_s=float(step),
                    details={"agent": name, "job_id": job_id, "reason": "peer_already_owns_job"},
                )
            else:
                queued_claims.setdefault(job_id, []).append(name)

        for job_id, names in queued_claims.items():
            job = jobs[job_id]
            if len(names) > 1:
                counters["duplicate_claims"] = counters.get("duplicate_claims", 0.0) + len(names) - 1
                ranked = sorted(
                    names,
                    key=lambda name: (-agents[name].rates[job.kind], name),
                )
                winner = ranked[0]
                for loser in ranked[1:]:
                    counters["blocked_steps"] = counters.get("blocked_steps", 0.0) + 1
                    events[loser].append(f"blocked_simultaneous_claim:{job_id}")
                    recorder.log_failure(
                        category="duplicate_claim_blocked",
                        step=step,
                        time_s=float(step),
                        details={"agent": loser, "job_id": job_id, "reason": "simultaneous_claim"},
                    )
            else:
                winner = names[0]

            job.status = "assigned"
            job.owner = winner
            agents[winner].active_job = job_id
            events[winner].append(f"assign:{job_id}:{job.kind}")

        progress_agents(
            agents=agents,
            jobs=jobs,
            step=step,
            counters=counters,
            events=events,
        )

        for name, agent in agents.items():
            job_id, kind = selected[name]
            record_agent_step(
                recorder,
                condition=condition,
                scenario=scenario,
                step=step,
                agent=agent,
                jobs=jobs,
                event=";".join(events[name]) or "idle",
                selected_job=job_id,
                selected_kind=kind,
                shadow_state="none",
                status_age=-1,
                counters=counters,
            )

    return (
        summary_from_jobs(
            condition=condition,
            scenario=scenario,
            jobs=jobs,
            horizon=horizon,
            counters=counters,
        ),
        jobs,
    )


def predicted_rate_map(
    agents: dict[str, Agent],
    *,
    shuffled: bool,
) -> dict[str, dict[str, float]]:
    names = sorted(agents)
    if not shuffled:
        return {name: dict(agents[name].rates) for name in names}
    if len(names) != 2:
        raise ValueError("Shuffled capability control expects exactly two agents")
    return {
        names[0]: dict(agents[names[1]].rates),
        names[1]: dict(agents[names[0]].rates),
    }


def run_coordinated(
    *,
    condition: str,
    cfg: dict[str, Any],
    recorder: RunRecorder,
) -> tuple[dict[str, Any], list[Job]]:
    scenario = "normal"
    horizon = int(cfg["normal_horizon_steps"])
    agents = make_agents(cfg)
    jobs = make_jobs(cfg, int(cfg["normal_job_count"]))
    counters: dict[str, float] = {}

    delay = int(cfg["communication"]["delayed_steps"]) if condition == "coordinated_delayed" else 0
    dropout_modulus = (
        int(cfg["communication"]["dropout_modulus"])
        if condition == "coordinated_dropout"
        else None
    )
    shuffled = condition == "shuffled_capability_map"
    predicted_rates = predicted_rate_map(agents, shuffled=shuffled)

    # Shared task board is authoritative; only robot availability/heartbeat is
    # communicated. This intentionally isolates communication freshness from
    # task-discovery uncertainty.
    shadow_state = {name: "idle" for name in agents}
    shadow_timestamp = {name: 0 for name in agents}
    message_queue: list[dict[str, Any]] = []

    for step in range(horizon):
        events = {name: [] for name in agents}
        selected: dict[str, tuple[int | None, str]] = {
            name: (None, "") for name in agents
        }

        due = [message for message in message_queue if int(message["deliver_step"]) <= step]
        message_queue = [
            message for message in message_queue if int(message["deliver_step"]) > step
        ]
        for message in sorted(due, key=lambda item: (int(item["send_step"]), str(item["agent"]))):
            name = str(message["agent"])
            shadow_state[name] = str(message["state"])
            shadow_timestamp[name] = int(message["send_step"])

        for name, agent in agents.items():
            age = max(0, step - shadow_timestamp[name])
            counters["status_age_sum"] = counters.get("status_age_sum", 0.0) + age
            counters["status_age_samples"] = counters.get("status_age_samples", 0.0) + 1

            if shadow_state[name] == "idle":
                if agent.active_job is not None:
                    counters["assignment_rejections"] = counters.get("assignment_rejections", 0.0) + 1
                    shadow_state[name] = "busy"
                    events[name].append("reject_stale_idle_shadow")
                    recorder.log_failure(
                        category="stale_assignment_rejected",
                        step=step,
                        time_s=float(step),
                        details={"agent": name, "real_active_job": agent.active_job, "status_age": age},
                    )
                    continue

                job = choose_job(name, jobs, predicted_rates)
                if job is not None:
                    selected[name] = (job.job_id, job.kind)
                    if fastest_agent(job.kind, agents) != name:
                        counters["capability_mismatch_assignments"] = counters.get(
                            "capability_mismatch_assignments", 0.0
                        ) + 1
                        events[name].append(f"capability_mismatch:{job.job_id}")
                    job.status = "assigned"
                    job.owner = name
                    agent.active_job = job.job_id
                    shadow_state[name] = "busy"
                    events[name].append(f"assign:{job.job_id}:{job.kind}")
            elif agent.active_job is None:
                counters["stale_idle_steps"] = counters.get("stale_idle_steps", 0.0) + 1
                events[name].append("idle_due_to_stale_busy_shadow")
                recorder.log_failure(
                    category="stale_status_idle",
                    step=step,
                    time_s=float(step),
                    details={"agent": name, "status_age": age, "shadow_state": shadow_state[name]},
                )

        progress_agents(
            agents=agents,
            jobs=jobs,
            step=step,
            counters=counters,
            events=events,
        )

        for index, (name, agent) in enumerate(sorted(agents.items())):
            state = "busy" if agent.active_job is not None else "idle"
            payload = {
                "agent": name,
                "state": state,
                "active_job": agent.active_job,
                "send_step": step,
            }
            encoded_bytes = len(json.dumps(payload, sort_keys=True).encode("utf-8"))
            counters["communication_messages_sent"] = counters.get(
                "communication_messages_sent", 0.0
            ) + 1

            transmit = dropout_modulus is None or ((step + index) % dropout_modulus == 0)
            if transmit:
                counters["communication_messages_transmitted"] = counters.get(
                    "communication_messages_transmitted", 0.0
                ) + 1
                counters["communication_bytes_transmitted"] = counters.get(
                    "communication_bytes_transmitted", 0.0
                ) + encoded_bytes
                message_queue.append(
                    {
                        "deliver_step": step + 1 + delay,
                        "send_step": step,
                        "agent": name,
                        "state": state,
                    }
                )
            else:
                events[name].append("heartbeat_dropped")

        for name, agent in agents.items():
            job_id, kind = selected[name]
            record_agent_step(
                recorder,
                condition=condition,
                scenario=scenario,
                step=step,
                agent=agent,
                jobs=jobs,
                event=";".join(events[name]) or "idle",
                selected_job=job_id,
                selected_kind=kind,
                shadow_state=shadow_state[name],
                status_age=max(0, step - shadow_timestamp[name]),
                counters=counters,
            )

    return (
        summary_from_jobs(
            condition=condition,
            scenario=scenario,
            jobs=jobs,
            horizon=horizon,
            counters=counters,
        ),
        jobs,
    )


def run_failure_suite(
    *,
    condition: str,
    cfg: dict[str, Any],
    recorder: RunRecorder,
) -> tuple[dict[str, Any], list[Job]]:
    scenario = "single_agent_failure"
    horizon = int(cfg["failure_horizon_steps"])
    failure_step = int(cfg["failure_step"])
    agents = make_agents(cfg)
    jobs = make_jobs(cfg, int(cfg["failure_job_count"]))
    predicted_rates = predicted_rate_map(agents, shuffled=False)
    counters: dict[str, float] = {}
    interrupted_job: int | None = None

    for step in range(horizon):
        events = {name: [] for name in agents}
        selected: dict[str, tuple[int | None, str]] = {
            name: (None, "") for name in agents
        }

        if step == failure_step:
            failed = agents["carrier"]
            failed.alive = False
            events[failed.name].append("agent_failure")
            interrupted_job = failed.active_job
            if interrupted_job is not None:
                counters["interrupted_job_id"] = float(interrupted_job)
                job = jobs[interrupted_job]
                failed.active_job = None
                if condition == "failure_reallocation":
                    job.status = "queued"
                    job.owner = ""
                    counters["reallocation_count"] = counters.get("reallocation_count", 0.0) + 1
                    events[failed.name].append(f"release_interrupted_job:{interrupted_job}")
                else:
                    events[failed.name].append(f"leave_interrupted_job_stuck:{interrupted_job}")

            recorder.log_failure(
                category="agent_failure",
                step=step,
                time_s=float(step),
                details={
                    "agent": failed.name,
                    "interrupted_job": interrupted_job,
                    "reallocation_enabled": condition == "failure_reallocation",
                },
            )

        for name, agent in agents.items():
            if not agent.alive or agent.active_job is not None:
                continue
            job = choose_job(name, jobs, predicted_rates)
            if job is None:
                continue
            selected[name] = (job.job_id, job.kind)
            if fastest_agent(job.kind, agents) != name:
                counters["capability_mismatch_assignments"] = counters.get(
                    "capability_mismatch_assignments", 0.0
                ) + 1
            job.status = "assigned"
            job.owner = name
            agent.active_job = job.job_id
            events[name].append(f"assign:{job.job_id}:{job.kind}")

        progress_agents(
            agents=agents,
            jobs=jobs,
            step=step,
            counters=counters,
            events=events,
        )

        if interrupted_job is not None:
            job = jobs[interrupted_job]
            if job.status == "done" and not counters.get("interrupted_job_recovered", 0.0):
                counters["interrupted_job_recovered"] = 1.0
                counters["recovery_latency_steps"] = float(step - failure_step + 1)
                events[job.owner or "dexter"].append(f"recover_interrupted_job:{interrupted_job}")

        for name, agent in agents.items():
            job_id, kind = selected[name]
            record_agent_step(
                recorder,
                condition=condition,
                scenario=scenario,
                step=step,
                agent=agent,
                jobs=jobs,
                event=";".join(events[name]) or ("failed" if not agent.alive else "idle"),
                selected_job=job_id,
                selected_kind=kind,
                shadow_state="failure_known" if not agent.alive else "fresh",
                status_age=0,
                counters=counters,
            )

    return (
        summary_from_jobs(
            condition=condition,
            scenario=scenario,
            jobs=jobs,
            horizon=horizon,
            counters=counters,
        ),
        jobs,
    )


def job_rows(condition: str, scenario: str, jobs: list[Job], interrupted_job_id: int) -> list[dict[str, Any]]:
    return [
        {
            "condition": condition,
            "scenario": scenario,
            "job_id": job.job_id,
            "kind": job.kind,
            "final_status": job.status,
            "final_owner": job.owner,
            "remaining_work": max(0.0, job.remaining),
            "completed_at": "" if job.completed_at is None else job.completed_at,
            "interrupted_job": int(job.job_id == interrupted_job_id),
        }
        for job in jobs
    ]


def run_experiment(cfg: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    all_job_rows: list[dict[str, Any]] = []

    conditions = [
        *[str(name) for name in cfg["normal_conditions"]],
        *[str(name) for name in cfg["failure_conditions"]],
    ]

    for condition in conditions:
        recorder = RunRecorder(
            output_root=output_root / "runs",
            lab_id=LAB_ID,
            condition=condition,
            seed=int(cfg["seed"]),
            config=cfg,
            repo_root=REPO_ROOT,
        )

        if condition == "independent_no_comm":
            summary, jobs = run_independent(cfg=cfg, recorder=recorder)
        elif condition in {
            "coordinated_fresh",
            "coordinated_delayed",
            "coordinated_dropout",
            "shuffled_capability_map",
        }:
            summary, jobs = run_coordinated(condition=condition, cfg=cfg, recorder=recorder)
        elif condition in {"failure_no_reallocation", "failure_reallocation"}:
            summary, jobs = run_failure_suite(condition=condition, cfg=cfg, recorder=recorder)
        else:
            raise ValueError(f"Unknown condition: {condition}")

        summaries.append(summary)
        interrupted = int(summary["interrupted_job_id"])
        all_job_rows.extend(job_rows(condition, str(summary["scenario"]), jobs, interrupted))
        recorder.finalize(summary)

    write_csv(output_root / "condition_metrics.csv", summaries)
    write_csv(output_root / "job_metrics.csv", all_job_rows)
    write_json(
        output_root / "experiment_summary.json",
        {
            "lab_id": LAB_ID,
            "normal_conditions": list(cfg["normal_conditions"]),
            "failure_conditions": list(cfg["failure_conditions"]),
            "normal_horizon_steps": int(cfg["normal_horizon_steps"]),
            "failure_horizon_steps": int(cfg["failure_horizon_steps"]),
            "failure_step": int(cfg["failure_step"]),
            "shared_authoritative_task_board": True,
            "robot_status_communicated": True,
            "failure_detection_fixed_in_failure_suite": True,
        },
    )

    print("Lab 38 multi-robot collaboration experiment complete")
    for row in summaries:
        print(
            f"{row['condition']:<27} "
            f"completion={float(row['completion_rate']):.3f} "
            f"makespan={int(row['makespan_steps']):02d} "
            f"blocked={int(row['blocked_steps']):02d} "
            f"stale_idle={int(row['stale_idle_steps']):02d} "
            f"cap_mismatch={int(row['capability_mismatch_assignments']):02d} "
            f"delivery={float(row['communication_delivery_ratio']):.3f} "
            f"recovered={int(row['interrupted_job_recovered'])}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=Path("/tmp/lab38_multi_robot"))
    args = parser.parse_args()

    cfg = load_json(args.config)
    run_experiment(cfg, args.output)


if __name__ == "__main__":
    main()
