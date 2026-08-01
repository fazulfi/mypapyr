# C4 Evidence — Malware Scanner (ClamAV) and CI Scanning (Trivy)

- **Access date:** 2026-07-31
- **Purpose:** primary-source evidence for `c4-vps-processing-hardening.md` (malware scanner selection, update channel, safe-failure, resource profile)
- **Method:** read-only fetch of official ClamAV documentation. No installs, no scanning, no live samples.

## 1. ClamAV overview and license

Sources: `https://docs.clamav.net/` and `https://docs.clamav.net/manual/Usage/Configuration.html` (accessed 2026-07-31).

- "ClamAV is an open source (GPLv2) anti-virus toolkit, designed especially for e-mail scanning on mail gateways… a flexible and scalable multi-threaded daemon, a command line scanner and advanced tool for automatic database updates." Maintained by Cisco Systems, Inc. (Talos).
- Supported formats include **PDF** (under "Support for other special files/formats"), HTML, RTF, OLE2/OOXML, archives (Zip, RAR, 7Zip, Tar, Gzip, Bzip2, DMG, ISO…), PE/ELF/Mach-O, mail files. Archive-bomb protection built in. Signed signature databases; bytecode signature runtime.
- **Honest-limits framing:** "ClamAV is not a traditional anti-virus or endpoint security suite." Format support disclaimer: "We cannot guarantee that we can unpack or extract every version or variant of the listed formats." → ClamAV is one defense layer; no malware-free guarantees (aligns with DEC-171).
- **Minimum recommended system requirements** (clamscan/clamd with the standard signature DB): **3 GiB+ RAM** (server edition); 1 CPU at 2.0 GHz+; ~5 GiB free disk. Docker note: "Server environments, like Docker, as well as and embedded runtime environments are often resource constrained. We recommend at 3-4 GiB of RAM, but you may get by with less if you're willing to accept some limitations." (Link: `https://docs.clamav.net/manual/Installing/Docker.html#memory-ram-requirements`.)
- Malware/false-positive submissions to Talos: ≥48 h to signature publication; files kept indefinitely by Cisco Talos (submission flow only, not production scanning).

## 2. clamd / freshclam configuration

Source: `https://docs.clamav.net/manual/Usage/Configuration.html` (accessed 2026-07-31).

- `freshclam` (automatic DB updater): daemon mode (`freshclam -d`) or cron; official guidance for hourly checks via cron with a non-multiple-of-10 minute ("N between 3 and 57… don't choose a multiple of 10"). Supports scripted (diff) updates, DNS version checks, digital signatures, proxy auth.
- freshclam options: `LogTime`, `LogRotate`, `NotifyClamd`, `DatabaseOwner`. DB directory owned by the DB owner user; clamd needs read access.
- `clamd.conf`: `LocalSocket` (unix socket, e.g., `/tmp/clamd.socket`), `LocalSocketMode`, `User`, `ScanOnAccess`/`OnAccessIncludePath`/`OnAccessExcludePath`/`OnAccessPrevention`, logging options. Resource/size knobs (`MaxScanSize`, `MaxFileSize`, `MaxFiles`, `MaxThreads`, `StreamMaxLength`, `ExtendedDetectionInfo`, etc.) are defined in the well-commented `clamd.conf.sample` (referenced; full current values verified at implementation). SELinux note: `antivirus_can_scan_system` / `clamd_can_scan_system` booleans.
- On-access scanning (ClamOnAcc) available on Linux; for this design, **on-demand scanning at admission** (clamd over the local socket) is the documented, low-complexity pattern.
- Scan result semantics: clamdscan/clamscan exit codes — 0 = no virus found, 1 = virus(es) found, 2 = error (documented in the ClamAV man/usage pages, referenced). These exit codes support fail-closed logic: an error (2) or daemon-down condition must be treated as "cannot confirm clean" → reject with a safe category per DEC-171/C4 recommendation.

## 3. Container image

- Official Docker image: `docker.io/clamav/clamav` (Docker Hub `clamav/clamav`; docs at `https://docs.clamav.net/manual/Installing/Docker.html`, referenced). Image runs clamd + freshclam; signature DB in a volume; resource constraints (especially RAM per §1) apply.

## 4. Trivy (CI container scanning)

Source: `https://aquasecurity.github.io/trivy/` (accessed 2026-07-31, referenced).

- Open-source (Apache-2.0) comprehensive scanner for container images, filesystems, git repos; vulnerability DB update; CI usage (exit-code gating, severity filters). Legacy precedent: `papyr-reference/.github/workflows/deploy-vps.yml:58-71` gates CRITICAL with `ignore-unfixed: true` in the deploy pipeline (evidence file for DEC-177 core-gate security scan).

## Uncertainties

- Exact `clamd.conf` resource-limit defaults and current ClamAV stable version number: verify at implementation against `docs.clamav.net` (version page referenced).
- Whether ClamAV's PDF inspection covers the active-content categories Papyr sanitizes (DEC-090): ClamAV detects malware signatures in PDFs but is not a PDF sanitizer; Papyr's own sanitization layer remains required. Recorded as a design conclusion, not a doc claim.

## Source list

| # | URL | Accessed |
|---|---|---|
| 1 | https://docs.clamav.net/ | 2026-07-31 |
| 2 | https://docs.clamav.net/manual/Usage/Configuration.html | 2026-07-31 |
| 3 | https://docs.clamav.net/manual/Installing/Docker.html | 2026-07-31 (referenced) |
| 4 | https://aquasecurity.github.io/trivy/ | 2026-07-31 (referenced) |
