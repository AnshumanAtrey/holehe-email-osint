# Holehe Email OSINT

Check if an email is registered on 120+ websites without alerting the target.

## What It Does

This actor checks if an email address is registered on popular platforms including Instagram, Twitter, GitHub, Discord, Amazon, Spotify, and 100+ more sites. Perfect for OSINT investigations and security research.

## Features

- ✅ Checks 120+ platforms simultaneously
- ✅ No alerts sent to the target email
- ✅ Fast async processing
- ✅ Detailed results with recovery information
- ✅ Rate limit detection

## Input

```json
{
  "email": "test@example.com",
  "onlyUsed": true,
  "noPasswordRecovery": false,
  "timeout": 30
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | String | Yes | Email address to check |
| `onlyUsed` | Boolean | No | Only show platforms where email is registered |
| `noPasswordRecovery` | Boolean | No | Skip password recovery detection methods |
| `timeout` | Integer | No | Request timeout in seconds (10-120, default: 30) |

## Output

```json
{
  "email": "test@example.com",
  "totalChecked": 123,
  "accountsFound": 15,
  "rateLimited": 2,
  "errors": 0,
  "results": [
    {
      "name": "instagram",
      "domain": "instagram.com",
      "exists": true,
      "emailrecovery": "te****@gmail.com",
      "phoneNumber": "+1****5678",
      "rateLimit": false
    }
  ],
  "summary": {
    "existsOn": ["instagram", "twitter", "github"],
    "notFoundOn": ["linkedin", "facebook"],
    "rateLimitedOn": ["spotify"]
  }
}
```

## Platforms Checked

**Social Media**: Instagram, Twitter, Facebook, TikTok, Snapchat, LinkedIn, Pinterest, Reddit

**Developer**: GitHub, GitLab, Stack Overflow, Docker Hub, npm, BitBucket

**Shopping**: Amazon, eBay, Etsy, AliExpress

**Entertainment**: Spotify, Netflix, Discord, Twitch, Steam

**And 100+ more platforms**

## Use Cases

- OSINT investigations
- Security research
- Digital footprint analysis
- Account discovery
- Background checks

## Rate Limiting

Some platforms may rate-limit requests. If you encounter rate limits:
- Enable Apify residential proxies
- Increase timeout value
- Run during off-peak hours

## Ethical Use

This tool is for **educational and legitimate security research purposes only**. Always:
- Obtain proper authorization
- Comply with local laws
- Respect privacy regulations
- Use responsibly

## Technical Details

- **Runtime**: 2-5 minutes per email
- **Memory**: 256-512 MB
- **Platforms**: 120+ modules
- **Based on**: [Holehe](https://github.com/megadose/holehe) by [@megadose](https://github.com/megadose)

## Integrations

This actor exposes a clean JSON API + webhooks, ready to drop into your existing pipeline:

- **Zapier** — trigger Holehe on new HubSpot/Pipedrive contact, push results to Google Sheets
- **Make (Integromat)** — lead-enrichment scenarios; route based on `accountsFound` count
- **n8n** — self-hosted workflows; the Apify node calls Holehe natively
- **Webhooks** — Apify dispatches on run completion; ingest into your own ETL
- **MCP Server** — exposed via the [Apify MCP Server](https://docs.apify.com/platform/integrations/mcp) for Claude / ChatGPT / Cursor agents
- **HTTP API + SDKs** — Python, Node.js, .NET, PHP

**Common lead-enrichment flow:** New lead → Holehe → if `accountsFound > 5` (active digital footprint) → enrich → send to sales rep.

## FAQ

### Does it alert the email owner?
**No.** Holehe uses platform login-flow probes that don't send confirmation, password-reset, or alert emails. Each platform is tested with a technique that leaves no trace in the user's inbox.

### How is this different from "email validator" tools?
Validators just check syntax + MX record. Holehe goes deeper — it tells you *which platforms* the email is registered on (Instagram, GitHub, Spotify, etc.). Validators say "this looks deliverable"; Holehe says "this person has accounts on 12 specific services."

### Can I use this for B2B cold email enrichment?
Yes. Most common use: feed Holehe a lead's email → if they're on LinkedIn + GitHub + Stack Overflow → they're a developer. Use that signal to personalize the outreach copy.

### Why does it sometimes say "rate limited"?
A handful of the 120+ platforms detect repeated probes. The actor logs which ones rate-limited so you know which signals to trust on a given run. Re-running 5-10 minutes later usually resets them.

### Is this legal?
Yes, in most jurisdictions — Holehe only checks publicly documented signup endpoints. You should still respect GDPR/CCPA/DPDP if you're collecting at scale; specifically, having a lawful basis for processing the data before storing it.

## Pairs nicely with

Bundle for richer OSINT workflows:

- **[NetIntel](https://apify.com/anshumanatrey/netintel)** — Unified WHOIS, DNS, GeoIP, SSL, port-scan intel for any domain or IP
- **[theHarvester](https://apify.com/anshumanatrey/theharvester-osint)** — Emails, subdomains, IPs, ASNs from 54 OSINT sources
- **[Social Analyzer](https://apify.com/anshumanatrey/social-analyzer)** — Find usernames across 900+ social platforms (great after Holehe finds an email registered on multiple sites)
- **[nmap](https://apify.com/anshumanatrey/nmap-scanner)** — Cloud port scanner + service detection + NSE scripts
- **[Bug Bounty Finder](https://apify.com/anshumanatrey/bug-bounty-finder)** — Find HackerOne/Bugcrowd programs for any target
- **[Zomato Restaurant Scraper](https://apify.com/anshumanatrey/zomato-restaurant-scraper)** — Restaurant lead lists by city (phone, address, cuisines)

## License

Built for educational purposes only. See [Holehe License](https://github.com/megadose/holehe/blob/master/LICENSE).
