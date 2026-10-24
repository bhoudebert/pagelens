# Security policy

## Scope and data handling

Pagelens processes files you point it at, locally. Page images and text are sent only to the
Ollama server in `PAGELENS_OLLAMA_URL` (default: `127.0.0.1`). Pointing that at a remote
host sends document content to it. Indexes and previews in `.pagelens*/` contain page
renderings and extracted text; protect them like the source PDFs.

Pagelens has no authentication, network service, or multi-user isolation.

## Reporting a vulnerability

Email **bhoudebert@gmail.com** with a description and reproduction steps. Please do not open
a public issue for security reports. Expect an acknowledgement within a few working days.
