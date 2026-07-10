# Evaluating Large Language Models as Assistive Tools 
# for People with Communication and Cognitive Disabilities

## Overview
This repository contains the data, analysis code, and 
visualizations for a structured comparative audit of 
GPT-4, Claude, and Groq/Llama 3 as assistive 
communication tools across AAC, aphasia, and 
intellectual disability contexts.
The study examines model performance across three disability-specific contexts:


Augmentative and Alternative Communication (AAC) — sentence prediction tasks
Aphasia — sentence prediction tasks
Intellectual Disabilities — text simplification tasks


Performance is evaluated across five dimensions grounded in assistive technology (AT) principles, 
constituting the Communication Inclusion Framework (CIF):
## Authors
- Kehinde Soetan (lead researcher)
- [Rhoda Oladosu] — [@RhodaOladosu]
- [Precious Aforkeoghene]
- Jesujoba Olanrewaju

## Study Design
- 60 assistive communication prompts
- 13 expert raters
- 780 total evaluations
- 5 evaluation dimensions (CIF)
- Bayesian hierarchical modeling (PyMC 6.0.1)

## Repository Structure
- /data — anonymized rating dataset
- /analysis — Bayesian analysis notebook
- /visualizations — all figures from the paper
- /qualitative — CIF coding sheet
- /prompts — prompt library

## Requirements
pip install pymc bambi arviz pandas numpy 
matplotlib seaborn

## How to Reproduce
1. Clone the repo
2. Install requirements
3. Open analysis/bayesian_analysis.ipynb
4. Run all cells

## Citation
Soetan, K. et al. (2026). Evaluating Large Language 
Models as Assistive Tools for People with 
Communication and Cognitive Disabilities.

## License
MIT License — free to use with attribution
