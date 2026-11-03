# Third party notices

The MAUD-derived excerpts and annotations in `data/maud_mae.jsonl`, associated evidence in `results/`, and any real contract examples remain attributed to **The Atticus Project**, publisher of **Merger Agreement Understanding Dataset (MAUD) v1**.

Citation: Steven H. Wang, Antoine Scardigli, Leonard Tang, Wei Chen, Dimitry Levkin, Anya Chen, Spencer Ball, Thomas Woodside, Oliver Zhang, and Dan Hendrycks (2023), *MAUD: An Expert-Annotated Legal NLP Dataset for Merger Agreement Understanding*. [Paper](https://arxiv.org/abs/2301.00876). [Dataset](https://www.atticusprojectai.org/maud/).

The publisher identifies MAUD as **Creative Commons Attribution 4.0 International**: [publisher license page](https://www.atticusprojectai.org/legal/), [license summary](https://creativecommons.org/licenses/by/4.0/), [legal code](https://creativecommons.org/licenses/by/4.0/legalcode.en). Preserve this notice with copies or adaptations. No endorsement by The Atticus Project, ABA, Stanford, or the underlying contracting parties is implied.

Changes: selected four MAE binary questions from the original `main` data; retained source text and labels; mapped Yes/No to 1/0; merged by contract; retained original row IDs; assigned a new contract-disjoint split; computed predictions and review prompts. These transformations are by this project, not the source annotators. Full source contracts are downloaded only into ignored local raw storage by default.

The source publisher's stated dataset license is not an assertion that all underlying SEC exhibits are public-domain works or that other third-party rights cannot apply. Original software is licensed separately under MIT. Citations to judicial opinions supply legal context, not annotated litigation outcomes for the dataset.
