# Google Colab CLI (googlecolab/google-colab-cli): research notes

Scope: read-only. No `colab new`, `colab exec`, or any runtime allocation was run.
Sources:
- Installed CLI: `colab` 0.7.6.dev1+g4025416a0 (`colab version`), at `~/.local/share/uv/tools/google-colab-cli`.
- Repo HEAD 4025416 (Wed Oct 21 2026), shallow clone at `<SP>/src_clone/repo`. Same commit as the installed build.
- Repo docs saved at `<SP>/repo_docs/` (README.md, docs/01-06, demos.md).
- Repo skill saved verbatim at `<SP>/colab-operator/SKILL.md`.

Path `<SP>` = `<scratch>`

Citation key: `docs/NN` = `<SP>/repo_docs/NN_*.md`; `src/...` = `<SP>/src_clone/repo/src/colab_cli/...`.

---

## 0. Skill file format

- `skills/colab-operator/` contains exactly one file: `SKILL.md`. It has YAML frontmatter (`name: colab-operator`, `description: ...`), then a Markdown body.
- The installed `colab skill` output is identical to the repo file except for one trailing blank line.

## 1. Answers to a-i

### a. Local disconnect, process killed, timeout

- **Docs:** not documented. No doc in the repo says what happens to a running cell when the client dies or when `--timeout` expires.
- **Client exit does not stop the kernel (code):** `runtime.stop()` only closes channels and the socket. It shuts the kernel down only when `shutdown_kernel=True` (`src/colab_cli/runtime.py:264-276`). `colab exec` calls `runtime.stop()` with the default in its `finally` (`src/colab_cli/commands/execution.py` ~275-279). SKILL.md "Mental model" says the same: each call "only closes the websocket on exit — it does **not** shut the kernel down."
- **No interrupt is sent:** `grep interrupt src/colab_cli` finds nothing. The CLI never calls `kernel_client.interrupt()`, so neither a timeout nor a dropped client interrupts the remote cell. Whether the Colab backend or Jupyter itself kills the cell on websocket drop is not documented; the most likely reading is that the cell keeps running, but that is inference.
- **Killed by signal:** `exec`, `run`, and `repl` install no signal handlers. Only `console.py` (SIGWINCH) and `ssh.py:547-552` register handlers. `ssh.py:533-536` documents the risk: "Python's default SIGHUP action would terminate us WITHOUT the teardown finally". The same applies to `colab run`, so a SIGHUP/SIGTERM/SIGKILL to `colab run` probably skips `_teardown` and leaves the VM assigned. This is inferred from Python semantics plus the ssh.py comment; not tested.
- **`--timeout` semantics (code, version-dependent):**
  - Doc: `docs/02` line 31 says the flag exists "to allow long-running silent tasks ... to execute without being prematurely killed". This does not say what happens on expiry.
  - Repo comment `src/colab_cli/runtime.py:186-198` says a quiet stretch longer than the timeout raises `TimeoutError` even though the execution is healthy.
  - Installed `jupyter_kernel_client` is **0.8.0** (`lib/python3.13/site-packages/jupyter_kernel_client-0.8.0`). `wsclient.py:1052-1054` sets `deadline = monotonic() + timeout` once. The loop at `wsclient.py:1056-1090` has no break on the deadline. `TimeoutError` is raised only in the reply wait (`wsclient.py:1218-1220`, `_recv_reply` at `wsclient.py:1354-1356`). With a passed deadline, the loop busy-polls (`wait(timeout=0)`) until idle.
  - Net effect in 0.8.0: a timeout does not interrupt the kernel. The client may raise `TimeoutError` after idle, or spin. The repo pins `jupyter-kernel-client==0.9.0` from git (`pyproject.toml:31,82`; `uv.lock`), which was not inspected. **Unverified live.**
- **Consequences in the CLI:**
  - `colab exec` on exception: `execution.py` `finally` runs `runtime.stop()`, not a kernel shutdown. The `log_event` for the execution (`execution.py:265-270`) is never reached, so the output is not logged. The VM is not released.
  - `colab run` on exception: `run.py` `except Exception: raise` → `finally` → `_teardown(...)` (`run.py` ~476-500). `_teardown` runs `rt.stop(shutdown_kernel=True)` and then `state.client.unassign(endpoint)`. **A timeout exception in `colab run` shuts the kernel and releases the VM, which kills the job.** The `colab run` default is `--timeout 30.0` (`docs/05` line 36).

### b. `colab console`

- **It is a shell on the VM:** `docs/02` lines 33-35: "Connects directly to the backend terminal endpoint (`/colab/tty`) via WebSockets ... Bypasses the Jupyter kernel entirely to provide a raw, PTY-backed bash session on the Colab VM."
- **tmux:** `docs/02` line 37 and `demos.md:152`: "The remote `/colab/tty` endpoint wraps bash in tmux". Whether you can use tmux or nohup yourself is **not documented**. The tmux wrapper implies tmux exists on the VM. Whether a job started with `nohup ... &` inside a piped console survives the forced `exit` on EOF is **not documented**.
- **Non-interactive use:** yes. `docs/02` lines 3-7 (2026-05-07 entry): `echo 'cmd' | colab console -s s` works. On EOF the client sends `exit\n`, then closes the websocket after `PIPED_EOF_GRACE_SECONDS = 0.5s`. Output contains terminal-control bytes, so filter with `grep -a` (`demos.md:152-155`). `docs/02` line 37 explains the choice of `exit\n` over Ctrl-D.
- **Exit code:** not documented.
- **Interactive use:** requires a local TTY (`README.md` "TTY Requirements", line 147). Do not run it interactively from an agent (SKILL.md, "Execute").

### c. Recommended pattern for long jobs and log polling

- **Documented pattern:** none for detached or long jobs. The only documented flow is foreground. `README.md:118-128`: `colab new -s trainer --gpu A100`, `colab install ...`, `colab exec -s trainer -f train.py` (blocking), `colab download ...`, `colab stop`.
- **Ephemeral:** `colab run` (`docs/05`, `README.md:151-170`) is the documented one-shot path. It is unsafe for jobs longer than the timeout (see a).
- **Polling:**
  - `colab log -s NAME -n N` shows recent events (`commands/utility.py:129-206`). Execution events are written only after an exec returns (`execution.py:265-270`), so **`colab log` cannot show live output of a running cell.**
  - `colab status` shows `BUSY (<file>)` from local bookkeeping (`session.py:283`, `execution.py` sets `s.running` before the exec and clears it in `finally`). If the exec process dies, the flag can go stale. Not verified.
- **My suggestion (not documented, from the code above):** start the job detached on the VM, with `subprocess.Popen(..., start_new_session=True)` or nohup from the kernel, logging to a file under `/content`. Return from `exec` at once. Poll with short `colab exec` calls that read the log tail, or with `colab download`. Keep `--timeout` small on polls. Do not depend on the client process staying alive for hours.

### d. `colab new` flags, A100 40/80GB, idle and max runtime

- **Flags (`colab new --help`):** `--gpu` (T4, L4, G4, H100, A100), `--tpu` (v5e1, v6e1), `--high-mem`, `-s`. Yes, `--gpu A100` and `--high-mem` both exist.
- **`--high-mem`:** "Request a high-RAM machine shape (CPU, T4, A100, etc.). Requires Colab Pro or Pro+ entitlement. Ignored for accelerators that only offer a single shape (L4, v5e1, v6e1)." (`colab new --help`). Mapping: `src/colab_cli/client.py:100-114` (`resolve_assign_shape`) and `client.py:331` (`shape=hm`). `docs/01` lines 40-45. This is **machine (system) RAM**, not GPU memory.
- **A100 80GB vs 40GB:** **not documented.** The CLI exposes no VRAM choice. Do not assume `--high-mem` picks 80GB. The only way to confirm is `colab status` / `nvidia-smi` after allocation.
- **Silent fallback (verified in code):** `src/colab_cli/commands/session.py:85`: `accelerator = mapping.get(gpu.lower(), Accelerator.A100)`. An unknown `--gpu` value silently becomes A100. This matches SKILL.md "Gotcha". Check `colab status` after `colab new`.
- **400 on allocation:** `session.py:159-168` tells the user to try `--gpu T4` or omit the flag.
- **Idle timeout / max runtime:** **not documented, no numbers.** `docs/01` lines 110-111: "A session persists until explicitly terminated via `colab stop` or until the backend reclaims it due to inactivity." `README.md:22`: "Sessions stay alive as long as the kernel is active." `docs/01` lines 110-111 and the removed keep-alive daemon (`docs/01` line 8, `docs/05` line 3) mean the CLI does not ping the VM.

### e. `colab install -r requirements.txt`

- **Code** (`src/colab_cli/commands/automation.py:229-275`):
  1. Checks that the local file exists (line ~250).
  2. Uploads it through the Contents API to `/content/<basename>` (`remote_path = f"content/{basename}"`, lines 254-255).
  3. Runs in the kernel: `subprocess.check_call(['uv', 'pip', 'install', '--system'] + packages)` (line 266), falling back to `[sys.executable, '-m', 'pip', 'install', ...]` (line 269). `-r` is passed as `-r /content/<name>`.
  4. Runs through `run_automation(name, "install", code)` (line 274), so the install code is written to the history log.
- **Pip into the kernel env:** it installs into the VM's system Python (`--system`), which is the same interpreter the kernel uses.
- **Kernel restart:** the code never restarts the kernel. Already-imported modules keep their old versions. Whether a restart is needed is **not documented**. Use `colab restart-kernel` after upgrading a module the kernel has already imported (inference).
- **Doc drift:** `docs/04` lines 106-112 describes a pip-only design using `sys.executable`. The code is uv-first. The code is authoritative.

### f. `colab drivemount`

- **Usage:** `colab drivemount [PATH]`, default `/content/drive` (`automation.py:211-217`; `colab drivemount --help`).
- **Mechanism:** the kernel runs `from google.colab import drive; drive.mount('<path>')` (`automation.py:217`). The CLI intercepts drivefs `colab_request` messages (`automation.py:55-129`) and sends them to the backend `/tun/m/credentials-propagation/` (`docs/04` lines 114-131). It logs `drive_auth_needed` with the consent `uri` and then `drive_auth_success` (`automation.py:102,129`).
- **Auth flow:** a human approves an OAuth consent URL in a browser, and the CLI sends the reply back to the kernel. The SKILL says it is not agent-runnable. Whether it works without a TTY is **not documented**.
- **Timeout:** 600 s for drivemount and auth (`automation.py:38`, passed at lines 203, 225).
- **Mount persistence** after the VM is released or the session is reconnected: **not documented**.

### g. `colab log` and secret leakage

- **Storage:** `~/.config/colab-cli/history/<session>.jsonl`, append-only (`src/colab_cli/history.py:16-30`). There is no delete path in `history.py` (`grep remove|unlink|rmtree` returns nothing).
- **Contents** (`history.py:29-40` docstring and the call sites):
  - `execution`: the full `code` string and the full `outputs` (stdout, stderr, display data). See `execution.py:265-270`, `execution.py:346-347`, `run.py:440-443`.
  - `stdin_request` (prompt) and `input_reply` (value), `runtime.py:206-214`. This includes pasted OAuth codes and anything typed at a prompt.
  - `automation` (install, auth, drivemount) with `code`, `automation.py:159`.
  - `run` payload, including the generated `sys.argv` prelude, `run.py:440-443`.
- **`--env` secrets leak into the log (verified):** `execution.py:65-73` builds `os.environ['KEY'] = 'VALUE'` prelude text. Line ~235 prepends it to `code`. Lines ~265-270 log that `code` string. **So `colab exec --env API_KEY=...` writes the value in plaintext into `history/<session>.jsonl` and into any exported `.ipynb`/`.md`/`.txt`/`.jsonl`.**
- **Exports:** `colab log -s NAME -o file.{ipynb,md,txt,jsonl}` (`colab log --help`; `converter.py`). No redaction in the code I read.
- **Subcommands:** the installed `colab log --help` has no `list` or `show` subcommands. `-s` with no session lists sessions that have logs (`utility.py:163-169`). `docs/04` lines 139-140 describe `colab log list` and `colab log show`, which are stale.
- **Mitigation (suggestion):** do not pass secrets through `--env`. Read them from files or the environment on the VM (for example `colab upload` a file with mode 600, or use `colab auth`). Delete `~/.config/colab-cli/history/<session>.jsonl` after sensitive runs (manual, the CLI has no command for it). File permissions on the history file are not verified.

### h. `colab upload` / `colab download`

- **Upload** (`src/colab_cli/contents.py:55-72`): reads the whole local file into memory, base64-encodes it, and sends one JSON `PUT /api/contents/<remote_path>` with `"format": "base64"` and `"chunk": 1`. The `chunk` field is set but there is no chunking loop. The remote name is the last path segment. There is **no size limit in the CLI code**. Server-side limits are **not documented**. `docs/03` lines 47-48 mention a kernel-streaming fallback for large files, but it is only a plan ("we'll implement a fallback"). Not implemented.
- **Download** (`contents.py:76-91`): `GET /api/contents/<remote>?content=1`. Decodes base64 or UTF-8 text and writes the local file. Refuses directories (`IsADirectoryError`). 404 becomes `FileNotFoundError` (`contents.py:~40-45`).
- **Paths:** `colab upload LOCAL REMOTE` and `colab download REMOTE LOCAL` (`--help`). Use absolute `/content/...` (SKILL.md, "Mental model"). For `ls`, the default path is `content`, which is the VM root (SKILL.md).
- **Directories:** upload of a directory is not supported by the code (it calls `open()` on the path).

### i. `colab usage` and CU cost

- **Command:** `colab usage` takes no flags (`colab usage --help`).
- **Source:** `GET https://colab.research.google.com/tun/m/ccu-info` (`docs/04` lines 143-150; `src/colab_cli/consumption.py:25-55`). Fields: `currentBalance`, `consumptionRateHourly`, `assignmentsCount`.
- **Exact output** (`consumption.py:47-55`):
  ```
  Current balance: <N.NN> compute units
  Usage rate: <R.RR>/hr
  Active assignments: <K>
  ```
  The rate is aggregate across all assigned VMs.
- **Per-accelerator CU rates:** **not documented** in the repo. `colab pay` opens `https://colab.research.google.com/signup` (`src/colab_cli/commands/utility.py:25-30`). I did not call `colab usage` (it needs auth and is not a runtime allocation, but I did not run it).

---

## 2. Discrepancies between docs, help, and code

| Topic | Docs / SKILL / README | Installed help / code | Note |
|---|---|---|---|
| `--auth` default | README:109 and SKILL say `adc` | `colab --help` shows `[default: oauth2]`; `docs/04` says oauth2 | Pass `--auth=adc` explicitly |
| Timeout semantics | `docs/02` and the runtime.py comment: quiet stretch raises | jupyter_kernel_client 0.8.0 has an absolute deadline with no break in the loop | Pinned 0.9.0 not checked; unverified live |
| `colab log` subcommands | `docs/04` lines 139-140: `log list` / `log show` | Only options; `-s` alone lists sessions | Docs stale |
| `colab install` | `docs/04` lines 106-112: pip with `sys.executable` | `automation.py:266`: `uv pip install --system` first, pip fallback | Code is authoritative |
| Installed deps | `pyproject.toml:31,82` pins `jupyter-kernel-client==0.9.0` (git) | Installed `jupyter_kernel_client-0.8.0` | Installed build may not match HEAD deps |
| SKILL vs bundled skill | Repo SKILL.md | `colab skill` | Identical except trailing newline |

---

## 3. Practical implications for multi-hour GPU eval jobs (my inference, not documented)

1. Do not run multi-hour work through `colab run`. Its `finally` releases the VM on any exception, including a timeout (`run.py` ~476-500), and a signal kills it without teardown (no handlers, see ssh.py:533-536).
2. Do not rely on the `--timeout` flag to bound a job. Its behaviour is version-dependent and it never interrupts the kernel.
3. Do not rely on a long-lived `colab exec` client. If the client dies, you lose its output stream. Start the job detached on the VM, log to a file under `/content`, and poll with short calls.
4. Verify the GPU after `colab new`: an unknown `--gpu` name silently becomes A100 (`session.py:85`).
5. Do not pass secrets through `--env` (plaintext in history and exports).
6. Use `colab stop` at the end. There is no documented idle or max-runtime limit to save you.

---

## 4. Unverified / caveats (summary)

- Nothing was executed against a live Colab runtime. Every behaviour claim is from the docs or source at commit 4025416 plus the installed 0.8.0 dependency.
- The kernel-keeps-running-after-client-dies claim is inferred from the absence of interrupt and shutdown code. Not verified.
- The SIGHUP/SIGKILL leak of `colab run` VMs is inferred from Python signal semantics and the ssh.py comment. Not verified.
- The timeout behaviour differs between the installed 0.8.0 and the pinned 0.9.0. Not verified.
- A100 40GB vs 80GB: not documented. Idle timeout and max runtime: not documented.
- Whether tmux, nohup, or background jobs survive in `colab console`: not documented.
- Whether drivemount works without a TTY: not documented.
- Server-side upload size limits: not documented.
- History file permissions: not checked.
