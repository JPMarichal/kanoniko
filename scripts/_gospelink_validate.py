#!/usr/bin/env python
"""Post-fetch content validation for a Gospelink slug.

Exits 1 if any file contains WAF/captcha leaks or is missing the standard
footer. Used by `just gospelink_finalize`.
"""
import os
import re
import sys

if len(sys.argv) != 2:
    print("Usage: _gospelink_validate.py <slug>", file=sys.stderr)
    sys.exit(2)

slug = sys.argv[1]
out_dir = os.path.join("corpus", "en", "books", "gospelink", slug)
if not os.path.isdir(out_dir):
    print(f"No corpus dir: {out_dir}", file=sys.stderr)
    sys.exit(2)

files = sorted(f for f in os.listdir(out_dir) if f.endswith(".txt"))
LEAK = re.compile(
    r"verify you are human|human verification|awsWafCookie|"
    r"let'?s confirm|confirme que es humano|elija todo|"
    r"challenge\.js|captcha",
    re.IGNORECASE,
)
FOOTER = re.compile(r"Printed from Gospelink\.com\s*$")

leaks = 0
no_footer = 0
sizes = []
for fn in files:
    p = os.path.join(out_dir, fn)
    with open(p, encoding="utf-8") as f:
        text = f.read()
    sizes.append(len(text))
    if LEAK.search(text):
        leaks += 1
    if not FOOTER.search(text):
        no_footer += 1

sizes.sort()
median = sizes[len(sizes) // 2] if sizes else 0
print(f"Validation: {len(files)} files | leaks={leaks} | "
      f"no-footer={no_footer} | min={sizes[0] if sizes else 0} "
      f"median={median} max={sizes[-1] if sizes else 0}")

sys.exit(1 if (leaks or no_footer) else 0)
