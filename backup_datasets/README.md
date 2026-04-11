# Dataset Backup - 2026-03-18 13:32:27

## What's in this backup?

These files were consolidated into `combined-training-dataset-final.json` and are no longer needed.
They are kept here as a backup only.

## Files backed up:
- unified-prompts-dataset.json
- clean-selenium-dataset.json
- page-helper-patterns-dataset-clean.json
- page-helper-training-dataset-clean.json
- page-helper-training-dataset.json
- common-web-actions-dataset-clean.json
- page-helper-prompts.json
- page-helper-patterns-dataset.json
- page-helper-selenium-converted.json
- combined-training-dataset-clean.json

## Consolidation details:

- **Final dataset**: combined-training-dataset-final.json
- **Total entries**: 1,961 unique prompts
- **Coverage**: 100% of all source datasets
- **Duplicates removed**: ~2,650+
- **Code quality**: 100% have working code, 96.3% have XPath

## Can I delete this backup?

Yes, after verifying that:
1. Your application works with the final dataset
2. All tests pass
3. You've confirmed you don't need the original dataset structures

## Restore instructions:

If needed, copy files from this backup back to `src/resources/` directory.
