# Tektolo skills and connector

[![smithery badge](https://smithery.ai/badge/tektolo/rental-property)](https://smithery.ai/servers/tektolo/rental-property)

Agent skills, a Claude Code plugin and the public API contract for **[Tektolo](https://tektolo.com)**. Tektolo runs rules-based, source-cited tools for real-world operations work: you send structured inputs, versioned rules are applied, and you get a checked answer with its sources. The same findings always get the same answer. Where a tool reads your notes or a document, an AI model turns them into findings and never sets a number; the answer lists every finding it read so you can check them. Every tool can be used three ways: on the web, from an AI assistant over MCP, or over REST.

This repository holds only instructions and public metadata. The engines and rule tables run on tektolo.com. Every file here is synced from the live site daily by [`scripts/sync.py`](scripts/sync.py).

## Tools

<!-- tools:start -->
| Tool | What it does | MCP tools | Links |
|---|---|---|---|
| **Property turnover estimate** | Turn move-out inspection findings into a priced, vendor-ready make-ready scope. | `property_turnover_quick_estimate`, `property_turnover_scope`, `property_turnover_issue_codes` | [web tool](https://tektolo.com/tools/rental-property/property-turnover) · [reference](https://tektolo.com/capabilities/property-turnover) · [skill](skills/property-turnover/SKILL.md) |
| **Deposit settlement** | Settle a US rental security deposit under the state's rule (and a covered city's): the return deadline, each deduction assessed (allowed category, depreciation, documentation), interest owed, the refund, penalty exposure and a draft itemized statement, every number cited. | `deposit_settlement_settle`, `deposit_settlement_rules` | [web tool](https://tektolo.com/tools/rental-property/deposit-settlement) · [reference](https://tektolo.com/capabilities/deposit-settlement) · [skill](skills/deposit-settlement/SKILL.md) |

Pricing: Try every tool free. Agents and software get a free tier of 20 calls a day. Some tools will add paid features. Details: https://tektolo.com/pricing
<!-- tools:end -->

## Use it from your AI assistant

The MCP server is `https://tektolo.com/mcp`. It uses streamable HTTP and needs no account. For your own free allowance behind Claude's or ChatGPT's shared servers, get a personal connector URL at [tektolo.com/connect-your-ai](https://tektolo.com/connect-your-ai).

**Claude Code**: install the plugin, which bundles the skills and the MCP server:

```bash
claude plugin marketplace add tektolo/skills
claude plugin install tektolo@tektolo
```

Or connect only the server:

```bash
claude mcp add --transport http tektolo https://tektolo.com/mcp
```

**Skills for any agent that reads `SKILL.md`** (Claude Code, Codex, Cursor, Gemini CLI, Copilot and others):

```bash
npx skills add tektolo/skills
```

**Claude, ChatGPT, Cursor, VS Code:** add a custom connector with the URL above. Step-by-step instructions are at [tektolo.com/connect-your-ai](https://tektolo.com/connect-your-ai).

**OpenClaw:** both skills are also on [ClawHub](https://clawhub.ai) under `@tektolo`.

## Use it over REST

Every MCP tool is also a plain JSON endpoint. [`contract/openapi.json`](contract/openapi.json) describes them, and [`contract/catalog.json`](contract/catalog.json) lists every operation with its schemas, pricing, privacy notes and ruleset hash. Request bodies that work are in [`examples/`](examples/):

```bash
curl -sS https://tektolo.com/v1/deposit-settlement/settle \
  -H 'content-type: application/json' \
  -d @examples/deposit-settlement/settle/california_carpet.json
```

## What's here

| Path | What it is |
|---|---|
| `skills/<tool>/SKILL.md` | agent skills (the open SKILL.md format) |
| `plugins/tektolo/` | Claude Code plugin: the same skills plus `.mcp.json` |
| `.claude-plugin/marketplace.json` | makes this repo a Claude Code plugin marketplace |
| `contract/` | `catalog.json`, `openapi.json`, the MCP server card and `llms.txt`, as served |
| `examples/` | request bodies taken from the catalog |

## Feedback and contact

Report a wrong result or suggest a tool at [tektolo.com/contact](https://tektolo.com/contact), or email hello@tektolo.com. Issues on this repository are welcome too.

## License

The skills, examples and docs in this repository are MIT-0 (see [LICENSE](LICENSE)). Using the Tektolo service is covered by its [Terms of Use](https://tektolo.com/terms) and [Privacy Policy](https://tektolo.com/privacy). Results are estimates under cited rules, not legal advice ([disclaimer](https://tektolo.com/disclaimer)).
