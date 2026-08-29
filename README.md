# Protein Ensemble Python SDK

## Run codegen

```bash
datamodel-codegen \            
  --input schemas/v0/manifest.schema.json \
  --input-file-type jsonschema \
  --output-model-type pydantic_v2.BaseModel \
  --preset standard-py312-20260826 \
  --output src/protein-ensemble-types/src/protein_ensemble_types/models.py
```
