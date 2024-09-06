## SECURITY.md

Tools used to parse standardize [SECURITY.md](https://github.com/sbrunner/security.md/wiki/SECURITY.md) files.

## Usage:

```python
from security_md import Security

security = Security("""
| Version         | Supported Until | Alternate Tag |
| --------------- | --------------- | ------------- |
| 7.6             | 23/06/2025      |               |
| 7.6-gdal3.7     | Best effort     |               |
| 7.6-gdal3.8     | Best effort     | 7.6           |
| 7.6-gdal3.9     | Best effort     |               |
""")
print(security.headers)
print(security.raw)
for version in security.supported_versions():
    print(version)
    print(security.all_tags(version))
```
