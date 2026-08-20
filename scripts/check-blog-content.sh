#!/bin/sh
set -eu

CONTENT_DIR="frontend/content/blog"
EXPECTED=15
count=0
for file in "$CONTENT_DIR"/*/*.mdx; do
  [ -f "$file" ] || continue
  case "$file" in
    */[a-z0-9-]*/[a-z][a-z].mdx) : ;;
    *) echo "check-blog-content: unexpected path: $file" >&2; exit 1 ;;
  esac
  count=$((count + 1))
  words=$(wc -w < "$file" | tr -d ' ')
  if [ "$words" -lt 400 ] || [ "$words" -gt 800 ]; then
    echo "check-blog-content: word count out of band ($words): $file" >&2; exit 1
  fi
  topic=$(basename "$(dirname "$file")")
  locale=$(basename "$file" .mdx)
  case "$topic:$locale" in
    compress-pdf:en) href="/en/compress-pdf" ;; compress-pdf:es) href="/es/comprimir-pdf" ;; compress-pdf:id) href="/id/kompres-pdf" ;;
    merge-pdf:en) href="/en/merge-pdf" ;; merge-pdf:es) href="/es/combinar-pdf" ;; merge-pdf:id) href="/id/gabungkan-pdf" ;;
    split-pdf:en) href="/en/split-pdf" ;; split-pdf:es) href="/es/dividir-pdf" ;; split-pdf:id) href="/id/pisahkan-pdf" ;;
    jpg-to-pdf:en) href="/en/jpg-to-pdf" ;; jpg-to-pdf:es) href="/es/jpg-a-pdf" ;; jpg-to-pdf:id) href="/id/gambar-ke-pdf" ;;
    pdf-to-jpg:en) href="/en/pdf-to-jpg" ;; pdf-to-jpg:es) href="/es/pdf-a-jpg" ;; pdf-to-jpg:id) href="/id/pdf-ke-gambar" ;;
    *) echo "check-blog-content: unknown topic/locale: $file" >&2; exit 1 ;;
  esac
  if ! grep -qF "$href" "$file"; then echo "check-blog-content: missing tool link ($href): $file" >&2; exit 1; fi
done
if [ "$count" -ne "$EXPECTED" ]; then echo "check-blog-content: expected $EXPECTED article files, found $count" >&2; exit 1; fi
echo "check-blog-content: OK ($count article files, links and length in band)"
