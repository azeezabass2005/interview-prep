# DOC-815: Preview shows an old version after editing

**Type:** Bug · **Priority:** Medium · **Reporter:** Deals team

## Description
After editing a term sheet, the preview pane still shows the old text, and the old version number, for up to 10 minutes. A
banker sent a client a screenshot of the preview with last night's numbers. Reloading the page doesn't help; waiting does.

## Acceptance criteria
- The preview always reflects the document's current version.
- Previews are still cached (rendering is expensive): viewing the same version twice renders once.
