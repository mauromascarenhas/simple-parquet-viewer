# Simple Parquet Viewer

Simple visualization tool for Parquet files.

## TODO

- Translations
- Package

## Generating icon

```sh
magick convert .\src\res\imgs\app_icon.svg -define icon:auto-resize=256,128,48,32,16 -background none -fuzz 10% -transparent white  .\src\res\imgs\app_icon.ico
```

## Translations

In order to generate a translation file, it is necessary to run the following command:

```sh
python ./scripts/i18n.py generate {LANG_CODE}
```

Then, you are going to be able to edit the strings with QtLinguist:

```sh
python ./scripts/i18n.py edit {LANG_CODE}
```

Finally, just release the translation:

```sh
python ./scripts/i18n.py release {LANG_CODE}
```