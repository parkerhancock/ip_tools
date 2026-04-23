# ip-tools TODO

Things flagged but not yet done. Sorted by how much they'd hurt if we
left them unchecked. Add items as you find them; check them off in PRs
that fix them.

## Nice-to-have UX improvements

- [ ] **Publish `ip-tools` to PyPI.** Install-from-GitHub works fine and
      the plugin's `uvx --from ${CLAUDE_PLUGIN_ROOT}[mcp]` already "just
      works" without PyPI. PyPI would unlock the shorter `pip install ip-tools`
      / `uvx --from ip-tools[mcp]` forms used throughout the docs, and
      enable install-without-git-clone for non-plugin users. Register the
      project name, set up trusted publishing from GitHub Actions, cut a
      0.2.0 release.

- [ ] **Cold-start latency on first plugin use.** First `uvx` invocation
      after `claude plugin add` downloads ~100 packages (lxml, onnxruntime,
      pypdfium2, etc.) and takes ~30 seconds. Subsequent invocations hit
      uv's cache and are ~1s. Consider pre-warming the cache at plugin-add
      time (via a Claude Code install hook, if one ever gets blessed) or
      leaning on the skill-first UX where the agent can answer before the
      MCP is cold-started.

## Known regressions / bugs

- [ ] **`mpep.search()` returns 0 hits for plausible queries against the
      live endpoint.** Surfaced during 2026-04-22 e2e install-mode testing.
      `get_section()` still works. Upstream indexing issue or a client-side
      query-construction regression — investigate and either fix or file
      upstream.

- [ ] _(law-tools, pre-existing)_ Stale VCR cassettes for TSDR and Fed
      Reserve. 2 tests fail as-recorded; re-record and commit.

- [ ] _(law-tools, pre-existing)_ Missing `pdfplumber` dep blocks colline
      test collection. Add `pdfplumber` to the `colline` optional-deps group
      or drop the extra if no longer used.

## Tech debt (carried forward)

- [ ] **EPO OPS client has no retry logic.** Doesn't inherit from
      `BaseAsyncClient` and doesn't use `law_tools_core.resilience`. Transient
      network errors surface as raw exceptions. Migrate to `BaseAsyncClient`
      or at minimum wrap in `default_retryer`.

- [ ] **Google Patents and JPO clients duplicate retry logic** instead of
      using `law_tools_core.resilience`. Consolidate.

- [ ] **JPO module has 0% test coverage.** Credentials are restricted so
      VCR cassettes are the pragmatic answer — record once against a known
      good fixture set.

- [ ] **USPTO Publications `_poll_print_job()` has no timeout.** A stuck
      job will hang indefinitely. Add a bounded poll with `anyio.fail_after`.

- [ ] **USPTO assignments / ODP / publications modules have no logging.**
      Log failures at WARNING with the log-file path convention (see
      `law_tools_core.logging`).

## Documentation

- [ ] **Skill `references/*.md` content needs a refresh pass.** Several
      reference files describe the pre-extraction API surface (law-tools
      module names). The extraction plan memory flagged this; still not
      done.

- [ ] **Monorepo `CLAUDE.md` doesn't list ip-tools as a library-backed
      skill.** Add to the skills directory in the top-level README/CLAUDE.

- [ ] **API docs under `docs/api/` lag the current module layout.** Cross-
      check every file in `src/ip_tools/` against `docs/api/` and fill the
      gaps (office_actions, bulk_data, petitions).

## Remote MCP deployment

- [ ] **Stand up a real remote MCP endpoint.** Deploy artifacts are ready
      in `deploy/` (systemd unit, nginx config, env template, step-by-step
      guide). Missing: a host, DNS, a TLS cert, and a first bearer token.
      Once up, swap `mcp.example.com` references in the docs for the real
      hostname.

- [ ] **CI auto-deploy on merge to `main`.** Model on `tools/law-tools/`'s
      GCP-WIF workflow (`.github/workflows/deploy.yml.disabled`) but
      generic — no firm-specific identity federation. GitHub Secrets:
      `REMOTE_HOST`, `REMOTE_SSH_KEY`, `LAW_TOOLS_CORE_API_KEY`.

## Nice to have

- [ ] **Cowork UI screenshots** for the installation guide. Text directions
      in [docs/installation.md §6](docs/installation.md#6-remote-mcp--cowork)
      are based on the described flow; screenshots would disambiguate.

- [ ] **`ip-tools-mcp --help` / `--version`.** The console script is a
      bare `mcp.run()` today. Add a thin argparse wrapper so `ip-tools-mcp --version`
      prints the package version and `--help` points at the docs.

- [ ] **Migrate the skill's `install.sh` to use `uv` or `pipx`** instead
      of `pip install --user`. Works everywhere, avoids PATH confusion.
