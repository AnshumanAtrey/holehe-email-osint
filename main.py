import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import trio
import httpx
from apify import Actor
from holehe.core import import_submodules, get_functions, launch_module
import holehe.modules as modules


MAX_EMAILS = 100          # cap per run so a bulk job stays inside the platform time budget
DEFAULT_CONCURRENCY = 10  # how many emails to check at once (each still checks ~120 sites)
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def clean_email(raw: str) -> str:
    """Normalize a pasted email: trim, drop mailto: and <> wrappers, lowercase."""
    if not raw:
        return ''
    s = str(raw).strip().strip('<>').strip()
    if s.lower().startswith('mailto:'):
        s = s[7:]
    return s.strip().lower()


def valid_email(e: str) -> bool:
    return bool(EMAIL_RE.match(e))


def collect_emails(actor_input: dict):
    """Gather emails from the bulk 'emails' field + legacy single 'email'.

    Accepts a list, or a comma/space separated string, plus the old single 'email'
    field for backward compatibility. Cleans each, drops duplicates, and splits out
    anything that is not a valid email so one bad entry never fails the whole batch.
    """
    raw = []
    ea = actor_input.get('emails')
    if isinstance(ea, list):
        raw.extend(ea)
    elif isinstance(ea, str) and ea.strip():
        raw.extend(re.split(r'[,\s]+', ea.strip()))
    single = actor_input.get('email')
    if single:
        raw.append(single)

    seen = set()
    valid, invalid = [], []
    for item in raw:
        c = clean_email(item)
        if not c:
            continue
        if valid_email(c):
            if c not in seen:
                seen.add(c)
                valid.append(c)
        else:
            invalid.append(str(item))
    return valid, invalid


async def run_holehe_checks(email, websites, only_used, timeout):
    """Check one email across every holehe module. Runs in a worker thread via trio."""
    results = []
    accounts_found = 0
    rate_limited = 0
    errors = 0

    async def check_all():
        nonlocal accounts_found, rate_limited, errors
        client = httpx.AsyncClient(timeout=timeout)
        try:
            for website_func in websites:
                try:
                    out = []
                    await launch_module(website_func, email, client, out)
                    if out:
                        result = out[0]
                        if only_used and not result.get('exists'):
                            continue
                        results.append(result)
                        if result.get('exists'):
                            accounts_found += 1
                        if result.get('rateLimit'):
                            rate_limited += 1
                except Exception:
                    errors += 1
        finally:
            await client.aclose()

    await check_all()
    return {
        'results': results,
        'accounts_found': accounts_found,
        'rate_limited': rate_limited,
        'errors': errors,
    }


async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        only_used = actor_input.get('onlyUsed', True)
        no_password_recovery = actor_input.get('noPasswordRecovery', False)
        timeout = actor_input.get('timeout', 30)

        # Collect + clean emails from the bulk field and the legacy single field.
        emails, invalid = collect_emails(actor_input)
        if invalid:
            Actor.log.warning(f'Skipping {len(invalid)} invalid entries: {invalid[:10]}')
        if not emails:
            await Actor.fail(status_message='No valid email given. Enter at least one address, e.g. name@example.com.')
            return
        if len(emails) > MAX_EMAILS:
            Actor.log.warning(f'{len(emails)} emails given; processing the first {MAX_EMAILS} this run.')
            emails = emails[:MAX_EMAILS]

        Actor.log.info(f'🔍 Checking {len(emails)} email(s)')

        # Load holehe modules once and reuse across every email.
        all_modules = import_submodules(modules)

        class Args:
            nopasswordrecovery = no_password_recovery

        websites = get_functions(all_modules, Args() if no_password_recovery else None)
        Actor.log.info(f'📊 Modules per email: {len(websites)}')

        loop = asyncio.get_event_loop()
        concurrency = min(DEFAULT_CONCURRENCY, len(emails))
        executor = ThreadPoolExecutor(max_workers=concurrency)
        sem = asyncio.Semaphore(concurrency)

        totals = {'emails': 0, 'accounts': 0, 'with_accounts': 0}

        async def process(email):
            async with sem:
                check_func = partial(trio.run, run_holehe_checks, email, websites, only_used, timeout)
                cr = await loop.run_in_executor(executor, check_func)

            # One charge per email actually checked (pay-per-event scales with bulk).
            await Actor.charge('email-check-completed')

            results = cr['results']
            found = cr['accounts_found']

            await Actor.push_data({
                'recordType': 'summary',
                'email': email,
                'totalChecked': len(websites),
                'accountsFound': found,
                'rateLimited': cr['rate_limited'],
                'errors': cr['errors'],
                'existsOn': [r['name'] for r in results if r.get('exists')],
                'rateLimitedOn': [r['name'] for r in results if r.get('rateLimit')],
            })

            # One record per account found, each charged as an 'account-found' event.
            for r in results:
                if r.get('exists'):
                    await Actor.push_data({
                        'recordType': 'account',
                        'email': email,
                        'platform': r.get('name'),
                        'exists': True,
                        'category': r.get('category'),
                        'domain': r.get('domain'),
                        'emailrecovery': r.get('emailrecovery'),
                        'phoneNumber': r.get('phoneNumber'),
                        'others': r.get('others'),
                    }, 'account-found')

            totals['emails'] += 1
            totals['accounts'] += found
            if found:
                totals['with_accounts'] += 1
            Actor.log.info(f'  ✓ {email}: {found} account(s)')
            return found

        await asyncio.gather(*(process(e) for e in emails))
        executor.shutdown(wait=False)

        # Clear end-of-run message so a 0-result run does not look like a broken one.
        if totals['accounts'] == 0:
            msg = (f"Checked {totals['emails']} email(s); found no registered accounts. "
                   f"These addresses may be unused, or the sites rate-limited the checks - try again or raise the timeout.")
        else:
            msg = (f"Checked {totals['emails']} email(s); found {totals['accounts']} account(s) "
                   f"across {totals['with_accounts']} email(s).")
        if invalid:
            msg += f" Skipped {len(invalid)} invalid entr{'y' if len(invalid) == 1 else 'ies'}."
        await Actor.set_status_message(msg)
        Actor.log.info(f'✅ {msg}')


if __name__ == '__main__':
    asyncio.run(main())
