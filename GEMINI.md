# Tektolo: rental move-out tools

This extension connects the Tektolo MCP server (`tektolo`) and two skills, `property-turnover` and `deposit-settlement`. Use them when someone is closing out a US rental move-out: pricing the turnover work, or settling the security deposit.

- **Turnover estimate.** For plain notes ("dog urine stains in bedroom carpet"), call `property_turnover_quick_estimate`. For findings already matched to issue codes, call `property_turnover_scope` (`property_turnover_issue_codes` lists the codes). Ask for a 5-digit ZIP if it is missing; never guess one. The numbers are estimates, not quotes. Relay refer-outs first.
- **Deposit settlement.** Call `deposit_settlement_settle` with the state (and city), the deposit, the move-in and move-out dates and the intended deductions. Relay the return deadline and its status, the refund, any deductions not allowed and why, and each citation with its link. Penalty exposure is exposure, not a verdict. Relay the disclaimer word for word; the manager signs the statement. `deposit_settlement_rules` answers "what is the rule in my state?".
- Never invent dates, ages, amounts or ZIP codes. Relay the assumptions, unknowns and warnings each result lists.
- Send a ZIP code, never a street address, a tenant's name or a face in a photo.

The skills carry the full input and relay rules; load the matching one before the first call.
