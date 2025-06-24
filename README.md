# Linking References to Documents in Parliamentary Debates

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

This repository contains the code and data for the paper "Linking References to Documents in Parliamentary Debates" by Floris Bos, Marc van Opijnen, and Maarten Marx (see [paper.pdf](paper.pdf) for the full paper).

The project focuses on improving the accessibility of Dutch parliamentary minutes by automatically detecting, validating, and linking textual references to their corresponding official documents.

## Abstract

In Dutch parliamentary debates, over 95\% of references to documents are implicit and non-standardized, hindering document accessibility and analysis. To address this challenge, we introduce a two-phase approach to automatically detect and link these references. The first phase uses a Large Language Model (LLM), specifically Gemini 2.5 Flash, for reference detection and semantic enrichment, extracting features like document type, a summary, and keywords. The second phase links these references to known documents using vector similarity search. Our large-scale analysis of 281 debates confirms the scale of the problem, revealing that nearly 74\% of all detected references are implicit. Evaluation on a new, manually annotated gold-standard dataset of 191 references shows our detection method achieves an F1-score of 0.49, while the LLM classifies semantic features like document type with 92-97\% accuracy. For the linking task, evaluated on 1,933 references, combining LLM-generated keywords with metadata filtering proves most effective. This approach correctly identifies the target document in 35\% of cases (Hit@1) and places it in the top 10 candidates of 57\% of the time (MRR 0.42). This work serves as a strong baseline for resolving complex, implicit references in a parliamentary proceedings. The methodology is inherently language-agnostic and shows significant promise for adaptation to other domains, such as legal case law or historical archives.

**Keywords**: Document Linking · Large Language Models · Known-item Search · Semantic Searchs.

## Table of Contents

- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
<!-- - [Citation](#citation) -->

## File Structure

The repository is organized into the main system code, experiments, and the annotated dataset.

```
linking-references-to-docs-in-parl-debates/
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
├── annotated-dataset/      # Manually annotated data and analysis notebooks
├── experiments/            # Scripts and results for experiments from the paper
├── README.md               # This file
└── system/                 # The main application source code
    ├── __main__.py         # Main entry point for the application
    ├── .env                # Environment variables (e.g., API keys)
    ├── config.py           # Configuration settings (API keys, paths)
    ├── data/               # Corpus of parliamentary documents to search against
    ├── detection.py        # Module for Phase 1: Reference Detection
    ├── featurebuilder.py   # Helper to construct query features
    ├── prompts/            # Prompt templates for the LLM
    ├── reconciliation.py   # Module for Phase 2: Reference Linking
    ├── utils/              # Helper utilities (file I/O, LLM wrappers, etc.)
    └── vectordb/           # Code for managing the Elasticsearch vector index
```

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/BluntKatana/linking-references-to-docs-in-parl-debates.git
    cd linking-references-to-docs-in-parl-debates
    ```

2.  **Set up a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    - Set up an Elasticsearch instance and provide the connection details in `system/config.py`.
    - Add your Google AI Platform API key to `system/config.py` to use the Gemini model.
    - Run the script to populate the vector database:
      ```bash
      python -m system.vectordb.fill_index --source_file system/data/documents_2000-2025_hundred-each-year.csv
      ```

## Usage

To run the full pipeline on a new text file containing parliamentary minutes:

```bash
python -id minute_id --system system
```

<!-- ## Citation

If you use this work, please cite the following paper:

```bibtex
@inproceedings{Bos2025Linking,
  author    = {Bos, Floris and Boersma, Wietske and van Opijnen, Marc and Marx, Maarten},
  title     = {Linking References to Documents in Parliamentary Debates},
  booktitle = {[TODO: Conference or Journal Name]},
  year      = {2025},
  pages     = {[TODO: Page numbers]},
  publisher = {[TODO: Publisher]}
}
```
-->

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
