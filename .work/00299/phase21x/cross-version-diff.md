# Cross-version pattern comparison

## Inline patterns (count per version)

| Pattern | v6 | v5 | v1.4 | v1.3 | v1.2 |
|---|---:|---:|---:|---:|---:|
| role_target | 2902 | 3075 | 54 | 414 | 476 |
| role_simple | 2137 | 2759 | 772 | 1417 | 1430 |
| double_backtick | 2448 | 2215 | 190 | 263 | 246 |
| ext_link_named | 282 | 280 | 42 | 81 | 81 |
| ext_link_anon | 4 | 4 | 0 | 0 | 0 |
| ref_named | 103 | 107 | 26 | 290 | 293 |
| ref_anon | 0 | 0 | 0 | 0 | 0 |
| substitution | 387 | 697 | 16 | 20 | 20 |
| footnote_ref | 198 | 219 | 31 | 131 | 137 |
| strong | 285 | 1238 | 1182 | 1789 | 1861 |
| emphasis | 105 | 134 | 75 | 117 | 118 |
| interpreted | 331 | 417 | 74 | 35 | 31 |

## Role names in use (per version)

### role_target

| Role | v6 | v5 | v1.4 | v1.3 | v1.2 |
|---|---:|---:|---:|---:|---:|
| doc | 9 | 8 | 0 | 12 | 10 |
| download | 29 | 67 | 9 | 45 | 51 |
| java:extdoc | 1837 | 1856 | 0 | 0 | 0 |
| javadoc_url | 4 | 4 | 0 | 0 | 0 |
| ref | 1023 | 1140 | 45 | 357 | 415 |

### role_simple

| Role | v6 | v5 | v1.4 | v1.3 | v1.2 |
|---|---:|---:|---:|---:|---:|
| doc | 104 | 611 | 533 | 569 | 560 |
| java:extdoc | 134 | 132 | 0 | 0 | 0 |
| ref | 1896 | 2013 | 239 | 845 | 867 |
| strong | 3 | 3 | 0 | 3 | 3 |

## Directive names (per version)

| Directive | v6 | v5 | v1.4 | v1.3 | v1.2 |
|---|---:|---:|---:|---:|---:|
| admonition | 0 | 0 | 2 | 84 | 84 |
| attention | 0 | 0 | 5 | 8 | 7 |
| class | 0 | 0 | 2 | 3 | 1 |
| code-block | 1543 | 1724 | 254 | 1109 | 1114 |
| contents | 154 | 156 | 0 | 5 | 0 |
| csv-table | 1 | 1 | 0 | 0 | 0 |
| figure | 10 | 26 | 16 | 23 | 23 |
| function | 0 | 0 | 24 | 20 | 18 |
| hint | 0 | 0 | 3 | 0 | 0 |
| image | 290 | 338 | 85 | 283 | 285 |
| important | 285 | 306 | 0 | 0 | 0 |
| include | 0 | 0 | 0 | 59 | 58 |
| java:method | 1 | 1 | 0 | 0 | 0 |
| list-table | 135 | 149 | 25 | 48 | 40 |
| literalinclude | 0 | 0 | 0 | 12 | 19 |
| note | 10 | 10 | 86 | 347 | 355 |
| raw | 0 | 0 | 0 | 152 | 149 |
| rubric | 0 | 0 | 0 | 1 | 1 |
| table | 60 | 60 | 0 | 0 | 0 |
| tip | 434 | 508 | 0 | 0 | 0 |
| toctree | 100 | 108 | 20 | 110 | 109 |
| warning | 4 | 4 | 19 | 88 | 85 |

## Patterns exclusive to a subset of versions

### Directives appearing in < 5 versions

- **admonition**: present in ['1.4', '1.3', '1.2'], absent elsewhere
- **attention**: present in ['1.4', '1.3', '1.2'], absent elsewhere
- **class**: present in ['1.4', '1.3', '1.2'], absent elsewhere
- **contents**: present in ['6', '5', '1.3'], absent elsewhere
- **csv-table**: present in ['6', '5'], absent elsewhere
- **function**: present in ['1.4', '1.3', '1.2'], absent elsewhere
- **hint**: present in ['1.4'], absent elsewhere
- **important**: present in ['6', '5'], absent elsewhere
- **include**: present in ['1.3', '1.2'], absent elsewhere
- **java:method**: present in ['6', '5'], absent elsewhere
- **literalinclude**: present in ['1.3', '1.2'], absent elsewhere
- **raw**: present in ['1.3', '1.2'], absent elsewhere
- **rubric**: present in ['1.3', '1.2'], absent elsewhere
- **table**: present in ['6', '5'], absent elsewhere
- **tip**: present in ['6', '5'], absent elsewhere

### Roles appearing in < 5 versions

- **role_target::doc**: ['6', '5', '1.3', '1.2']
- **role_target::java:extdoc**: ['6', '5']
- **role_target::javadoc_url**: ['6', '5']
- **role_simple::java:extdoc**: ['6', '5']
- **role_simple::strong**: ['6', '5', '1.3', '1.2']

## Block metrics per version

| Metric | v6 | v5 | v1.4 | v1.3 | v1.2 |
|---|---:|---:|---:|---:|---:|
| simple_table_count | 684 | 1215 | 747 | 1908 | 1794 |
| grid_table_sep_count | 413 | 459 | 102 | 651 | 629 |
| grid_table_head_count | 70 | 75 | 15 | 130 | 123 |
| line_block_count | 834 | 942 | 1065 | 2755 | 2682 |

## Section underline characters per version

| v | Underline chars |
|---|---|
| v6 | {'=': 635, '-': 1265, '^': 63, '~': 544, '*': 14, '+': 14, '`': 2} |
| v5 | {'=': 936, '-': 1447, '~': 581, '^': 53, '*': 22, '+': 10, '`': 2} |
| v1.4 | {'=': 408, '-': 349, '^': 20, '~': 8, '*': 8} |
| v1.3 | {'=': 1048, '-': 1070, '^': 56, '~': 100, '*': 18} |
| v1.2 | {'=': 1026, '-': 1043, '^': 53, '~': 97} |
