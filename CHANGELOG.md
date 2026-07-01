# Changelog

## [1.1.0] - 2026-07-01

### Added
- Bulk mode: the new `emails` field accepts many addresses (up to 100 per run) and checks them concurrently, so a whole list can be processed in one run. This makes the long-standing "provide emails as an array" promise real.
- Email auto-clean: each address is trimmed, lowercased, and stripped of `mailto:` and `<>` wrappers before checking.
- Input validation: invalid entries are skipped with a warning instead of failing the whole batch; a run with no valid email fails fast with a clear reason.
- Clear end-of-run status message with per-run totals (emails checked, accounts found), including an explicit note when nothing was found.
- `recordType` field on every dataset item (`summary` or `account`) to make bulk output easy to split.

### Changed
- The single `email` field is kept for backward compatibility; the `emails` field is now the primary input.
- README input table and output example now match what the actor actually accepts and returns (was describing an `emails` array plus a `platforms` filter that did not exist).

### Notes
- Pricing is unchanged: pay-per-event, per email checked plus per account found. Bulk scales both linearly.
- Concurrency and a per-run email cap keep bulk runs inside the platform time and compute budget.

## [1.0.0] - 2024-11-10

### Added
- Initial release
- Support for 120+ platform checks
- Email validation
- Only show used accounts filter
- Skip password recovery option
- Configurable timeout
- Comprehensive error handling
- Progress logging
- Rate limit detection
