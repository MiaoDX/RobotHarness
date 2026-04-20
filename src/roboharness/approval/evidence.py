"""Shared paired-evidence primitives for approval/report flows."""

from __future__ import annotations

import base64
import html
import mimetypes
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

EvidenceStatus = Literal["full", "ambiguous", "partial", "empty", "mismatch"]
CaptionBuilder = Callable[["EvidenceTarget", EvidenceStatus], str]
AmbiguitySelector = Callable[["EvidenceTarget"], bool]


@dataclass(frozen=True)
class MetricExplanation:
    """Single chip of explanatory text shown alongside paired evidence."""

    metric: str
    copy: str


@dataclass(frozen=True)
class EvidenceTarget:
    """One requested paired-evidence lookup under two bounded roots."""

    phase_id: str
    phase_label: str
    view_name: str
    current_relative_path: str
    baseline_relative_path: str
    forced_mismatch_message: str | None = None
    missing_current_message: str | None = None
    missing_baseline_message: str | None = None
    empty_message: str | None = None
    ambiguous_message: str | None = None


@dataclass
class EvidencePair:
    """Resolved paired evidence plus the UI copy needed to render it."""

    phase_id: str
    phase_label: str
    view_name: str
    current_image_path: Path | None
    baseline_image_path: Path | None
    status: EvidenceStatus
    metric_explanations: list[MetricExplanation]
    interpretation_caption: str
    diagnostic_message: str | None = None
    current_label: str = "Current"
    baseline_label: str = "Baseline"


def resolve_evidence_path(root: Path, relative_path: str) -> Path | None:
    """Resolve a relative evidence path only if it stays under *root*."""
    root_resolved = root.resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return None
    return candidate


def resolve_evidence_pairs(
    *,
    current_root: Path,
    baseline_root: Path,
    targets: Sequence[EvidenceTarget],
    metric_explanations: Sequence[MetricExplanation] = (),
    current_label: str = "Current",
    baseline_label: str = "Baseline",
    caption_builder: CaptionBuilder | None = None,
    ambiguity_selector: AmbiguitySelector | None = None,
) -> list[EvidencePair]:
    """Resolve a deterministic paired-evidence set from bounded roots."""
    explanations = list(metric_explanations)
    pairs: list[EvidencePair] = []
    for target in targets:
        if target.forced_mismatch_message:
            pairs.append(
                EvidencePair(
                    phase_id=target.phase_id,
                    phase_label=target.phase_label,
                    view_name=target.view_name,
                    current_image_path=None,
                    baseline_image_path=None,
                    status="mismatch",
                    metric_explanations=[],
                    interpretation_caption=target.forced_mismatch_message,
                    diagnostic_message=target.forced_mismatch_message,
                    current_label=current_label,
                    baseline_label=baseline_label,
                )
            )
            continue

        current_path = resolve_evidence_path(current_root, target.current_relative_path)
        baseline_path = resolve_evidence_path(baseline_root, target.baseline_relative_path)
        if current_path is None or baseline_path is None:
            message = (
                "Paired evidence path escaped the allowed roots. "
                f"Current={target.current_relative_path!r}, "
                f"comparison={target.baseline_relative_path!r}."
            )
            pairs.append(
                EvidencePair(
                    phase_id=target.phase_id,
                    phase_label=target.phase_label,
                    view_name=target.view_name,
                    current_image_path=None,
                    baseline_image_path=None,
                    status="mismatch",
                    metric_explanations=[],
                    interpretation_caption=message,
                    diagnostic_message=message,
                    current_label=current_label,
                    baseline_label=baseline_label,
                )
            )
            continue

        current_exists = current_path.exists()
        baseline_exists = baseline_path.exists()
        if current_exists and baseline_exists:
            status: EvidenceStatus = (
                "ambiguous"
                if ambiguity_selector is not None and ambiguity_selector(target)
                else "full"
            )
            diagnostic_message = target.ambiguous_message if status == "ambiguous" else None
            pairs.append(
                EvidencePair(
                    phase_id=target.phase_id,
                    phase_label=target.phase_label,
                    view_name=target.view_name,
                    current_image_path=current_path,
                    baseline_image_path=baseline_path,
                    status=status,
                    metric_explanations=explanations,
                    interpretation_caption=_interpretation_caption(
                        target,
                        status,
                        caption_builder,
                    ),
                    diagnostic_message=diagnostic_message,
                    current_label=current_label,
                    baseline_label=baseline_label,
                )
            )
            continue

        if current_exists or baseline_exists:
            if current_exists:
                message = target.missing_baseline_message or (
                    f"{baseline_label} evidence missing for {target.phase_id}/{target.view_name}."
                )
                current_resolved: Path | None = current_path
                baseline_resolved: Path | None = None
            else:
                message = target.missing_current_message or (
                    f"{current_label} evidence missing for {target.phase_id}/{target.view_name}."
                )
                current_resolved = None
                baseline_resolved = baseline_path
            pairs.append(
                EvidencePair(
                    phase_id=target.phase_id,
                    phase_label=target.phase_label,
                    view_name=target.view_name,
                    current_image_path=current_resolved,
                    baseline_image_path=baseline_resolved,
                    status="partial",
                    metric_explanations=explanations,
                    interpretation_caption=_interpretation_caption(
                        target,
                        "partial",
                        caption_builder,
                    ),
                    diagnostic_message=message,
                    current_label=current_label,
                    baseline_label=baseline_label,
                )
            )
            continue

        message = target.empty_message or (
            f"No paired evidence is currently available for {target.phase_id}/{target.view_name}."
        )
        pairs.append(
            EvidencePair(
                phase_id=target.phase_id,
                phase_label=target.phase_label,
                view_name=target.view_name,
                current_image_path=None,
                baseline_image_path=None,
                status="empty",
                metric_explanations=explanations,
                interpretation_caption=_interpretation_caption(
                    target,
                    "empty",
                    caption_builder,
                ),
                diagnostic_message=message,
                current_label=current_label,
                baseline_label=baseline_label,
            )
        )
    return pairs


def render_zoomable_image(
    image_path: Path,
    *,
    alt: str,
    caption: str,
    class_name: str = "evidence-zoom-button",
) -> str:
    """Render a zoomable inline image button backed by a data URI."""
    image_src = _image_data_uri(image_path)
    return (
        f'<button type="button" class="{html.escape(class_name)}" '
        f'aria-label="Expand {html.escape(caption)}" '
        f'data-lightbox-caption="{html.escape(caption)}">'
        f'<img src="{html.escape(image_src)}" alt="{html.escape(alt)}" loading="lazy"/>'
        "</button>"
    )


def render_lightbox_shell() -> str:
    """Render the reusable DOM + JS needed for evidence lightboxes."""
    return "\n".join(
        [
            '<div class="image-lightbox" data-evidence-lightbox hidden aria-hidden="true">',
            '  <div class="image-lightbox-backdrop" data-lightbox-close></div>',
            '  <div class="image-lightbox-dialog" role="dialog" aria-modal="true"',
            '       aria-labelledby="image-lightbox-title">',
            '    <div class="image-lightbox-toolbar">',
            '      <p class="image-lightbox-kicker" id="image-lightbox-title">'
            "Expanded evidence</p>",
            '      <button type="button" class="image-lightbox-close" '
            "data-lightbox-close>Close</button>",
            "    </div>",
            '    <img class="image-lightbox-image" data-lightbox-image alt="" />',
            '    <p class="image-lightbox-caption" data-lightbox-caption></p>',
            "  </div>",
            "</div>",
            "<script>",
            "(function () {",
            "  if (window.__roboharnessEvidenceLightboxBound) {",
            "    return;",
            "  }",
            "  window.__roboharnessEvidenceLightboxBound = true;",
            '  var lightbox = document.querySelector("[data-evidence-lightbox]");',
            "  if (!lightbox) {",
            "    return;",
            "  }",
            '  var lightboxImage = lightbox.querySelector("[data-lightbox-image]");',
            '  var lightboxCaption = lightbox.querySelector("[data-lightbox-caption]");',
            '  var closeButton = lightbox.querySelector(".image-lightbox-close");',
            "  var lastTrigger = null;",
            "  function closeLightbox() {",
            "    if (lightbox.hidden) {",
            "      return;",
            "    }",
            "    lightbox.hidden = true;",
            '    lightbox.setAttribute("aria-hidden", "true");',
            '    document.body.classList.remove("lightbox-open");',
            '    lightboxImage.removeAttribute("src");',
            '    lightboxImage.setAttribute("alt", "");',
            '    lightboxCaption.textContent = "";',
            "    if (lastTrigger) {",
            "      lastTrigger.focus();",
            "      lastTrigger = null;",
            "    }",
            "  }",
            '  document.addEventListener("click", function (event) {',
            '    var trigger = event.target.closest(".evidence-zoom-button");',
            "    if (trigger) {",
            '      var triggerImage = trigger.querySelector("img");',
            "      if (!triggerImage) {",
            "        return;",
            "      }",
            "      event.preventDefault();",
            "      lastTrigger = trigger;",
            '      lightboxImage.setAttribute("src", triggerImage.getAttribute("src") || "");',
            '      lightboxImage.setAttribute("alt", triggerImage.getAttribute("alt") || "");',
            '      lightboxCaption.textContent = trigger.getAttribute("data-lightbox-caption")',
            '        || triggerImage.getAttribute("alt") || "";',
            "      lightbox.hidden = false;",
            '      lightbox.setAttribute("aria-hidden", "false");',
            '      document.body.classList.add("lightbox-open");',
            "      closeButton.focus();",
            "      return;",
            "    }",
            '    if (!lightbox.hidden && event.target.closest("[data-lightbox-close]")) {',
            "      event.preventDefault();",
            "      closeLightbox();",
            "    }",
            "  });",
            '  document.addEventListener("keydown", function (event) {',
            '    if (event.key === "Escape" && !lightbox.hidden) {',
            "      closeLightbox();",
            "    }",
            "  });",
            "})();",
            "</script>",
        ]
    )


def _interpretation_caption(
    target: EvidenceTarget,
    status: EvidenceStatus,
    caption_builder: CaptionBuilder | None,
) -> str:
    if caption_builder is not None:
        return caption_builder(target, status)
    if status == "ambiguous":
        return (
            f"{target.phase_label} / {target.view_name} is suggestive, "
            "but the available still images are not decisive."
        )
    if status == "partial":
        return (
            f"{target.phase_label} / {target.view_name} remains partially comparable, "
            "but one side of the proof is missing."
        )
    if status == "empty":
        return f"No paired evidence is available for {target.phase_label} / {target.view_name}."
    if status == "mismatch":
        return (
            f"{target.phase_label} / {target.view_name} could not be resolved under the "
            "declared evidence roots."
        )
    return f"{target.phase_label} / {target.view_name} is ready for side-by-side review."


def _image_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"
