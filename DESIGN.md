---
name: RAG Search Comparison
description: Restrained, readable local search comparison interface.
colors:
  paper: "#f6f7f4"
  surface: "#ffffff"
  ink: "#202c29"
  muted: "#53615b"
  line: "#d5ddd7"
  accent: "#176348"
  soft: "#e8f1eb"
  error: "#9a3029"
typography:
  body:
    fontFamily: "Segoe UI, sans-serif"
    fontSize: "16px"
    lineHeight: 1.55
rounded:
  panel: "12px"
  control: "6px"
spacing:
  small: "8px"
  medium: "16px"
  large: "24px"
---

## Overview

The interface uses quiet green accents, pale surfaces, and explicit labels so questions and retrieved evidence remain the focus. The implementation in `web/style.css` is the source for these documented conventions.

## Colors

Paper is the page background; surface separates the question form and header. Ink carries primary copy and muted carries hints and metadata. Accent identifies actions, links, focus, and method rules. Soft distinguishes the generated answer and method labels. Error is reserved for failures.

## Typography

Use the system sans family throughout. The page heading scales from 28–40px with 1.2 line height and -0.025em tracking. Section headings are 23px, method headings 20px, source titles 16px, and passage text 14px. Metadata uses 12–13px. Ranks and scores use tabular numerals. Underlines stay visible on source links.

## Layout

Content is centered in a 1408px maximum-width shell with 24px horizontal padding. The desktop comparison uses three equal columns with 28px gaps. Controls wrap below 950px; below 700px the methods stack and controls occupy full rows, with 20px page gutters. Long source links, questions, and passages wrap within their columns.

## Elevation & Depth

Separate surfaces with thin borders or background fills. There are no decorative shadows. Results are divided by horizontal rules rather than individual cards.

## Shapes

Question and answer panels use the panel radius; inputs, buttons, and error messages use the control radius. Method labels use a small 5px radius.

## Components

The question form has a visible label, result-count selector, optional hybrid answer checkbox, and one primary submit action. Controls have a minimum 44px height. Suggested questions populate and focus the text field. During requests, the submit button is disabled and status text describes progress.

Results identify rank, shared passage ID, linked source title, method-specific score, excerpt, and a native disclosure for the full passage. Preserve the distinct BM25, cosine similarity, and fusion score labels and the warning that their scales differ. The optional answer preserves text line breaks and includes source links.

Keyboard focus uses a 3px accent outline with a 3px offset. Selection is pale green, the textarea caret uses the accent, and checkbox styling follows the same accent. Errors use an alert region; progress uses a live status region. Empty, loading, success, and unavailable states are explicit text. The interface uses no authored animation.

## Do's and Don'ts

- Keep evidence readable and source links recognizable.
- Preserve method names and shared passage IDs across layouts.
- Keep API configuration on the server; the interface does not display credentials.
- Avoid decorative imagery, gradients, and nested result cards.
