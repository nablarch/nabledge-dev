# Phase 21-Y / Y-1: docutils AST probe

## Parse health

| Version | Total | OK | Warn | Error |
|---|---:|---:|---:|---:|
| v6 | 667 | 667 | 0 | 0 |
| v5 | 772 | 771 | 1 | 0 |
| v1.4 | 464 | 389 | 71 | 4 |
| v1.3 | 380 | 317 | 62 | 1 |
| v1.2 | 298 | 239 | 59 | 0 |

## Table rowspan / colspan

| Version | tables | entries | morerows | morecols |
|---|---:|---:|---:|---:|
| v6 | 901 | 14610 | 74 | 52 |
| v5 | 1092 | 19344 | 91 | 77 |
| v1.4 | 1193 | 19341 | 133 | 90 |
| v1.3 | 927 | 14647 | 77 | 72 |
| v1.2 | 777 | 11357 | 72 | 55 |

## Substitution

| Version | Definitions | References |
|---|---:|---:|
| v6 | 95 | 0 |
| v5 | 133 | 0 |
| v1.4 | 1 | 0 |
| v1.3 | 0 | 0 |
| v1.2 | 0 | 0 |

## System messages by (level,type)

### v6

| (level,type) | count |
|---|---:|
| `level=1:type=INFO` | 452 |

### v5

| (level,type) | count |
|---|---:|
| `level=1:type=INFO` | 472 |
| `level=2:type=WARNING` | 1 |

### v1.4

| (level,type) | count |
|---|---:|
| `level=1:type=INFO` | 244 |
| `level=2:type=WARNING` | 184 |
| `level=3:type=ERROR` | 6 |

### v1.3

| (level,type) | count |
|---|---:|
| `level=1:type=INFO` | 204 |
| `level=2:type=WARNING` | 163 |
| `level=3:type=ERROR` | 1 |

### v1.2

| (level,type) | count |
|---|---:|
| `level=1:type=INFO` | 160 |
| `level=2:type=WARNING` | 157 |

## Top node types

### v6

| Node | Count |
|---|---:|
| `Text` | 78627 |
| `paragraph` | 38056 |
| `entry` | 14610 |
| `inline` | 10093 |
| `list_item` | 8557 |
| `row` | 5572 |
| `title` | 5438 |
| `literal` | 4891 |
| `section` | 4395 |
| `reference` | 3433 |
| `definition_list_item` | 3352 |
| `term` | 3352 |
| `definition` | 3352 |
| `literal_block` | 3134 |
| `bullet_list` | 2831 |
| `target` | 2807 |
| `colspec` | 2384 |
| `definition_list` | 1766 |
| `field` | 990 |
| `field_name` | 990 |
| `field_body` | 990 |
| `table` | 901 |
| `tgroup` | 901 |
| `tbody` | 901 |
| `tip` | 872 |
| `thead` | 821 |
| `block_quote` | 800 |
| `raw` | 708 |
| `document` | 667 |
| `title_reference` | 657 |

### v5

| Node | Count |
|---|---:|
| `Text` | 87990 |
| `paragraph` | 44388 |
| `entry` | 19344 |
| `inline` | 10804 |
| `list_item` | 9121 |
| `row` | 6750 |
| `title` | 5891 |
| `section` | 4752 |
| `literal` | 4331 |
| `definition_list_item` | 3619 |
| `term` | 3619 |
| `definition` | 3619 |
| `reference` | 3326 |
| `literal_block` | 3279 |
| `colspec` | 3026 |
| `bullet_list` | 2969 |
| `target` | 2858 |
| `definition_list` | 1907 |
| `strong` | 1479 |
| `table` | 1092 |
| `tgroup` | 1092 |
| `tbody` | 1092 |
| `block_quote` | 1041 |
| `field` | 1006 |
| `field_name` | 1006 |
| `field_body` | 1006 |
| `thead` | 1005 |
| `raw` | 977 |
| `tip` | 936 |
| `title_reference` | 805 |

### v1.4

| Node | Count |
|---|---:|
| `Text` | 48540 |
| `paragraph` | 29646 |
| `entry` | 19341 |
| `row` | 6703 |
| `line` | 4384 |
| `list_item` | 3482 |
| `title` | 3477 |
| `colspec` | 3315 |
| `strong` | 3142 |
| `section` | 2951 |
| `inline` | 2740 |
| `line_block` | 2436 |
| `literal_block` | 1784 |
| `block_quote` | 1541 |
| `target` | 1256 |
| `table` | 1193 |
| `tgroup` | 1193 |
| `tbody` | 1193 |
| `thead` | 1179 |
| `bullet_list` | 1152 |
| `definition_list_item` | 940 |
| `term` | 940 |
| `definition` | 940 |
| `definition_list` | 536 |
| `literal` | 505 |
| `note` | 474 |
| `document` | 464 |
| `image` | 455 |
| `reference` | 453 |
| `system_message` | 434 |

### v1.3

| Node | Count |
|---|---:|
| `Text` | 37469 |
| `paragraph` | 22666 |
| `entry` | 14647 |
| `row` | 5180 |
| `line` | 3490 |
| `list_item` | 2716 |
| `title` | 2704 |
| `colspec` | 2541 |
| `strong` | 2463 |
| `section` | 2255 |
| `inline` | 2164 |
| `line_block` | 1902 |
| `literal_block` | 1482 |
| `block_quote` | 1175 |
| `target` | 1015 |
| `table` | 927 |
| `tgroup` | 927 |
| `tbody` | 927 |
| `thead` | 916 |
| `bullet_list` | 904 |
| `definition_list_item` | 807 |
| `term` | 807 |
| `definition` | 807 |
| `definition_list` | 469 |
| `document` | 380 |
| `note` | 376 |
| `system_message` | 368 |
| `image` | 333 |
| `reference` | 307 |
| `literal` | 280 |

### v1.2

| Node | Count |
|---|---:|
| `Text` | 31553 |
| `paragraph` | 18761 |
| `entry` | 11357 |
| `row` | 4316 |
| `line` | 3094 |
| `list_item` | 2341 |
| `title` | 2311 |
| `colspec` | 2071 |
| `section` | 1956 |
| `inline` | 1898 |
| `strong` | 1874 |
| `line_block` | 1659 |
| `literal_block` | 1352 |
| `block_quote` | 1059 |
| `target` | 956 |
| `bullet_list` | 832 |
| `definition_list_item` | 802 |
| `term` | 802 |
| `definition` | 802 |
| `table` | 777 |
| `tgroup` | 777 |
| `tbody` | 777 |
| `thead` | 766 |
| `definition_list` | 449 |
| `note` | 369 |
| `system_message` | 317 |
| `image` | 309 |
| `document` | 298 |
| `literal` | 245 |
| `reference` | 233 |

## Problem files (first 30 per version)

### v6 (problem files total: 0)

_none_

### v5 (problem files total: 0)

_none_

### v1.4 (problem files total: 4)

- `/home/tie303177/work/nabledge/work2/.lw/nab-official/v1.4/document/fw/core_library/enterprise_messaging_overview.rst` — parse_error
  - `<string>:1: (WARNING/2) "include" directive disabled.`
- `/home/tie303177/work/nabledge/work2/.lw/nab-official/v1.4/document/guide/04_Explanation_messaging/04_Explanation_http_send_sync/02_basic.rst` — parse_error
  - `<string>:52: (ERROR/3) Unexpected indentation.`
- `/home/tie303177/work/nabledge/work2/.lw/nab-official/v1.4/document/sample/portal/doc/index.rst` — parse_error
  - `<string>:102: (ERROR/3) Malformed table.`
- `/home/tie303177/work/nabledge/work2/.lw/nab-official/v1.4/document/tool/07_AuthGenerator/01_AuthGenerator.rst` — parse_error
  - `<string>:276: (ERROR/3) Inconsistent title style: skip from level 2 to 4.`

### v1.3 (problem files total: 1)

- `/home/tie303177/work/nabledge/work2/.lw/nab-official/v1.3/document/sample/portal/doc/index.rst` — parse_error
  - `<string>:102: (ERROR/3) Malformed table.`

### v1.2 (problem files total: 0)

_none_
