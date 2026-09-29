# Documentation maintenance

The generated Markdown is committed as readable content. `write-guide.py` regenerates the 36 unified chapters and root READMEs using retained native chapters under `docs/native/docs/` and desktop `docs/media/manifest.json`. It does not need raw capture frames.

`build-docs.mjs` renders Markdown with marked. Set `MARKED_MODULE` to an installed marked module file, or install marked in your documentation environment. It writes the three unified HTML readers, landing page, CSS/JS and media provenance HTML. It does not deploy a website.

`validate-docs.py` uses Python's standard library to check local links, anchors, counts, routes and media hashes. It does not start a browser. Browser visual/interaction checks are explicitly pending.

`capture-desktop.py` requires the complete desktop v12 source and its dependencies. Set `DESKTOP_SOURCE` to the source directory and `CAPTURE_OUT` to a writable frame directory. It uses a temporary save profile. `build-media.py CAPTURE_DIRECTORY OUTPUT_DIRECTORY` requires Pillow and software FFmpeg (set `FFMPEG`). It assembles H.264 videos, fully decodes them, then makes animated GIFs. Retained native recordings were made using the separate native project's documentation capture test.

Do not run game capture against a modified build and retain old verification claims. Update provenance, all three languages and validation evidence together. Raw frames are authoring assets and are excluded from delivery ZIPs.
