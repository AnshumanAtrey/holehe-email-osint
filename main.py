import asyncio
import trio
import httpx
from apify import Actor
from holehe.core import import_submodules, get_functions, launch_module
import holehe.modules as modules
from functools import partial


async def run_holehe_checks(email, websites, only_used, timeout):
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
        'errors': errors
    }


async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        email = actor_input.get('email')
        only_used = actor_input.get('onlyUsed', False)
        no_password_recovery = actor_input.get('noPasswordRecovery', False)
        timeout = actor_input.get('timeout', 30)

        if not email:
            await Actor.fail('Email is required!')
            return

        Actor.log.info(f'🔍 Checking email: {email}')

        all_modules = import_submodules(modules)

        class Args:
            nopasswordrecovery = no_password_recovery

        websites = get_functions(all_modules, Args() if no_password_recovery else None)

        Actor.log.info(f'📊 Total modules to check: {len(websites)}')

        loop = asyncio.get_event_loop()
        check_func = partial(trio.run, run_holehe_checks, email, websites, only_used, timeout)

        Actor.log.info('🚀 Starting checks...')
        check_results = await loop.run_in_executor(None, check_func)

        results = check_results['results']
        accounts_found = check_results['accounts_found']
        rate_limited = check_results['rate_limited']
        errors = check_results['errors']

        await Actor.charge('email-check-completed')

        summary = {
            'email': email,
            'totalChecked': len(websites),
            'accountsFound': accounts_found,
            'rateLimited': rate_limited,
            'errors': errors,
            'existsOn': [r['name'] for r in results if r.get('exists')],
            'notFoundOn': [r['name'] for r in results if not r.get('exists')],
            'rateLimitedOn': [r['name'] for r in results if r.get('rateLimit')],
        }
        await Actor.push_data(summary)

        for r in results:
            if r.get('exists'):
                await Actor.push_data({
                    'email': email,
                    'platform': r.get('name'),
                    'exists': True,
                    'category': r.get('category'),
                    'domain': r.get('domain'),
                    'emailrecovery': r.get('emailrecovery'),
                    'phoneNumber': r.get('phoneNumber'),
                    'others': r.get('others'),
                }, 'account-found')

        Actor.log.info(f'✅ Check complete! Found on {accounts_found}/{len(websites)} platforms')
        Actor.log.info(f'📈 Rate limited: {rate_limited}, Errors: {errors}')


if __name__ == '__main__':
    asyncio.run(main())
