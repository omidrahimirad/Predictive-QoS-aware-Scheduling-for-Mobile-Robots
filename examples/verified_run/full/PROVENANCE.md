# Full campaign provenance

The campaign was launched before a report-only repair that supplies column names
for empty statistical tables. That repair is needed for a single-policy demo and
changes no numeric computation in this full seven-policy campaign. The exact
source fingerprint at launch is recorded in manifest.json. All other Python
source files match the current implementation. The fingerprint was independently
reconstructed exactly by reverting the attached full-launch-to-current.patch.

The campaign was launched before the first local commit, so its Git commit is
honestly recorded as unborn. It completed 2,730 episode-policy runs. Reproduction
from the current commit will have a different run ID and source fingerprint.
The simulator, predictors, seeds, policy weights, and statistical equations are
unchanged by the empty-table reporting repair.
