#!/usr/bin/env python3
"""Make Bolt's conan recipe usable with enable_gcs=True.

Bolt's conanfile.py adds `google-cloud-cpp` to requirements() when enable_gcs is set, but its
package_info() never lists it in any component's `requires`. Conan then aborts the install with:

  ERROR: bolt/main: package_info(): The direct dependency 'google-cloud-cpp' is not used by any
  '(cpp_info/components).requires'.

enable_s3 already has the equivalent block (aws-sdk-cpp::s3 ...). This inserts the matching block for
GCS, using the `storage` component of conan-center's google-cloud-cpp recipe.

Usage: python3 dev/patch-bolt-recipe.py <path/to/bolt/conanfile.py>
Idempotent; exits non-zero if the anchor it patches around is missing (the recipe changed upstream).
"""
import sys

ANCHOR = (
    '        if self.options.get_safe("enable_tos"):\n'
    '            self.cpp_info.components["bolt_engine"].requires.append(\n'
    '                "tos_client::tos_client"\n'
    "            )\n"
)
BLOCK = (
    '        if self.options.get_safe("enable_gcs"):\n'
    '            self.cpp_info.components["bolt_engine"].requires.append(\n'
    '                "google-cloud-cpp::storage"\n'
    "            )\n"
)


def main(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        src = f.read()
    if BLOCK in src:
        print(f"{path}: already patched")
        return 0
    if src.count(ANCHOR) != 1:
        print(
            f"{path}: expected exactly one 'enable_tos' package_info block to patch around, found "
            f"{src.count(ANCHOR)}; the Bolt recipe changed, update this script",
            file=sys.stderr,
        )
        return 1
    with open(path, "w", encoding="utf-8") as f:
        f.write(src.replace(ANCHOR, BLOCK + ANCHOR, 1))
    print(f"{path}: patched (google-cloud-cpp::storage added to bolt_engine requires)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
