#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 19 easy-Urdu tashreeh v4 chunks into jild-19.json.

Reads the 16 leaf chunk files listed in chunks-manifest-v4-jild19.json,
concatenates them in order 01 -> 02 -> 03 -> 04-a -> 04-b -> 05 -> 06-a
-> 06-b -> 07 -> 08-a -> 08-b -> 09-a -> 09-b -> 10 -> 11 -> 12, JOINS
the 7 simple duplicate-id pairs (masala-24, 48, 91, 113, 140, 153,
172) and the cross-id pair (masala-228 + muna-wal-durar-2) into single
items, applies the merge-time rename masala-250 -> masala-150, STABLE
SORTS by start_page (mirroring the v3 merge), derives start_page =
min(pages) where the field is absent, normalises page markers,
validates, and writes {"masail": [...]} to jild-19.json.

ORDER -- chunk order is the order, then a stable sort by start_page:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-19.json
  has ID order == stable sort by start_page of the concatenation
  (verified locally by the coordinator: the v3 order IS the stable
  sort, including its 36 tied start_pages). Do NOT sort or reorder
  before the joins. Within each chunk, items keep file order.
  CHUNK_ORDER is an explicit 16-leaf list because 04a/04b, 06a/06b,
  08a/08b and 09a/09b break the numeric range pattern. Chunk 07's
  file order is wrong in v3 itself (masala-147-149 first, belongs
  between 146 and 250 by start_page 422) — the sort fixes it, exactly
  as the v3 merge does.

JOINS: parts are found BY ID anywhere in the list (masala-140's halves
  are NOT consecutive — chunk 07's misplaced masala-147-149 sits
  between them). Parts must be in ascending page order. Sawal modes:
  "first" (48, 91, 140, 172 — the single non-empty sawal, in the first
  part), "concat" (24, 113 — both sawals non-empty, concatenated with
  a single space), "second" (153 — chunk 08-a's fuller restatement is
  kept, chunk 07's partial sawal is DISCARDED). Titles: the joined
  title is the FIRST part's title, asserted against the embedded
  merged-v3 title (V3_TITLES) — EXCEPT masala-91, where both parts'
  titles end " (حصہ اول)" and the suffix is stripped at merge (the
  merged-v3 title has no suffix). title_must_match is deliberately NOT
  used: the two halves' titles differ by design in the v3 chunks.
  masala-24 [138, 139-141], masala-48 [185-192, 193], masala-91
  [292, 293], masala-113 [342, 343], masala-140 [391-392, 393],
  masala-153 [440, 441-444], masala-172 [489-490, 491-492].
CROSS-ID JOIN (1):
  masala-228: c10 head jild19-masala-228 [563-590] (sawal) + c11
    jild19-muna-wal-durar-2 [591-607] (sawal empty) -> ONE item;
    sawal = head only; title from the head. Net -1 item.
  After the joins there are 261 items and 261 unique ids — the
  duplicate-id assertion runs AFTER the joins, not before.
  MERGE-TIME RENAME: jild19-masala-250 -> jild19-masala-150 (p.433
  print error for ۱۵۰; id only — the title already matches the
  merged-v3 title verbatim). The three rasail are SEQUENCES of
  separately numbered masail, NOT one mas'ala each — no mega-combines.
  NO folds. All chunks carry start_page == min(pages) (0 derived).
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild19.json"

# Concatenation order: chunk files 01 -> 18, in order.
CHUNK_ORDER = ["jild-19-chunk-01.json", "jild-19-chunk-02.json", "jild-19-chunk-03.json", "jild-19-chunk-04-a.json", "jild-19-chunk-04-b.json", "jild-19-chunk-05.json", "jild-19-chunk-06-a.json", "jild-19-chunk-06-b.json", "jild-19-chunk-07.json", "jild-19-chunk-08-a.json", "jild-19-chunk-08-b.json", "jild-19-chunk-09-a.json", "jild-19-chunk-09-b.json", "jild-19-chunk-10.json", "jild-19-chunk-11.json", "jild-19-chunk-12.json"]

EXPECTED_ITEMS = 261
EXPECTED_PAGES = 599
EXPECTED_MIN_PAGE = 5
EXPECTED_MAX_PAGE = 692
EXPECTED_VOLUME_IDS = {45}
EXPECTED_FIRST_ID = "jild19-pesh-lafz"
EXPECTED_LAST_ID = "jild19-khatima"

# v3 ID sequence, verbatim from content/tashreeh/jild-19.json.
V3_IDS = ["jild19-pesh-lafz", "jild19-masala-1", "jild19-masala-2", "jild19-masala-3", "jild19-masala-4", "jild19-masala-5", "jild19-masala-6", "jild19-masala-7", "jild19-masala-8", "jild19-masala-9-10", "jild19-masala-11", "jild19-masala-12", "jild19-masala-13", "jild19-masala-14", "jild19-masala-15", "jild19-masala-16", "jild19-masala-17", "jild19-masala-18", "jild19-masala-19", "jild19-masala-20", "jild19-masala-21-alif", "jild19-masala-21-be", "jild19-masala-22", "jild19-masala-23", "jild19-masala-24", "jild19-masala-25", "jild19-masala-26", "jild19-masala-27", "jild19-masala-28", "jild19-masala-29", "jild19-masala-30", "jild19-masala-31", "jild19-masala-32", "jild19-masala-33", "jild19-masala-34", "jild19-masala-35", "jild19-masala-36", "jild19-masala-37", "jild19-masala-38", "jild19-masala-39", "jild19-masala-40", "jild19-masala-41", "jild19-masala-42", "jild19-masala-43", "jild19-masala-44", "jild19-masala-45", "jild19-masala-46", "jild19-masala-47", "jild19-masala-48", "jild19-masala-49", "jild19-masala-50", "jild19-masala-51", "jild19-masala-52", "jild19-masala-53", "jild19-masala-54", "jild19-masala-55", "jild19-masala-56", "jild19-masala-57", "jild19-p212", "jild19-masala-59", "jild19-masala-60", "jild19-masala-61", "jild19-masala-62", "jild19-masala-63", "jild19-masala-64", "jild19-masala-65", "jild19-masala-66", "jild19-masala-67", "jild19-masala-68", "jild19-masala-69", "jild19-masala-70", "jild19-masala-71", "jild19-masala-72", "jild19-masala-73", "jild19-masala-74", "jild19-masala-75", "jild19-masala-76", "jild19-masala-77", "jild19-masala-78", "jild19-masala-79", "jild19-masala-80", "jild19-masala-81", "jild19-masala-82", "jild19-masala-83", "jild19-masala-84", "jild19-masala-85", "jild19-masala-86", "jild19-masala-87", "jild19-masala-88", "jild19-masala-89", "jild19-masala-90", "jild19-masala-91", "jild19-masala-92", "jild19-masala-93", "jild19-masala-94", "jild19-masala-95", "jild19-masala-96", "jild19-masala-97", "jild19-masala-98-102", "jild19-masala-103", "jild19-masala-104", "jild19-masala-105", "jild19-masala-106", "jild19-masala-107-112", "jild19-masala-113", "jild19-masala-114", "jild19-masala-115", "jild19-masala-116", "jild19-masala-117", "jild19-masala-118", "jild19-masala-119", "jild19-masala-120", "jild19-masala-122", "jild19-masala-123", "jild19-masala-124", "jild19-masala-125", "jild19-masala-126", "jild19-masala-127", "jild19-masala-128", "jild19-masala-129", "jild19-masala-130", "jild19-masala-131", "jild19-masala-132", "jild19-masala-133", "jild19-masala-134", "jild19-masala-135", "jild19-masala-136", "jild19-masala-137", "jild19-masala-138", "jild19-masala-139", "jild19-masala-140", "jild19-masala-141", "jild19-masala-142", "jild19-masala-143", "jild19-masala-144", "jild19-masala-145", "jild19-masala-146", "jild19-masala-147-149", "jild19-masala-150", "jild19-masala-151", "jild19-masala-152", "jild19-masala-153", "jild19-masala-154", "jild19-masala-155", "jild19-masala-156", "jild19-masala-157", "jild19-masala-158", "jild19-masala-159", "jild19-masala-160", "jild19-masala-161", "jild19-masala-162", "jild19-masala-163", "jild19-masala-164", "jild19-masala-165", "jild19-masala-166", "jild19-masala-167", "jild19-masala-168", "jild19-masala-169", "jild19-masala-170", "jild19-masala-171", "jild19-masala-172", "jild19-masala-173", "jild19-masala-174", "jild19-masala-175", "jild19-masala-176-178", "jild19-masala-179", "jild19-masala-180", "jild19-masala-181", "jild19-masala-182", "jild19-masala-193", "jild19-masala-184", "jild19-masala-185", "jild19-masala-186", "jild19-masala-187", "jild19-masala-188-189", "jild19-masala-190", "jild19-masala-191", "jild19-masala-192", "jild19-p504", "jild19-masala-194", "jild19-masala-195", "jild19-masala-196", "jild19-masala-197", "jild19-masala-198", "jild19-masala-199", "jild19-masala-200", "jild19-masala-201-203", "jild19-masala-204-206", "jild19-masala-207", "jild19-masala-208", "jild19-masala-209", "jild19-masala-210", "jild19-masala-211", "jild19-masala-212", "jild19-masala-213", "jild19-masala-214", "jild19-masala-215", "jild19-masala-216", "jild19-masala-217", "jild19-masala-218", "jild19-masala-219", "jild19-masala-220", "jild19-p541", "jild19-masala-221", "jild19-masala-222", "jild19-masala-223", "jild19-masala-224-225", "jild19-masala-226", "jild19-masala-227", "jild19-masala-228", "jild19-masala-229-231", "jild19-masala-232", "jild19-masala-233", "jild19-masala-234", "jild19-masala-235", "jild19-masala-236", "jild19-masala-237", "jild19-masala-238", "jild19-masala-239", "jild19-masala-240", "jild19-masala-241", "jild19-masala-242", "jild19-masala-243", "jild19-masala-244-251", "jild19-masala-252", "jild19-masala-253", "jild19-masala-254", "jild19-masala-255", "jild19-masala-256", "jild19-masala-257", "jild19-masala-258", "jild19-masala-259", "jild19-masala-260", "jild19-masala-261", "jild19-masala-262", "jild19-masala-263", "jild19-masala-264", "jild19-masala-265", "jild19-masala-266", "jild19-masala-267", "jild19-masala-268", "jild19-masala-269", "jild19-masala-270", "jild19-masala-271", "jild19-masala-272", "jild19-masala-273", "jild19-masala-274", "jild19-masala-275", "jild19-masala-276", "jild19-masala-277", "jild19-masala-278", "jild19-masala-279", "jild19-masala-280", "jild19-masala-281-283", "jild19-masala-284", "jild19-masala-285-286", "jild19-masala-287", "jild19-masala-288-292", "jild19-masala-293", "jild19-masala-294", "jild19-khatima"]

# v3 pages per item id, verbatim from content/tashreeh/jild-19.json.
V3_PAGES = {
    "jild19-pesh-lafz": [5, 6, 7],
    "jild19-masala-1": [93, 94],
    "jild19-masala-2": [94, 95],
    "jild19-masala-3": [95, 96],
    "jild19-masala-4": [97],
    "jild19-masala-5": [98, 99, 100, 101, 102, 103, 104, 105, 106],
    "jild19-masala-6": [106, 107],
    "jild19-masala-7": [107, 108, 109],
    "jild19-masala-8": [110, 111],
    "jild19-masala-9-10": [112, 113],
    "jild19-masala-11": [113, 114, 115],
    "jild19-masala-12": [116],
    "jild19-masala-13": [116, 117],
    "jild19-masala-14": [117, 118],
    "jild19-masala-15": [119, 120, 121, 122, 123],
    "jild19-masala-16": [123, 124],
    "jild19-masala-17": [124, 125, 126, 127, 128],
    "jild19-masala-18": [128],
    "jild19-masala-19": [129],
    "jild19-masala-20": [129, 130],
    "jild19-masala-21-alif": [131, 132, 133],
    "jild19-masala-21-be": [133],
    "jild19-masala-22": [133, 134],
    "jild19-masala-23": [134, 135, 136, 137, 138],
    "jild19-masala-24": [138, 139, 140, 141],
    "jild19-masala-25": [141, 142],
    "jild19-masala-26": [142, 143, 144, 145, 146, 147, 148, 149, 150, 151],
    "jild19-masala-27": [151],
    "jild19-masala-28": [153, 154],
    "jild19-masala-29": [154, 155],
    "jild19-masala-30": [155],
    "jild19-masala-31": [155, 156],
    "jild19-masala-32": [156, 157, 158, 159],
    "jild19-masala-33": [159],
    "jild19-masala-34": [159, 160, 161, 162],
    "jild19-masala-35": [162, 163, 164],
    "jild19-masala-36": [164],
    "jild19-masala-37": [164, 165],
    "jild19-masala-38": [165, 166],
    "jild19-masala-39": [166],
    "jild19-masala-40": [166, 167],
    "jild19-masala-41": [167, 168, 169, 170],
    "jild19-masala-42": [171],
    "jild19-masala-43": [171],
    "jild19-masala-44": [173, 174],
    "jild19-masala-45": [174, 175, 176, 177, 178],
    "jild19-masala-46": [179, 180],
    "jild19-masala-47": [180, 181, 182, 183, 184],
    "jild19-masala-48": [185, 186, 187, 188, 189, 190, 191, 192, 193],
    "jild19-masala-49": [193, 194, 195, 196, 197],
    "jild19-masala-50": [197, 198],
    "jild19-masala-51": [198, 199],
    "jild19-masala-52": [200, 201, 202, 203, 204, 205],
    "jild19-masala-53": [205, 206],
    "jild19-masala-54": [206, 207],
    "jild19-masala-55": [207, 208, 209],
    "jild19-masala-56": [209, 210],
    "jild19-masala-57": [210, 211, 212],
    "jild19-p212": [212, 213, 214],
    "jild19-masala-59": [214, 215, 216, 217],
    "jild19-masala-60": [217, 218],
    "jild19-masala-61": [218, 219, 220],
    "jild19-masala-62": [220],
    "jild19-masala-63": [220, 221],
    "jild19-masala-64": [221, 222],
    "jild19-masala-65": [222],
    "jild19-masala-66": [222, 223],
    "jild19-masala-67": [223, 224, 225, 226, 227],
    "jild19-masala-68": [227, 228],
    "jild19-masala-69": [229, 230],
    "jild19-masala-70": [230, 231],
    "jild19-masala-71": [231, 232],
    "jild19-masala-72": [232, 233, 234, 235, 236],
    "jild19-masala-73": [236, 237, 238, 239],
    "jild19-masala-74": [239, 240, 241, 242],
    "jild19-masala-75": [243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256],
    "jild19-masala-76": [256, 257, 258, 259, 260, 261],
    "jild19-masala-77": [261, 262],
    "jild19-masala-78": [262, 263],
    "jild19-masala-79": [264, 265, 266, 267, 268, 269, 270, 271],
    "jild19-masala-80": [271, 272, 273],
    "jild19-masala-81": [273, 274, 275, 276, 277, 278],
    "jild19-masala-82": [278, 279],
    "jild19-masala-83": [279],
    "jild19-masala-84": [279, 280, 281],
    "jild19-masala-85": [281],
    "jild19-masala-86": [281, 282, 283, 284, 285],
    "jild19-masala-87": [285, 286],
    "jild19-masala-88": [286, 287, 288, 289, 290],
    "jild19-masala-89": [290, 291],
    "jild19-masala-90": [291, 292],
    "jild19-masala-91": [292, 293],
    "jild19-masala-92": [293, 294],
    "jild19-masala-93": [294, 295, 296, 297, 298, 299],
    "jild19-masala-94": [299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325],
    "jild19-masala-95": [325, 326, 327],
    "jild19-masala-96": [327, 328],
    "jild19-masala-97": [328, 329, 330],
    "jild19-masala-98-102": [330, 331, 332],
    "jild19-masala-103": [332, 333],
    "jild19-masala-104": [333, 334, 335],
    "jild19-masala-105": [335, 336],
    "jild19-masala-106": [336],
    "jild19-masala-107-112": [336, 337, 338, 339, 340, 341, 342],
    "jild19-masala-113": [342, 343],
    "jild19-masala-114": [344, 345, 346],
    "jild19-masala-115": [346, 347],
    "jild19-masala-116": [347],
    "jild19-masala-117": [347, 348],
    "jild19-masala-118": [348],
    "jild19-masala-119": [348, 349],
    "jild19-masala-120": [350, 351],
    "jild19-masala-122": [351, 352],
    "jild19-masala-123": [352],
    "jild19-masala-124": [352, 353],
    "jild19-masala-125": [353, 354],
    "jild19-masala-126": [354, 355, 356],
    "jild19-masala-127": [356, 357],
    "jild19-masala-128": [357, 358],
    "jild19-masala-129": [358, 359],
    "jild19-masala-130": [359, 360, 361, 362],
    "jild19-masala-131": [362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383],
    "jild19-masala-132": [383, 384],
    "jild19-masala-133": [384, 385, 386],
    "jild19-masala-134": [386, 387, 388],
    "jild19-masala-135": [388, 389],
    "jild19-masala-136": [389],
    "jild19-masala-137": [389, 390],
    "jild19-masala-138": [390],
    "jild19-masala-139": [390, 391],
    "jild19-masala-140": [391, 392, 393],
    "jild19-masala-141": [393, 394],
    "jild19-masala-142": [394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404],
    "jild19-masala-143": [405, 406],
    "jild19-masala-144": [406, 407],
    "jild19-masala-145": [407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420],
    "jild19-masala-146": [420, 421, 422],
    "jild19-masala-147-149": [422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433],
    "jild19-masala-150": [433, 434, 435, 436, 437],
    "jild19-masala-151": [437, 438, 439],
    "jild19-masala-152": [439, 440],
    "jild19-masala-153": [440, 441, 442, 443, 444],
    "jild19-masala-154": [445],
    "jild19-masala-155": [445, 446],
    "jild19-masala-156": [446],
    "jild19-masala-157": [446, 447, 448, 449, 450, 451, 452],
    "jild19-masala-158": [452, 453, 454],
    "jild19-masala-159": [454, 455],
    "jild19-masala-160": [455, 456, 457, 458, 459, 460, 461, 462],
    "jild19-masala-161": [463, 464, 465, 466, 467, 468],
    "jild19-masala-162": [468, 469, 470, 471, 472],
    "jild19-masala-163": [472, 473],
    "jild19-masala-164": [473, 474, 475],
    "jild19-masala-165": [475],
    "jild19-masala-166": [475, 476, 477],
    "jild19-masala-167": [477, 478],
    "jild19-masala-168": [478, 479, 480],
    "jild19-masala-169": [480, 481, 482, 483, 484, 485, 486],
    "jild19-masala-170": [486, 487, 488],
    "jild19-masala-171": [488, 489],
    "jild19-masala-172": [489, 490, 491, 492],
    "jild19-masala-173": [492, 493],
    "jild19-masala-174": [493, 494],
    "jild19-masala-175": [494, 495, 496],
    "jild19-masala-176-178": [496, 497],
    "jild19-masala-179": [498],
    "jild19-masala-180": [498, 499],
    "jild19-masala-181": [499],
    "jild19-masala-182": [499, 500, 501],
    "jild19-masala-193": [501],
    "jild19-masala-184": [502],
    "jild19-masala-185": [502],
    "jild19-masala-186": [502, 503],
    "jild19-masala-187": [503],
    "jild19-masala-188-189": [503],
    "jild19-masala-190": [503, 504],
    "jild19-masala-191": [504],
    "jild19-masala-192": [504],
    "jild19-p504": [504],
    "jild19-masala-194": [505],
    "jild19-masala-195": [505],
    "jild19-masala-196": [505, 506, 507, 508, 509, 510],
    "jild19-masala-197": [510, 511, 512, 513, 514, 515],
    "jild19-masala-198": [515, 516],
    "jild19-masala-199": [516, 517],
    "jild19-masala-200": [518, 519],
    "jild19-masala-201-203": [519, 520, 521],
    "jild19-masala-204-206": [521],
    "jild19-masala-207": [521],
    "jild19-masala-208": [521, 522],
    "jild19-masala-209": [522, 523],
    "jild19-masala-210": [523, 524, 525, 526, 527],
    "jild19-masala-211": [527],
    "jild19-masala-212": [528, 529],
    "jild19-masala-213": [529, 530],
    "jild19-masala-214": [530],
    "jild19-masala-215": [530, 531, 532, 533],
    "jild19-masala-216": [533, 534, 535, 536, 537],
    "jild19-masala-217": [537, 538],
    "jild19-masala-218": [538],
    "jild19-masala-219": [538, 539],
    "jild19-masala-220": [539, 540],
    "jild19-p541": [541, 542, 543, 544, 545, 546, 547, 548, 549, 550],
    "jild19-masala-221": [550, 551, 552, 553],
    "jild19-masala-222": [553],
    "jild19-masala-223": [554, 555, 556, 557, 558],
    "jild19-masala-224-225": [558, 559],
    "jild19-masala-226": [559, 560],
    "jild19-masala-227": [560, 561, 562],
    "jild19-masala-228": [563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607],
    "jild19-masala-229-231": [608, 609, 611, 612, 613, 614],
    "jild19-masala-232": [615, 616, 617, 618],
    "jild19-masala-233": [618, 619],
    "jild19-masala-234": [619, 620, 621],
    "jild19-masala-235": [621, 622],
    "jild19-masala-236": [622, 623],
    "jild19-masala-237": [623, 624, 625, 626],
    "jild19-masala-238": [626, 627],
    "jild19-masala-239": [627, 628, 629],
    "jild19-masala-240": [629, 630, 631],
    "jild19-masala-241": [631, 632],
    "jild19-masala-242": [632, 633],
    "jild19-masala-243": [634],
    "jild19-masala-244-251": [634, 635],
    "jild19-masala-252": [635, 636, 637, 638],
    "jild19-masala-253": [638, 639, 640],
    "jild19-masala-254": [640, 641],
    "jild19-masala-255": [642, 643, 645],
    "jild19-masala-256": [645, 646, 647, 648, 649, 650],
    "jild19-masala-257": [650, 651],
    "jild19-masala-258": [651, 652],
    "jild19-masala-259": [653, 654],
    "jild19-masala-260": [654, 655, 656],
    "jild19-masala-261": [656, 657, 658, 659, 660, 661],
    "jild19-masala-262": [661, 662],
    "jild19-masala-263": [662, 663],
    "jild19-masala-264": [663, 664, 665],
    "jild19-masala-265": [665, 666],
    "jild19-masala-266": [666, 667],
    "jild19-masala-267": [667, 668, 669],
    "jild19-masala-268": [669, 670, 671],
    "jild19-masala-269": [671, 672, 673, 674],
    "jild19-masala-270": [674, 675, 676],
    "jild19-masala-271": [676, 677],
    "jild19-masala-272": [677, 678],
    "jild19-masala-273": [678, 679, 680],
    "jild19-masala-274": [680, 681, 682],
    "jild19-masala-275": [682],
    "jild19-masala-276": [682, 683],
    "jild19-masala-277": [683, 684],
    "jild19-masala-278": [684, 685],
    "jild19-masala-279": [685, 686, 687],
    "jild19-masala-280": [687],
    "jild19-masala-281-283": [687, 688],
    "jild19-masala-284": [688, 689],
    "jild19-masala-285-286": [688, 689],
    "jild19-masala-287": [689],
    "jild19-masala-288-292": [689, 690, 691],
    "jild19-masala-293": [691],
    "jild19-masala-294": [691, 692],
    "jild19-khatima": [692],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 16, f"expected 16 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

        # SIMPLE JOINS (7): parts found BY ID anywhere (masala-140's
    # halves are NOT consecutive — chunk 07's misplaced masala-147-149
    # sits between them). Sawal modes: first / concat / second.
    # CROSS-ID JOIN (1): masala-228 + muna-wal-durar-2, sawal = head.

    def join_consecutive(item_id, expected_parts, seam_checks, sawal_mode="first", title_suffix=None):
        idxs = [i for i, it in enumerate(all_items) if it["id"] == item_id]
        assert len(idxs) == expected_parts, (
            f"{item_id}: expected {expected_parts} parts, found {len(idxs)}"
        )
        parts = [all_items[i] for i in idxs]
        assert [min(p["pages"]) for p in parts] == sorted(min(p["pages"]) for p in parts), (
            f"{item_id}: parts not in page order"
        )
        vols = {p.get("volume_id") for p in parts}
        assert vols == EXPECTED_VOLUME_IDS, f"{item_id}: volume mismatch {vols}"
        for part_no, which, needle in seam_checks:
            txt = parts[part_no].get("tashreeh_jawab") or ""
            if which == "end":
                assert txt.rstrip().endswith(needle), (
                    f"{item_id} part {part_no + 1} end seam mismatch: ...{txt.rstrip()[-60:]!r}"
                )
            else:
                assert txt.lstrip().startswith(needle), (
                    f"{item_id} part {part_no + 1} start seam mismatch: {txt.lstrip()[:60]!r}"
                )
        if sawal_mode == "first":
            sawals = [p.get("tashreeh_sawal") for p in parts if p.get("tashreeh_sawal")]
            assert len(sawals) <= 1, f"{item_id}: {len(sawals)} non-empty sawals"
            if sawals:
                assert parts[0].get("tashreeh_sawal"), f"{item_id}: non-empty sawal not in first part"
            sawal = sawals[0] if sawals else ""
        elif sawal_mode == "concat":
            assert all(p.get("tashreeh_sawal") for p in parts), f"{item_id}: concat needs both sawals"
            sawal = " ".join(p["tashreeh_sawal"].strip() for p in parts)
        elif sawal_mode == "second":
            assert parts[0].get("tashreeh_sawal") and parts[1].get("tashreeh_sawal"), (
                f"{item_id}: second mode needs both sawals"
            )
            sawal = parts[1]["tashreeh_sawal"]
        else:
            raise AssertionError(f"{item_id}: unknown sawal_mode {sawal_mode}")
        title = parts[0]["title"]
        if title_suffix:
            assert title.endswith(title_suffix), f"{item_id}: first-part title lacks suffix {title_suffix!r}"
            assert all(p["title"].endswith(title_suffix) for p in parts), f"{item_id}: a part title lacks the suffix"
            title = title[: -len(title_suffix)]
        assert title == V3_TITLES[item_id], f"{item_id}: joined title != v3 title"
        pages = sorted({p for part in parts for p in part["pages"]})
        assert pages == V3_PAGES[item_id], f"{item_id}: joined pages != v3"
        joined = {
            "id": item_id,
            "title": title,
            "volume_id": parts[0]["volume_id"],
            "pages": pages,
            "start_page": min(pages),
            "tashreeh_sawal": sawal,
            "tashreeh_jawab": " ".join(p["tashreeh_jawab"].strip() for p in parts if p.get("tashreeh_jawab")),
            "notes": [n for p in parts for n in p.get("notes", [])],
        }
        first = idxs[0]
        for i in reversed(idxs[1:]):
            del all_items[i]
        all_items[first] = joined
        print(f"joined {item_id}: {expected_parts} parts -> 1 item, {len(pages)} pages")

    def join_cross_id(head_id, tail_ids, sawal_mode, seam_checks):
        seq = [head_id] + tail_ids
        idxs = [i for i, it in enumerate(all_items) if it["id"] in seq]
        assert [all_items[i]["id"] for i in idxs] == seq, (
            f"{head_id}: cross-id order mismatch"
        )
        parts = [all_items[i] for i in idxs]
        vols = {p.get("volume_id") for p in parts}
        assert vols == EXPECTED_VOLUME_IDS, f"{head_id}: volume mismatch {vols}"
        if sawal_mode == "head_only":
            assert parts[0].get("tashreeh_sawal"), f"{head_id}: head sawal empty"
            assert all(not p.get("tashreeh_sawal") for p in parts[1:]), (
                f"{head_id}: a tail sawal is non-empty"
            )
            sawal = parts[0]["tashreeh_sawal"]
        else:
            raise AssertionError(f"{head_id}: unknown sawal_mode {sawal_mode}")
        for part_no, which, needle in seam_checks:
            txt = parts[part_no].get("tashreeh_jawab") or ""
            if which == "end":
                assert txt.rstrip().endswith(needle), (
                    f"{head_id} part {part_no + 1} end seam mismatch: ...{txt.rstrip()[-60:]!r}"
                )
            else:
                assert txt.lstrip().startswith(needle), (
                    f"{head_id} part {part_no + 1} start seam mismatch: {txt.lstrip()[:60]!r}"
                )
        pages = sorted({p for part in parts for p in part["pages"]})
        assert pages == V3_PAGES[head_id], f"{head_id}: joined pages != v3"
        title = parts[0]["title"]
        assert title == V3_TITLES[head_id], f"{head_id}: joined title != v3 title"
        joined = {
            "id": head_id,
            "title": title,
            "volume_id": parts[0]["volume_id"],
            "pages": pages,
            "start_page": min(pages),
            "tashreeh_sawal": sawal,
            "tashreeh_jawab": " ".join(p["tashreeh_jawab"].strip() for p in parts if p.get("tashreeh_jawab")),
            "notes": [n for p in parts for n in p.get("notes", [])],
        }
        first = idxs[0]
        for i in reversed(idxs[1:]):
            del all_items[i]
        all_items[first] = joined
        print(f"joined {head_id}: {1 + len(tail_ids)} parts -> 1 item, {len(pages)} pages")

    V3_TITLES = {
        "jild19-masala-24": "مسئلہ ۲۴: مضاربت کے جواب کی بعض عبارات کی تشریح (پہلا حصہ)",
        "jild19-masala-48": "مسئلہ ۴۸: رشیدہ کے نام جائداد و آمدنی کا تملیك نامہ — ہبہ ہے یا وصیت؟",
        "jild19-masala-91": "مسئلہ ۹۱: نکاح نامہ میں لکھا کہ آدھا مال پہلی بیوی کا — اولاد محروم ہوگی؟",
        "jild19-masala-113": "بیوی کے نام خریدا ہوا مکان — سوال کا پہلا حصہ",
        "jild19-masala-140": "مسئلہ ۱۴۰: یتیم پوتوں کو مشترکہ ہبہ اور فتویٰ کس کے قول پر ہے؟",
        "jild19-masala-153": "مسئلہ ۱۵۳: مکان و زمین کرایہ پر دینا — پادری، پنڈت وغیرہ کو (سوال کا پہلا حصہ، صفحہ ۴۴۰)",
        "jild19-masala-172": "مسئلہ ۱۷۲: دکان کا کرایہ — مدت طے نہ ہو تو کتنا کرایہ واجب؟",
        "jild19-masala-228": "مسئلہ ۲۲۸: منی آرڈر — فیس اجرت ہے یا سود؟",
        "jild19-masala-150": "مسئلہ ۲۵۰ (مطبوعہ نمبر): سنی واعظ کی خدمت و نذر — حلال ہے یا نہیں؟",
    }

    join_consecutive(
        "jild19-masala-24", 2,
        [
            (1, "start", "جواب میں اعلیٰ حضرت رحمۃ اللہ علیہ پانچ باتیں فرماتے ہیں۔ مضاربت اس عقد کو کہتے "),
        ],
        sawal_mode="concat",
        title_suffix=None,
    )
    join_consecutive(
        "jild19-masala-48", 2,
        [
            (0, "end", "سے کون مانع ہو سکتا ہے، کیونکہ دوسرے کی نسبت انسان کو اپنی ذات پر قدرت زیادہ ہے۔"),
            (1, "start", "یہ مسئلہ ۴۸ کے جواب کا آخری حصہ ہے۔ اس میں اعلیٰ حضرت رحمۃ اللہ علیہ اس نتیجے پر"),
        ],
        sawal_mode="first",
        title_suffix=None,
    )
    join_consecutive(
        "jild19-masala-91", 2,
        [
            (0, "end", "عدم الاضافۃ الی بعد الموت مع کونہ فی الصحۃ»۔ جواب کا بقیہ حصہ اگلے chunk میں ہے۔"),
            (1, "start", "جواب کا بقیہ حصہ جو اگلے صفحے پر ہے، اس میں اعلیٰ حضرت رحمۃ اللہ علیہ فرماتے ہیں"),
        ],
        sawal_mode="first",
        title_suffix=" (حصہ اول)",
    )
    join_consecutive(
        "jild19-masala-113", 2,
        [
            (1, "start", "جواب میں اعلیٰ حضرت رحمۃ اللہ علیہ دو صورتیں الگ الگ بیان فرماتے ہیں۔ پہلی صورت "),
        ],
        sawal_mode="concat",
        title_suffix=None,
    )
    join_consecutive(
        "jild19-masala-140", 2,
        [
            (0, "end", " ہو، پہلی دو صورتوں میں صاحبین کا خلاف ہے — اور جواب کا بقیہ حصہ صفحہ ۳۹۳ پر ہے۔"),
            (1, "start", "یہ مسئلہ ۱۴۰ کے جواب کا آخری حصہ ہے جس میں اعلیٰ حضرت رحمۃ اللہ علیہ اس بات کی و"),
        ],
        sawal_mode="first",
        title_suffix=None,
    )
    join_consecutive(
        "jild19-masala-153", 2,
        [
            (1, "start", "جواب میں اعلیٰ حضرت رحمۃ اللہ علیہ فرماتے ہیں کہ یہاں دو الگ باتیں ہیں، پہلی یہ "),
        ],
        sawal_mode="second",
        title_suffix=None,
    )
    join_consecutive(
        "jild19-masala-172", 2,
        [
            (1, "start", "جواب کے اس بقیہ حصے میں اعلیٰ حضرت رحمۃ اللہ علیہ فرماتے ہیں کہ اگر کرایہ سالانہ"),
        ],
        sawal_mode="first",
        title_suffix=None,
    )
    join_cross_id(
        "jild19-masala-228",
        ["jild19-muna-wal-durar-2"],
        "head_only",
        [
            (0, "end", " سے متصادم نہ ہوگا۔ یہاں تک اس حصے کی تشریح ہے؛ جواب اس صفحے کے بعد بھی جاری ہے۔"),
            (1, "start", "یہ حصہ اسی رسالے کا بقیہ ہے جو صفحہ ۵۶۳ سے چلا آ رہا ہے، اور اس میں عرف و تعامل "),
        ],
    )
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS after joins: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )

    print(f"after joins: {len(all_items)} items (269 concatenated)")
    # MERGE-TIME RENAME (p.433 print error for ۱۵۰): id only — the
    # title already matches the merged-v3 title verbatim.
    _ren = next(it for it in all_items if it["id"] == "jild19-masala-250")
    assert _ren["title"] == V3_TITLES["jild19-masala-150"], "rename: title != v3 title"
    assert _ren["pages"] == V3_PAGES["jild19-masala-150"], "rename: pages != v3 pages"
    _ren["id"] = "jild19-masala-150"
    print('renames applied: [jild19-masala-250 -> jild19-masala-150]')
    assert len(all_items) == len({it["id"] for it in all_items}), "DUPLICATE IDS after rename"
    # STABLE SORT by start_page, mirroring the v3 merge: chunk 07's
    # masala-147-149 sits first in its file but belongs between 146
    # and 250 by start_page 422. Stable sort keeps tied start_pages
    # in concatenation order, exactly as v3.
    all_items.sort(key=lambda it: it["start_page"])
    print(f"sorted by start_page: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-19.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-19.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
