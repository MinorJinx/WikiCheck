# WikiCheck

Searches wikipedia to check if url has a wikipage.

Uses BeautifulSoup to parse wikipage infobox to find website hrefs.

If input url matches url on the wikipage, the wikipage is searched for the terms 'mainstream' and 'popular'.

```
Expects .csv with hostnames in first column.
Outputs .csv with list of mainstream/popular hostnames.
```
