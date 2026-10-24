from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from typing import cast

import pymupdf

from pagelens.domain.models import EvidenceMode, SearchResult, Verification


class OllamaVerifier:
    def __init__(
        self,
        base_url: str,
        model: str,
        evidence_mode: EvidenceMode = EvidenceMode.VISUAL,
        timeout: float = 120.0,
    ) -> None:
        self._endpoint = f"{base_url.rstrip('/')}/api/chat"
        self._model = model
        self._evidence_mode = evidence_mode
        self._timeout = timeout

    def verify(self, query: str, candidate: SearchResult) -> Verification:
        crop = base64.b64encode(candidate.preview_path.read_bytes()).decode("ascii")
        page = base64.b64encode(_render_page(candidate)).decode("ascii")
        evidence_rule = (
            "Confirm only when the requested object itself is visibly depicted in Image 1 or "
            "Image 2. A label, caption, or text-only mention does not count as visual evidence; "
            "text may only provide metadata for a visibly depicted object."
            if self._evidence_mode is EvidenceMode.VISUAL
            else (
                "Confirm when the requested item is either visibly depicted or explicitly "
                "supported by the supplied page text."
            )
        )
        prompt = f"""You verify evidence retrieved from a PDF.

User request: {query}
Text spatially associated with this crop:
{candidate.text or "(none)"}

Image 1 is the strongest matching page crop. Image 2 is the complete source page.
Evidence policy ({self._evidence_mode.value}): {evidence_rule}

Classify only what the user actually requested and obey the evidence policy above:
- confirmed: the requested object is supported by an allowed evidence source. For a broad
  category such as "motorcycle" or "water pump", clearly seeing that object is sufficient;
  an exact manufacturer or model is not required. Apply broad category meaning literally;
  do not assume a related component is present just because the page describes a system.
- rejected: the evidence shows a different object or the requested object is absent.
- uncertain: the requested object itself cannot be decided because it is obscured,
  ambiguous, or illegible. Do not use uncertain merely because optional metadata is absent.

Set evidence_source to visual when the object is visibly depicted, text when only words
support it, both when both do, and none when neither does. In visual mode, a diagram symbol
counts only if it clearly depicts the requested object; do not infer an unshown component
from the system or process around it.

Similar appearance alone does not prove an exact manufacturer or model when exact identity
was requested. When rejecting, object_type should name the actual visible object, not repeat
the requested object. Extract values only when visible in the images or supplied text.
Return JSON with exactly these fields:
status (confirmed, rejected, or uncertain), evidence_source (visual, text, both, or none),
object_type, manufacturer, model, reference, evidence (array of short strings), confidence
(number from 0 to 1).
"""
        body = json.dumps(
            {
                "model": self._model,
                "messages": [{"role": "user", "content": prompt, "images": [crop, page]}],
                "format": "json",
                "stream": False,
                "options": {"temperature": 0},
            }
        ).encode()
        request = urllib.request.Request(
            self._endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                payload = json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            raise RuntimeError(f"Ollama request failed: {error}") from error
        try:
            content = payload["message"]["content"]
            verification = Verification.model_validate_json(content)
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError("Ollama returned an invalid verification response") from error
        if (
            self._evidence_mode is EvidenceMode.VISUAL
            and verification.status == "confirmed"
            and verification.evidence_source not in {"visual", "both"}
        ):
            return verification.model_copy(
                update={
                    "status": "rejected",
                    "evidence": [
                        "Rejected: the verifier did not identify visible-object evidence "
                        "required by the visual policy."
                    ],
                }
            )
        return verification


def _render_page(candidate: SearchResult) -> bytes:
    """Render one-based source page context for the vision verifier."""
    with pymupdf.open(candidate.source_path) as document:  # type: ignore[no-untyped-call]
        page_index = candidate.page - 1
        if page_index < 0 or page_index >= document.page_count:
            raise RuntimeError(
                f"stored page {candidate.page} is outside {candidate.source_path.name}"
            )
        pixmap = document[page_index].get_pixmap(dpi=110, alpha=False)
        return cast(bytes, pixmap.tobytes("jpeg", jpg_quality=82))
