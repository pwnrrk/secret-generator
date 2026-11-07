# Secret Generator

An interactive, wizard-style command-line tool for generating cryptographically secure secrets: API keys, JWT secrets, passwords, encryption keys and more.

Everything is generated with Python's built-in [`secrets`](https://docs.python.org/3/library/secrets.html) module. No third-party dependencies.

## Requirements

- Python 3.10 or newer

## Usage

```
python secret_generator.py
```

The wizard walks you through five steps:

| Step | What you choose |
|------|-----------------|
| 1. Usage | What the secret is for (see presets below) |
| 2. Format | Output encoding: hex, base64, base64url, alphanumeric, or password |
| 3. Length | Bytes of entropy (hex/base64) or number of characters (alphanumeric/password) |
| 4. Prefix | Optional prefix such as `sk_live_` (API keys and webhook secrets) |
| 5. Count | How many secrets to generate (1 to 100) |

Press Enter at any prompt to accept the default shown in `[brackets]`. Press Ctrl+C to cancel.

After generating, the tool shows the approximate entropy in bits and can optionally:

- print the result as `.env` lines (`NAME=value`)
- save the secrets to a file (created with `600` permissions on Unix-like systems)

## Presets

| # | Usage | Default format | Default length |
|---|-------|----------------|----------------|
| 1 | API Key | alphanumeric | 32 chars, prefix `sk_live_` |
| 2 | JWT Secret | base64url | 64 bytes |
| 3 | Password | password (with symbols) | 24 chars |
| 4 | Encryption Key | hex | 32 bytes (AES-256) |
| 5 | Session / CSRF Secret | base64url | 50 bytes |
| 6 | Webhook Secret | hex | 32 bytes, prefix `whsec_` |
| 7 | UUID v4 | uuid | n/a |
| 8 | Custom | hex | 32 bytes |

### Length guidance

- **JWT (HMAC):** HS256 needs at least 32 bytes, HS384 at least 48, HS512 at least 64.
- **AES keys:** 16 bytes = AES-128, 24 = AES-192, 32 = AES-256.
- **Passwords:** 16+ characters is a reasonable minimum. Generated passwords always contain lowercase, uppercase, a digit and (if enabled) a symbol.

Note that for `base64url`, the length is the number of random bytes. The resulting string is about 1.33 times longer.

## Example session

```
$ python secret_generator.py
====================================================
  Secret Generator Wizard
  Cryptographically secure (Python `secrets`)
====================================================

Step 1/5 - What is the secret for?

  1. API Key                Prefixed token, e.g. sk_live_xxxxx
  2. JWT Secret             HMAC signing secret (HS256 needs >= 32 bytes, HS512 >= 64)
  ...

Select usage [1]: 2
...
----------------------------------------------------
<your generated secret appears here>
----------------------------------------------------
Approx. entropy: 512 bits
Store it in a secrets manager or env var. Never commit it to git.
```

## Security notes

- Secrets are printed to your terminal and may remain in scrollback or shell history of your terminal emulator. Clear it if the secret is sensitive.
- Never commit secrets to version control. Use environment variables or a secrets manager.
- Saved files get `600` permissions on Unix-like systems. On Windows, file permissions are not restricted this way, so store the file somewhere protected.
- UUID v4 is an identifier, not a strong secret. Do not use it for authentication.

## License

Add your preferred license here.


