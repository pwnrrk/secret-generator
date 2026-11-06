#!/usr/bin/env python3
"""Interactive secret generator wizard.

Generates cryptographically secure secrets (via the `secrets` module) for
common use cases: API keys, JWT secrets, passwords, encryption keys, etc.
"""

import base64
import secrets
import string
import sys
import uuid

# ---------------------------------------------------------------------------
# Usage presets
# key: (label, description, default_bytes_or_length, default_format)
# ---------------------------------------------------------------------------
PRESETS = {
    "1": {
        "label": "API Key",
        "desc": "Prefixed token, e.g. sk_live_xxxxx",
        "length": 32,
        "format": "base62",
        "prefix": True,
    },
    "2": {
        "label": "JWT Secret",
        "desc": "HMAC signing secret (HS256 needs >= 32 bytes, HS512 >= 64)",
        "length": 64,
        "format": "base64url",
        "prefix": False,
    },
    "3": {
        "label": "Password",
        "desc": "Human-typeable password with mixed characters",
        "length": 24,
        "format": "password",
        "prefix": False,
    },
    "4": {
        "label": "Encryption Key",
        "desc": "Raw key for AES etc. (16=AES-128, 24=AES-192, 32=AES-256)",
        "length": 32,
        "format": "hex",
        "prefix": False,
    },
    "5": {
        "label": "Session / CSRF Secret",
        "desc": "Web framework SECRET_KEY (Django, Flask, Rails)",
        "length": 50,
        "format": "base64url",
        "prefix": False,
    },
    "6": {
        "label": "Webhook Secret",
        "desc": "Signing secret for verifying webhooks",
        "length": 32,
        "format": "hex",
        "prefix": True,
    },
    "7": {
        "label": "UUID v4",
        "desc": "Random UUID (identifier, not a strong secret)",
        "length": None,
        "format": "uuid",
        "prefix": False,
    },
    "8": {
        "label": "Custom",
        "desc": "Choose length and format yourself",
        "length": 32,
        "format": "hex",
        "prefix": True,
    },
}

FORMATS = {
    "1": ("hex", "Hexadecimal (0-9, a-f)"),
    "2": ("base64", "Base64 (standard)"),
    "3": ("base64url", "Base64 URL-safe (no +, /, =)"),
    "4": ("base62", "Alphanumeric (A-Z, a-z, 0-9)"),
    "5": ("password", "Password (letters, digits, symbols)"),
}

BASE62 = string.ascii_letters + string.digits
PASSWORD_SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------
def gen_password(length: int, symbols: bool = True) -> str:
    """Password guaranteed to contain lower, upper, digit (and symbol)."""
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        pools.append(PASSWORD_SYMBOLS)
    alphabet = "".join(pools)
    if length < len(pools):
        raise ValueError(f"Password length must be at least {len(pools)}.")
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if all(any(c in pool for c in pwd) for pool in pools):
            return pwd


def generate(fmt: str, length: int, symbols: bool = True) -> str:
    """Generate a secret. `length` = bytes of entropy for hex/base64 formats,
    and number of characters for base62/password."""
    if fmt == "uuid":
        return str(uuid.uuid4())
    if fmt == "hex":
        return secrets.token_hex(length)
    if fmt == "base64":
        return base64.b64encode(secrets.token_bytes(length)).decode()
    if fmt == "base64url":
        return secrets.token_urlsafe(length)
    if fmt == "base62":
        return "".join(secrets.choice(BASE62) for _ in range(length))
    if fmt == "password":
        return gen_password(length, symbols)
    raise ValueError(f"Unknown format: {fmt}")


# ---------------------------------------------------------------------------
# Wizard helpers
# ---------------------------------------------------------------------------
def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        print()
        sys.exit(1)
    return answer or (default or "")


def ask_choice(prompt: str, valid: list[str], default: str | None = None) -> str:
    while True:
        answer = ask(prompt, default)
        if answer in valid:
            return answer
        print(f"  Please choose one of: {', '.join(valid)}")


def ask_int(prompt: str, default: int, minimum: int = 1, maximum: int = 4096) -> int:
    while True:
        answer = ask(prompt, str(default))
        try:
            value = int(answer)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if minimum <= value <= maximum:
            return value
        print(f"  Value must be between {minimum} and {maximum}.")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    d = "Y/n" if default else "y/N"
    while True:
        answer = ask(f"{prompt} ({d})").lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please answer y or n.")


def banner() -> None:
    print("=" * 52)
    print("  Secret Generator Wizard")
    print("  Cryptographically secure (Python `secrets`)")
    print("=" * 52)


def entropy_bits(fmt: str, length: int, symbols: bool) -> int | None:
    import math

    if fmt in ("hex", "base64", "base64url"):
        return length * 8
    if fmt == "base62":
        return int(length * math.log2(len(BASE62)))
    if fmt == "password":
        size = len(BASE62) + (len(PASSWORD_SYMBOLS) if symbols else 0)
        return int(length * math.log2(size))
    if fmt == "uuid":
        return 122
    return None


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------
def run_wizard() -> None:
    banner()

    # Step 1: usage
    print("\nStep 1/5 - What is the secret for?\n")
    for key, p in PRESETS.items():
        print(f"  {key}. {p['label']:<22} {p['desc']}")
    choice = ask_choice("\nSelect usage", list(PRESETS), "1")
    preset = PRESETS[choice]
    fmt = preset["format"]
    length = preset["length"]
    symbols = True

    # Step 2: format
    if fmt != "uuid":
        print(f"\nStep 2/5 - Output format (recommended: {fmt})\n")
        for key, (name, desc) in FORMATS.items():
            mark = "*" if name == fmt else " "
            print(f" {mark}{key}. {desc}")
        default_fmt = next(k for k, (n, _) in FORMATS.items() if n == fmt)
        if choice == "8" or ask_yes_no("\nChange the format?", False):
            fmt_key = ask_choice("Select format", list(FORMATS), default_fmt)
            fmt = FORMATS[fmt_key][0]
    else:
        print("\nStep 2/5 - Format: UUID v4 (fixed)")

    # Step 3: length
    if fmt != "uuid":
        unit = "bytes of entropy" if fmt in ("hex", "base64", "base64url") else "characters"
        print(f"\nStep 3/5 - Length in {unit}")
        if choice == "2":
            print("  Tip: HS256 -> 32+, HS384 -> 48+, HS512 -> 64+ bytes.")
        if choice == "4":
            print("  Tip: 16 = AES-128, 24 = AES-192, 32 = AES-256.")
        min_len = 4 if fmt == "password" else 8 if fmt == "base62" else 8
        length = ask_int("Length", length or 32, minimum=min_len)
        if fmt == "password":
            symbols = ask_yes_no("Include symbols?", True)
    else:
        print("\nStep 3/5 - Length: n/a for UUID")

    # Step 4: prefix
    prefix = ""
    print("\nStep 4/5 - Prefix")
    if preset["prefix"] and fmt != "uuid":
        default_prefix = {"1": "sk_live_", "6": "whsec_"}.get(choice, "")
        prefix = ask(
            "Prefix (e.g. sk_live_, pk_test_; blank for none)",
            default_prefix or None,
        )
    else:
        print("  Not applicable for this usage.")

    # Step 5: count
    print("\nStep 5/5 - How many?")
    count = ask_int("Count", 1, minimum=1, maximum=100)

    # Generate
    print("\n" + "-" * 52)
    secrets_out = [prefix + generate(fmt, length, symbols) for _ in range(count)]
    for s in secrets_out:
        print(s)
    print("-" * 52)

    bits = entropy_bits(fmt, length or 0, symbols)
    if bits:
        print(f"Approx. entropy: {bits} bits")
    print("Store it in a secrets manager or env var. Never commit it to git.")

    # Optional: env-style output / save
    if ask_yes_no("\nPrint as .env line?", False):
        var = ask("Variable name", preset["label"].upper().replace(" / ", "_").replace(" ", "_"))
        for i, s in enumerate(secrets_out, 1):
            name = var if count == 1 else f"{var}_{i}"
            print(f"{name}={s}")

    if ask_yes_no("Save to a file? (permissions set to 600)", False):
        import os

        path = ask("Filename", "secrets.txt")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(secrets_out) + "\n")
        print(f"Saved to {path}")


def main() -> None:
    try:
        while True:
            run_wizard()
            if not ask_yes_no("\nGenerate another?", False):
                break
            print()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()


