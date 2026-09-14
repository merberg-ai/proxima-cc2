# Proxima Dual Trust

Proxima will preserve the CC2 stock verification path and replace only the fallback community trust identity.

Target policy:

```text
ELEGOO stock signature
        OR
Proxima signature
```

The initial implementation will be derived from Neme77 Dual Trust v2, which injects an ARM verifier into the CC2 update daemon and embeds a 451-byte RSA public-key PEM.

## Reproducibility requirement

Before any bootstrap touches a printer, the Proxima updater must be constructed independently in two ways:

1. Rebuild the Dual Trust payload from assembly with the Proxima public key and patch the frozen stock daemon.
2. Replace exactly the embedded community public-key bytes in the known-good qualified Neme77 v3.7 daemon.

The two resulting updater binaries must be byte-for-byte identical. A mismatch is a hard failure.

Only the Proxima public key belongs in this repository. The matching private key must remain outside Git.
