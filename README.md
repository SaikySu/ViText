# ViText - Vietnamese Text Normalization Toolkit

## Introduction

ViText is a **personal project** created for learning purposes, based on the [Vinorm](https://github.com/v-nhandt21/Vinorm), It provides powerful Vietnamese text normalization for **Natural Language Processing** (NLP) tasks. The project supports conversion, phonetic transcription, and normalization of special entities such as numbers, dates, measurement units, product codes, emails, phone numbers, abbreviations, and many other Vietnamese-specific patterns.

ViText is designed to standardize text for various applications such as Text-to-Speech (TTS), smart search, chatbots, text analytics, and AI/ML data preparation for personal projects.

---

## Key Features

| Feature                        | Example Input            | Example Output                                         |
|--------------------------------|--------------------------|--------------------------------------------------------|
| **Number-to-word conversion**  | `1000`                   | `một nghìn`                                            |
| **Number + unit expansion**    | `245l`                   | `hai trăm bốn mươi lăm lít`                            |
| **Product code normalization** | `ABC-01-23A`             | `a bê xê không một hai ba a`                           |
| **Date normalization**         | `12/2020`                | `tháng mười hai năm hai nghìn không trăm hai mươi`     |
| **Email/phone/website**        | `abc@gmail.com`          | `a bê xê a còng giy em a i eo chấm xê o em`            |
| **Unit & abbreviation**        | `km, cm, mg, lmht`       | Expanded in Vietnamese (customizable)                  |
| **Clean unwanted chars**       | `(), -, _`               | Removed or replaced                                    |
| **Keep Vietnamese words**      | `xin chào`               | `xin chào`                                             |

---

## Technologies Used

| Component     | Description                                                        |
|---------------|--------------------------------------------------------------------|
| **Python 3.11**  | Core language                                                  |
| **Standard Libs**| `os`, `re` for file & regex                                     |
| **chardet**      | Encoding detection for robust dictionary loading                |

> No third-party dependencies except `chardet` (for dictionary files).

---

## Project Structure

```
vitext/
├── core.py        # Main class and normalization logic
├── utils.py       # Utility functions: number/unit conversion, patterns, etc.
├── main.py        # Example script: run normalization, test samples
├── dicts/         # Dictionaries: units, abbreviations, rules (customizable)
└── output.txt     # Output after running main.py
```

---

## Component Overview 1.0 Version

| File/Folder | Purpose                                                                          |
|-------------|----------------------------------------------------------------------------------|
| `core.py`   | Contains the main `Vinorm` class: normalization workflow, extensible API         |
| `utils.py`  | Utilities: number-to-word, spelling, pattern matching, helpers                   |
| `main.py`   | Example usage: test normalization with your inputs                               |
| `dicts/`    | Dictionary files for measurement units, abbreviations, user rules, etc.          |

---

## Real-world Applications

- **Vietnamese TTS** preprocessing
- Text normalization for **search, chatbot, analytics, or AI/ML**
- Standardize invoices, emails, reports for data processing
- Research, academic, and personal NLP projects

---

## System Requirements

- Python 3.11+
- Install `chardet`:
  ```bash
  pip install chardet
  ```

---

## Customization

- Edit/add new rules and expansions by updating files in the `dicts/` folder (format: `key#value` per line).
- Extend `core.py` and `utils.py` to add new patterns or normalization logic.

---

## Acknowledgements

- Special thanks to [Mr. Đỗ Trí Nhân](https://github.com/v-nhandt21), the original author of the Vinorm library, for making this resource and its extensive Vietnamese datasets available to the community.

## Fix version & Note
- **1.0**: In this version, I used hard-coded logic to test the stable operation of most functions defined in `utils` and `core`. 
> The code runs stably in most common cases; however, it takes too much time to run all test cases `(~8s for 92 test cases)`.

- **2.0**: In this version, I used classes defined in different modules and organized the flow in a more structured and debuggable way.
> The code works well for many more complex cases compared to 1.0 and significantly improves performance `(<1s with 152 test cases)`. However, there are still some bugs when the input is a complex code string longer than `20` characters.