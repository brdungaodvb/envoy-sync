# envoy-sync

> CLI tool to sync and diff environment variables across multiple `.env` files and cloud secret managers.

---

## Installation

```bash
pip install envoy-sync
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install envoy-sync
```

---

## Usage

**Diff two `.env` files:**

```bash
envoy-sync diff .env.local .env.production
```

**Sync variables from one source to another:**

```bash
envoy-sync sync .env.local .env.staging
```

**Sync with a cloud secret manager (e.g., AWS Secrets Manager):**

```bash
envoy-sync sync .env.production aws://my-app/production
```

**Check for missing keys across multiple files:**

```bash
envoy-sync check .env.example .env.local .env.staging
```

Run `envoy-sync --help` to see all available commands and options.

---

## Supported Backends

- Local `.env` files
- AWS Secrets Manager
- GCP Secret Manager
- HashiCorp Vault

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).