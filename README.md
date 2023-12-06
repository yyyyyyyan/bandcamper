```
   ▄▀▀█▄▄   ▄▀▀█▄   ▄▀▀▄ ▀▄  ▄▀▀█▄▄   ▄▀▄▄▄▄   ▄▀▀█▄   ▄▀▀▄ ▄▀▄  ▄▀▀▄▀▀▀▄  ▄▀▀█▄▄▄▄  ▄▀▀▄▀▀▀▄
  ▐ ▄▀   █ ▐ ▄▀ ▀▄ █  █ █ █ █ ▄▀   █ █ █    ▌ ▐ ▄▀ ▀▄ █  █ ▀  █ █   █   █ ▐  ▄▀   ▐ █   █   █
    █▄▄▄▀    █▄▄▄█ ▐  █  ▀█ ▐ █    █ ▐ █        █▄▄▄█ ▐  █    █ ▐  █▀▀▀▀    █▄▄▄▄▄  ▐  █▀▀█▀
    █   █   ▄▀   █   █   █    █    █   █       ▄▀   █   █    █     █        █    ▌   ▄▀    █
   ▄▀▄▄▄▀  █   ▄▀  ▄▀   █    ▄▀▄▄▄▄▀  ▄▀▄▄▄▄▀ █   ▄▀  ▄▀   ▄▀    ▄▀        ▄▀▄▄▄▄   █     █
  █    ▐   ▐   ▐   █    ▐   █     ▐  █     ▐  ▐   ▐   █    █    █          █    ▐   ▐     ▐
  ▐                ▐        ▐        ▐                ▐    ▐    ▐          ▐
```

# bandcamper
The most powerful Bandcamp downloader there is! If you can play a song on Bandcamp, bandcamper can download it for free ;).

## Description

bandcamper is a Python-powered tool that tries its best to download albums and tracks from Bandcamp for free! It does that by trying these 3 methods:

1. If an item has a "free download" option ([example](https://concretomorto.bandcamp.com/album/medo-da-astrologia)), amazing! bandcamper will be able to download it in **any format** you'd like.
2. If an item has an "email download" option ([example](https://stippling.bandcamp.com/album/stippling)), amazing! bandcamper will use [onesecmail](https://github.com/yyyyyyyan/onesecmail) to get a temporary email address and will be able to download the item in **any format** you'd like.
3. If an item is playable via Bandcamp ([example](https://eltorofuerte.bandcamp.com/album/nossos-amigos-e-os-lugares-que-visitamos)), good! bandcamper will be able to download it in **mp3-128 format**.

### Does Bandcamp allow this?

You can read Bandcamp's position [here (*I heard you can steal music on Bandcamp. What are you doing about this?*)](https://get.bandcamp.help/hc/en-us/articles/360007902173-I-heard-you-can-steal-music-on-Bandcamp-What-are-you-doing-about-this-).

## Installation

Use [pipx](https://github.com/pypa/pipx) or [pip](https://pip.pypa.io/en/stable/) to install **bandcamper**:
```bash
pipx install bandcamper
```

## Usage

Call `bandcamper` through the command line:

```
Usage: bandcamper [OPTIONS] URL [URL...]

Options:
  Input Options:
    -i, --input FILE              Download from URLs/artists subdomains listed
                                  on file. This option can be used multiple
                                  times
  Audio Options:
    -f, --format [aac-hi|aiff-lossless|alac|flac|mp3-128|mp3-320|mp3-v0|vorbis|wav]
                                  Preferred audio formats to download. This
                                  option can be used multiple times. Defaults
                                  to mp3-320.
    --fallback / --no-fallback    Download fallback mp3-128 audio file in case
                                  there are no other free downloads available
  Download Options:
    -d, --destination DIRECTORY   Base destination folder for downloaded
                                  files. Defaults to current folder
    -o, --output TEMPLATE         Output filename template. See the 'Output
                                  Template' section of the README for all the
                                  info
    --output-extra TEMPLATE       Output filename template for extra files.
                                  See the 'Extra Output Template' section of
                                  the README for all the info
  Request Options:
    --random-user-agent           Use random User-Agent for Bandcamp requests
    --http-proxy URL              Proxy to use for HTTP connections
    --https-proxy URL             Proxy to use for HTTPS connections
    --proxy URL                   Proxy to use for all connections. This
                                  option overrides --http-proxy and --https-
                                  proxy
    --force-https / --no-force-https
                                  Rewrite every URL to use HTTPS  [default:
                                  force-https]
  Output Options:
    -v, --verbose                 Run bandcamper with more verbose output
    -q, --quiet                   Completely disable output
    --colored / --no-colors       Use colored output  [default: colored]
  --config FILE                   Read option defaults from the specified JSON
                                  config file. Defaults to
                                  bandcamper_config.json
  -V, --version                   Show the version and exit.
  -h, --help                      Show this message and exit.
```

### Output Template

The output template is a string that can contain special variables and will be joined to the destination directory to determine the final path of the downloaded tracks.

This template follows the Python string formatting scheme of `{var}` and is, by default, `"{artist}/{album}/{track_num:02d} - {track}.{ext}"`. You can change the template through the -o/--output flag.

Two output operators are implemented; `u` and `l` which format the variable to all upper-case or all lower-case respectively. These are used with `{var:format}` where `format` is either of the format characters.

These are the available variables you can use in the template:

| Variable  | Description                |
|-----------|----------------------------|
| album     | The album's title          |
| artist    | The artist's name          |
| ext       | The track's file extension |
| track     | The track's title          |
| track_num | The track number           |
| year      | The album's release year   |

### Extra Output Template

Some Bandcamp downloads come with extra files other than the tracks, like the cover art image. These files will not follow the output template, since they are not tracks.

Instead, they follow the extra output template, which can be passed through the --output-extra parameter and by default is `"{artist}/{album}/{filename}"`.

These are the available variables you can use in the template:

| Variable  | Description                |
|-----------|----------------------------|
| album     | The album's title          |
| artist    | The artist's name          |
| filename  | The name of the file       |
| year      | The album's release year   |


### Examples

#### Download all releases from the band [stippling](https://stippling.bandcamp.com/):
```
bandcamper stippling
```

#### Download album [stippling - Perfect Life](https://stippling.bandcamp.com/album/perfect-life) in flac format:
```
bandcamper -f flac "https://stippling.bandcamp.com/album/perfect-life"
```
Results:
```
stippling
└── Perfect Life
   ├── 01 - My Friend Dead.flac
   ├── 02 - Oh My God.flac
   ├── 03 - Sunshine Kids.flac
   ├── 04 - Brights.flac
   ├── 05 - Monologue.flac
   ├── 06 - 2am.flac
   ├── 07 - Inner Dark.flac
   ├── 08 - Think of You.flac
   ├── 09 - Scared of Changing.flac
   ├── 10 - Ready Set Rock.flac
   ├── 11 - The Journal.flac
   ├── 12 - Letters to Ghosts.flac
   ├── 13 - Fake Smile.flac
   ├── 14 - Perfect Life.flac
   └── cover.jpg
```
#### Download album [stippling - Perfect Life](https://stippling.bandcamp.com/album/perfect-life) in flac and mp3-320 formats with custom output template:
```
bandcamper -f flac -f mp3-320 -o "{artist}/{album} ({year})/{ext}/{track_num:02d} - {track}.{ext}" --output-extra "{artist}/{album} ({year})/{filename}" "https://stippling.bandcamp.com/album/perfect-life"

```
Results:
```
stippling
└── Perfect Life (2018)
   ├── cover.jpg
   ├── flac
   │  ├── 01 - My Friend Dead.flac
   │  ├── 02 - Oh My God.flac
   │  ├── 03 - Sunshine Kids.flac
   │  ├── 04 - Brights.flac
   │  ├── 05 - Monologue.flac
   │  ├── 06 - 2am.flac
   │  ├── 07 - Inner Dark.flac
   │  ├── 08 - Think of You.flac
   │  ├── 09 - Scared of Changing.flac
   │  ├── 10 - Ready Set Rock.flac
   │  ├── 11 - The Journal.flac
   │  ├── 12 - Letters to Ghosts.flac
   │  ├── 13 - Fake Smile.flac
   │  └── 14 - Perfect Life.flac
   └── mp3
      ├── 01 - My Friend Dead.mp3
      ├── 02 - Oh My God.mp3
      ├── 03 - Sunshine Kids.mp3
      ├── 04 - Brights.mp3
      ├── 05 - Monologue.mp3
      ├── 06 - 2am.mp3
      ├── 07 - Inner Dark.mp3
      ├── 08 - Think of You.mp3
      ├── 09 - Scared of Changing.mp3
      ├── 10 - Ready Set Rock.mp3
      ├── 11 - The Journal.mp3
      ├── 12 - Letters to Ghosts.mp3
      ├── 13 - Fake Smile.mp3
      └── 14 - Perfect Life.mp3

```

## Contributing

Pull requests are welcome! We just released the alpha so right now our top priorities are **refactoring** and **testing**, but any contribution might be a good contribution :-). I also plan on replacing requests with httpx soon.

In order to start contributing with bandcamper's code, make sure you install the pre-commit hooks listed in the [.pre-commit-config.yaml](https://github.com/yyyyyyyan/bandcamper/blob/main/.pre-commit-config.yaml) file with the following commands:
```bash
pip install -r requirements_dev.txt
pre-commit install
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yyyyyyyan/bandcamper/blob/main/LICENSE) file for details.
