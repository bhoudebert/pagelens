# Notice

## Licence

Pagelens is open source under the MIT licence (see `LICENSE`). It is provided "as is",
without warranty of any kind.

## Models and services

Pagelens does not bundle model weights. It calls a local [Ollama](https://ollama.com) server,
and the models you pull have their own licences and terms, which apply to anything you
produce with them. Check them before commercial use.

| Component | Used for | Where its terms live |
| --- | --- | --- |
| `embeddinggemma-2:440m-q8_0-text-vision` (default) | Text and image embeddings | The model card and licence published with the model on Ollama |
| `qwen3-vl:8b-instruct` (default, optional) | Candidate verification | The model card and licence published with the model on Ollama |
| Ollama | Serving the models | Ollama's licence |
| Tesseract (optional) | OCR of scanned pages | Apache-2.0 |

## Libraries

PyMuPDF (AGPL-3.0 or a commercial licence from Artifex), NumPy, Pillow, Pydantic, Rich and
Typer. **PyMuPDF's AGPL terms matter if you distribute or host Pagelens as a service**:
review them, or obtain a commercial licence, before doing so.

## Test data

Everything under `testdata/` is fictional. The raster assets were generated for this
repository; prompts avoided brands, labels and watermarks. No real manufacturer, product
or customer document is represented.
