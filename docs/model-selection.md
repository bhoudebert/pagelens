# Model selection

## Retrieval model

The default is Ollama's `embeddinggemma-2:440m-q8_0-text-vision`. It accepts text and
images and emits normalized 768-dimensional vectors in one comparable space. It avoids a
separate Torch/Transformers runtime. Override it with
`PAGELENS_EMBEDDING_MODEL` or the CLI `--model` option. Changing models requires
rebuilding the collection because vectors from different models are not comparable.

## Verification model

The default Ollama verifier is `qwen3-vl:8b-instruct`, a 6.2 GB Q4 model that accepts both
text and image input. It requires Ollama 0.12.7 or newer and is configurable through
`PAGELENS_OLLAMA_MODEL`. Verification is opt-in because it is slower than retrieval. The
server defaults to `http://127.0.0.1:11434`.

## High CPU usage while the GPU is in use

Observed on Ollama 0.40.4 (CUDA, RTX 5080 16 GB, Ryzen 9 9950X3D): during `--verify` the
`llama-server` runner of the verification model sat at 550-750% CPU even though
`ollama ps` reported `100% GPU` and the log showed all layers (and the vision encoder)
offloaded to CUDA.

Cause: the runner starts a CPU thread pool of one thread per physical core (`n_threads = 8`)
and a few small ops stay on the CPU (`graph splits = 2`). Those threads busy-spin on every
generated token, so the GPU does the work while the cores stay pegged. `pagelens verify`
sends many requests back to back, so the runner never idles. Measured, text-only requests:

| Model | `llama-server` CPU |
| --- | --- |
| `qwen3:8b` | ~70% |
| `gemma4:12b` | ~440% |
| `qwen3-vl:8b-instruct` | ~690% |

It is not caused by images or `format: json`; text-only requests without a JSON format
gave the same load. A per-request `options.num_thread` is ignored, because the runner is
already running with `-t 8`. Set it in a Modelfile, which sets the runner's launch args:

```
FROM qwen3-vl:8b-instruct
PARAMETER num_thread 2
```

```bash
ollama create qwen3-vl-t2 -f Modelfile
PAGELENS_OLLAMA_MODEL=qwen3-vl-t2 pagelens query "..." --verify
```

With `-t 2` the runner dropped from ~690% to ~190% CPU. Request latency was not
benchmarked. The same trick applies to the embedding model if it shows the same behavior.

## Model cache and privacy

Model weights are managed by Ollama. After they are pulled, indexing and retrieval can run
offline. PDF contents and crops remain local. Ollama requests go only to the configured
server; setting a remote server explicitly changes that privacy boundary.

