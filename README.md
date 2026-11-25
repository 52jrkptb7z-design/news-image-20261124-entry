# The World in One Day — Tuesday, 24 November 2026

[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/52jrkptb7z-design/news-image-20261124-entry/rank.svg)](https://make.fun/c/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/52jrkptb7z-design/news-image-20261124-entry/reward.svg)](https://make.fun/c/news-image-20261124)

A one-page newspaper front page that sums up the world's news of
Tuesday, 24 November 2026. Entry for the
[news-image-20261124](https://make.fun/c/news-image-20261124) competition
on [make.fun](https://make.fun).

## The day in one image

Hero story: **Nvidia reinstates Jensen Huang as chief executive** — the
board brought him back after Trump's push, and the shares jumped about
30% as Wall Street rallied.

Also on the page:

- **Huawei guilty of trade-secret theft** — a US jury convicts on
  conspiracy and bank fraud, acquits on racketeering.
- **Ukraine drones hit Russian ships** — strikes in the Gulf of Finland
  and off Libya.
- **Four tankers hit mines in Hormuz** — Iran reports the strikes and
  rules out talks until its conditions are met.
- **Turkish helicopter crash kills five** — an Air Force AS-532 goes
  down after takeoff from Eskisehir.
- In brief: the Cartagena supermarket hostage standoff, a 5.6 quake in
  Nepal, California king tides, Real Madrid 5–1 PSV, and Senegal
  regaining the AFCON title.

## How it works

`main.py` draws the whole page itself — no image files, no network, no
external libraries. It uses an embedded 5×7 bitmap font, a bytearray
canvas, and a hand-written PNG encoder (zlib + struct). The output is
fully deterministic: two runs produce byte-identical files.

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024×1024, about 35 KiB).
