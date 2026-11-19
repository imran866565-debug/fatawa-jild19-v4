# Fatawa Razviya — Jild 19 tashreeh v4 merge

Merge workspace: 16 leaf chunk files of the easy-Urdu tashreeh v4 for Fatawa Razviya Jild 19 (volume_id 45; 261 items, 599 pages) are merged into `jild-19.json` by GitHub Actions (`merge_jild19_v4.py`), then published as a v1.0 release asset.

Item order reproduces the v3 merged file exactly (first jild19-pesh-lafz, last jild19-khatima). All 16 leaf chunks carry start_page == min(pages). The merge renames masala-250 to masala-150 (p.433 print error for 150) and joins 7 simple duplicate-id pairs (masala-24, 48, 91, 113, 140, 153, 172) plus the cross-id masala-228 (head + muna-wal-durar-2), then stable-sorts by start_page, matching the v3 merged file. No page markers are present in the chunks.
