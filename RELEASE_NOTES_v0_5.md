# Affinity Atlas v0.5 — Public deployment preparation

This is a staging release, **not a live hosted deployment**. All Qloo + LLM live evidence is from local v0.4, not from this package.

Changes:

- `render.yaml` for free-tier Python hosting with required server-held Qloo and remote LLM credentials.
- `ATLAS_PUBLIC_DEMO=1` opt-in mode; non-loopback binding without it is refused at startup.
- Public startup fails closed without server-held Qloo key and a configured authenticated HTTPS LLM endpoint.
- Process-local global rolling demo quotas (hourly, daily, concurrent) and HTTP 429 on saturation.
- Public requests ignore any browser-supplied Qloo key. Local demo remains compatible with v0.4.
- Rejects non-JSON POST content types; adds modest security response headers.
- 5 offline tests added to the 27 inherited: 32 total PASS.

**Not yet proven / limitations:** no cloud deploy, no remote LLM trial, no rotated Qloo key, no public Git repo, no external uptime guarantee. Process-local limits reset on restart/spin-down and are NOT reliable cost controls. Render Free sleeps when idle. Set provider-side quotas and monitor before publication; use a paid durable quota store or edge provider throttling for significant traffic. The public-facing HTTP server remains an intentionally lightweight demo server and requires additional hardening for general production use.
