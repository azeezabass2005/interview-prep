# R2-02 · Equity OMS: interviewer notes

~550 lines. Four tickets of different shapes: a pure logic bug, a concurrency bug (lost update), a state-machine bug whose
**acceptance criteria point at the wrong component**, and a float-precision bug.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| OMS-201 average price | `(old_avg + price) / 2`: a pairwise mean, not quantity-weighted | `services/executions.py::apply_execution` | None; good warm-up. Check they test 3+ executions, not just 2 |
| OMS-202 lost fills | **Read-modify-write race.** `apply_execution` reads `filled_qty`/`avg_price`, computes in Python, writes absolute values. Two instances overwrite each other | `services/executions.py` + `repositories/orders.py::save_fill_state` | "Never happens in test (single instance)": a process lock would pass a single-process test and still fail in prod |
| OMS-203 cancelled-but-filled | `cancel_order` never checks the current status; it unconditionally sets `CANCELLED` | `services/orders.py::cancel_order` | **AC is wrong.** It asks to change `PositionService` to ignore cancelled orders' executions. Positions are *correct*: the client owns the shares. Following the AC hides real exposure (a partially filled then cancelled order really did execute) |
| OMS-204 valid price rejected | `price * 100` in float: `4.35 * 100 = 434.99999…` | `services/validation.py::validate_order` | Fix with `Decimal(str(price)) % tick == 0`; don't "add an epsilon" without reasoning |

## OMS-202 in depth

**Invariant:** an order's `filled_qty`/`avg_price`/`status` always equal the aggregate of its stored executions, regardless of interleaving.

| Option | Verdict | Why |
|---|---|---|
| `threading.Lock` in `ExecutionService` | Reject | Process-local; executions for one order hit different instances |
| Re-read the order just before writing | Reject | Narrows the window only |
| Atomic increment in SQL (`filled_qty = filled_qty + ?`) | Accept for qty | Store-owned. Average still needs care (can't do Decimal math in SQLite TEXT safely) |
| Recompute fill state **from the executions table** inside one write transaction (`BEGIN IMMEDIATE`) | **Accept** | Executions are the source of truth (unique `exec_id`); derived fields are recomputed under the DB's write lock |
| Optimistic concurrency (version column, retry on mismatch) | Accept | Also store-owned; more code |

**Deterministic test:** two `ExecutionService` instances on one DB file; patch `OrderRepository.get` so the first two calls wait on a
`Barrier(2)` after reading. Both read `filled_qty = 0`. Assert the final `filled_qty == 100`, status `FILLED`, avg = weighted.

## OMS-203 in depth
Minimal fix: allow cancel only from `NEW`/`PARTIALLY_FILLED`; otherwise `InvalidState` (409). Better: make it a **conditional update**
(`UPDATE … SET status='CANCELLED' WHERE order_id=? AND status IN ('NEW','PARTIALLY_FILLED')` and check rowcount), so a fill racing with a
cancel can't be overwritten either. What to say about the AC: "Position is computed from executions and is correct. The bug is that the
order's status lies. I'd push back on changing positions."
Also worth noticing: `apply_execution` on a `CANCELLED` order. If the exchange fills after the cancel was sent, the fill must still be
recorded (the exchange is authoritative). Out of scope, but a great risk to call out.

## Out-of-scope smells
- `reporting.blotter` uses `avg_price × filled_qty`, which is only right once OMS-201 is fixed.
- `ids.new_order_id` uses a process-local counter (collisions across instances are protected by the uuid suffix; fine).

## Strong prompts
- "Starting at `ExecutionService.apply_execution`, list every read and write of `filled_qty` and `avg_price`, in order. Identify what happens if two calls interleave between the read and the write. Don't modify code."
- "Which component is the source of truth for what was executed: the orders row or the executions table? Show me the evidence."
