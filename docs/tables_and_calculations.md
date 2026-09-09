# Tables, CSV Imports & Expression Calculations

LabRecord Engine includes a flexible table typesetting system supporting multi-column layouts, comma-separated entry shorthands, direct CSV file imports, and an automated mathematical expression evaluation engine for experimental calculations.

---

## 1. Table Types & Formats

### Format A: Direct CSV Import (`"csv"`)
Specify `"csv": "path/to/file.csv"` in your table section. The engine automatically reads the CSV matrix, converts LaTeX expressions, applies table borders, and formats column headers.

```json
{
  "type": "table",
  "title": "DC Characteristics Data",
  "csv": "data/dc_sweep.csv",
  "delimiter": ","
}
```

---

### Format B: Row-Based & Column-Based Tables (`"element_type"`)
Tables can be structured by row or by column:

#### Column-Based Example:
```json
{
  "type": "table",
  "title": "Design Parameters",
  "element_type": "column",
  "elements": [
    {
      "title": "Parameter",
      "entries": ["Technology", "$V_{DD}$", "PMOS Width ($W_p$)"]
    },
    {
      "title": "Value",
      "entries": ["180 nm", "1.8 V", "400 nm"]
    }
  ]
}
```

---

### Format C: Comma-Separated Entry Shorthand
Instead of declaring separate entries arrays, write comma-separated strings inside entries:

```json
{
  "type": "table",
  "title": "MOSFET Specification Table",
  "elements": [
    {
      "title": "Parameter",
      "entries": [
        "Technology , 180 nm",
        "$V_{DD}$ , 1.8 V",
        "PMOS Width ($W_p$) , 0.9 \\mu m",
        "NMOS Width ($W_n$) , 0.45 \\mu m"
      ]
    }
  ]
}
```

Or write raw shorthand row strings:

```json
{
  "type": "table",
  "title": "Quick Data Table",
  "elements": [
    "Parameter , Value , Unit",
    "Technology , 180 , nm",
    "Supply Voltage , 1.8 , V"
  ]
}
```

---

## 2. Dynamic Table Calculations & Formula Engine

LabRecord Engine supports automatic cell arithmetic, cross-references, and mathematical functions directly inside table cell entries.

### Relative Cell References

| Syntax | Target Cell Reference |
| :--- | :--- |
| `r<R>e<E>` | Cell at row `R` (1-indexed) and element/column `E` (1-indexed). Example: `r2e2`. |
| `c<C>e<E>` | Cell at column `C` (1-indexed) and element/row `E` (1-indexed). Example: `c1e2`. |
| `re<E>` | Cell at **same row**, element/column `E`. Example: `re1`. |
| `ce<E>` | Cell at **same column**, element/row `E`. Example: `ce1`. |

---

### Supported Expression Operations

#### Basic Arithmetic (`+`, `-`, `*`, `/`)
Calculate values between relative cells.

Example: Subtract element 1 of row 2 from element 2 of row 2 (`r2e2 - r2e1`):

```json
{
  "type": "table",
  "title": "Resistance Calculations",
  "element_type": "row",
  "elements": [
    { "title": "Header", "entries": ["Initial (V)", "Final (V)", "Delta (V)"] },
    { "title": "Trial 1", "entries": ["1.2", "4.8", "re2 - re1"] }
  ]
}
```
*Result in PDF*: Delta column automatically evaluates to `3.6`.

---

#### Average Function: `$avg(...)`
Computes the arithmetic mean of a list of cell references.

```json
"$avg(re1, ce2, r3e2)"
```

```json
{
  "type": "table",
  "title": "Voltage Measurement Averages",
  "elements": [
    "Trial , V1 , V2 , V3 , Average",
    "Run 1 , 1.8 , 1.82 , 1.79 , $avg(re2, re3, re4)"
  ]
}
```
*Result in PDF*: Average column automatically evaluates to `1.8033`.

---

#### Percentage Error Function: `$perr(theoretical, experimental)`
Computes percentage error between theoretical value $V_{th}$ and experimental value $V_{exp}$:

$$\text{Error} = \frac{|V_{th} - V_{exp}|}{V_{th}} \times 100\%$$

```json
"$perr(re1, re2)"
```

```json
{
  "type": "table",
  "title": "Threshold Voltage Error",
  "elements": [
    "Parameter , Theoretical , Measured , % Error",
    "$V_{TH}$ , 0.50 , 0.52 , $perr(re2, re3)"
  ]
}
```
*Result in PDF*: % Error column automatically evaluates to `4.00%`.
