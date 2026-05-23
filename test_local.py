#!/usr/bin/env python3
"""
Local test script for Holehe Actor
Run this to test the actor logic without Apify infrastructure
"""

import trio
import httpx
import json
from holehe.core import import_submodules, get_functions, launch_module
import holehe.modules as modules


async def test_holehe_actor():
    # Simulate actor input
    email = "test@example.com"
    only_used = True
    no_password_recovery = False
    timeout = 30
    
    print(f'🔍 Checking email: {email}')
    
    # Import all holehe modules
    all_modules = import_submodules(modules)
    
    # Get all check functions (with password recovery filter if needed)
    class Args:
        nopasswordrecovery = no_password_recovery
    
    websites = get_functions(all_modules, Args() if no_password_recovery else None)
    
    print(f'📊 Total modules to check: {len(websites)}')
    
    # Create HTTP client with custom timeout
    client = httpx.AsyncClient(timeout=float(timeout))
    
    results = []
    accounts_found = 0
    rate_limited = 0
    errors = 0
    
    try:
        # Run all checks
        for i, website_func in enumerate(websites):
            try:
                out = []
                await launch_module(website_func, email, client, out)
                
                if out:
                    result = out[0]
                    
                    # Only add to results if account exists (when only_used is True)
                    if only_used and not result.get('exists'):
                        continue
                    
                    results.append(result)
                    
                    # Count statistics
                    if result.get('exists'):
                        accounts_found += 1
                        print(f'✅ [{i+1}/{len(websites)}] Found on {result.get("name", "unknown")}')
                    
                    if result.get('rateLimit'):
                        rate_limited += 1
                        print(f'⚠️  [{i+1}/{len(websites)}] Rate limited on {result.get("name", "unknown")}')
            
            except Exception as e:
                errors += 1
                print(f'❌ Error checking module: {str(e)}')
    
    finally:
        await client.aclose()
    
    # Prepare final output
    output = {
        'email': email,
        'totalChecked': len(websites),
        'accountsFound': accounts_found,
        'rateLimited': rate_limited,
        'errors': errors,
        'results': results,
        'summary': {
            'existsOn': [r['name'] for r in results if r.get('exists')],
            'notFoundOn': [r['name'] for r in results if not r.get('exists')],
            'rateLimitedOn': [r['name'] for r in results if r.get('rateLimit')]
        }
    }
    
    print(f'\n✅ Check complete! Found on {accounts_found}/{len(websites)} platforms')
    print(f'📈 Rate limited: {rate_limited}, Errors: {errors}')
    print(f'\n📄 Sample output:')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    trio.run(test_holehe_actor)
