# ViText - Vietnamese Text Normalization Toolkit

## Introduction

ViText is a **personal project** created for learning purposes, based on the [Vinorm](https://github.com/v-nhandt21/Vinorm), It provides powerful Vietnamese text normalization for **Natural Language Processing** (NLP) tasks. The project supports conversion, phonetic transcription, and normalization of special entities such as numbers, dates, measurement units, product codes, emails, phone numbers, abbreviations, and many other Vietnamese-specific patterns.

ViText is designed to standardize text for various applications such as Text-to-Speech (TTS), smart search, chatbots, text analytics, and AI/ML data preparation for personal projects.

## Key Features

- **Number-to-word conversion**: "1000" → "một nghìn"
- **Number + unit expansion**: "245l" → "hai trăm bốn mươi lăm lít"
- **Product code and serial normalization**: "ABC-01-23A" → "a bê xê không một hai ba a"
- **Date normalization**: "12/2020" → "tháng mười hai năm hai nghìn không trăm hai mươi"
- **Protect and spell out emails, phone numbers, websites:**: "[abc@gmail.com](mailto\:abc@gmail.com)" → "a bê xê a còng giy em a i eo chấm xê o em"
- **Abbreviation, technical term, and measurement expansion**: "km", "cm", "mg", "lmht", ...
- **Remove/replace unwanted characters**: (), -, \_
- **Preserve native Vietnamese words**: Valid Vietnamese words remain unchanged

## Project Structure
```
vitext/
├── core.py        # Main class and normalization logic
├── utils.py       # Utility functions for number/unit handling, pattern matching, spelling, etc.
├── main.py        # Example/demo script for quick normalization testing
├── dicts/         # Folder for unit, abbreviation, and special rule dictionaries (customizable)
└── output.txt     # Output file (created after running main.py)
```

## Technology Stack

- Python 3.11
- Standard libraries: `os`, `re`, `chardet` (for automatic encoding detection in dictionary files)
- No third-party dependencies except for `chardet` (only for robust dictionary file reading)

## Component Overview

- **core.py**:\
    The `Vinorm` class is responsible for the main normalization process. It can be customized with additional functions and dictionaries.

- **utils.py**:\
    Provides functions for:

    - Number-to-word conversion

    - Spelling out characters, emails, phone numbers

    - Special pattern recognition (dates, numbers, units, etc.)

    - Helper functions for tokenization, protection, and string replacement

- **main.py**:\
  Example usage—you can change the input to test different cases.

- **dicts/**:\
  Lookup dictionaries for measurement units, abbreviations, special names, and customizable rules (user-defined in `key#value` format)

## Real-world Applications
- Vietnamese Text-to-Speech (TTS) preprocessing
- Text normalization for analytics, search, chatbot, or AI/ML tasks
- Converting reports, invoices, emails, and messages into a more readable or standardized format
- Vietnamese NLP research and academic projects

## Acknowledgements
- Special thanks to [Mr. Đỗ Trí Nhân](https://github.com/v-nhandt21), the original author of the Vinorm library, for making this resource and its extensive Vietnamese datasets available to the community.