# Security

## Data handling

Pagelens processes files you point it at, locally. Page images and text are sent only to
the Ollama server in `PAGELENS_OLLAMA_URL` (default `127.0.0.1`). Pointing it at a remote
host sends document content to that host. Indexes and previews in `.pagelens*/` contain
page renderings and extracted text; protect them like the source PDFs, and never commit
them (they are git-ignored).

Pagelens has no authentication, network service or multi-user isolation.

## Supply chain

Dependabot keeps Python and GitHub Actions dependencies current, and CodeQL scans the
code weekly and on pull requests. `flake.lock` pins the Nix toolchain.

## Reporting a vulnerability

Open a private security advisory on the repository, or email **bhoudebert@gmail.com**.
Please do not open a public issue for a vulnerability. Expect an acknowledgement within a
few working days.
