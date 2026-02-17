# Data preparation scripts

The following scripts can be used for preparing the web page data on the FitLayout server:

- `render.py` - renders the pages listed in /data/book_urls.txt, creates the [Page artifacts](https://github.com/FitLayout/FitLayout/wiki/Basic-Concepts#artifact-types)
- `segment.py` - performs simple segmentation, creates an AreaTree for each Page
- `tagging.py` - an example script that assigns tags to important area (book titles and prices in this example) using simple DOM-based and presentation-based rules.

## Configuration

All the script share the FitLayout server configuration defined in [config.py](config.py).

## Running the scripts

The scripts can be executed from the root folder, e.g.:

```bash
python src/prepare/render.py
```

For an interactive CLI that allows to manage the configured repository content use:

```bash
python src/prepare/cli.py
```
