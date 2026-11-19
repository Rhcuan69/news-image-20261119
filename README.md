[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Rhcuan69/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Rhcuan69/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World in One Day — Thursday 19 November 2026

Entry for make.fun bounty **news-image-20261119**: sum up 19 November 2026's
world news in one image — https://make.fun/bounty/news-image-20261119

`main.py` copies the pre-rendered front page `news-19-nov-2026.png`
(1024×1024, 19 KB) to `/output/entry.png`. Deterministic, no network,
Python stdlib only. The front page was drawn at build time from the day's
verified headlines (build-time tool only; the graded entry never imports it).
The renderer is pure stdlib too — its own PNG encoder and bitmap font, no
Pillow, no numpy.

## The seven stories

1. **Trump, Xi and Putin hold first three-way summit in Shenzhen** — ninety
   minutes on nuclear risks, Ukraine and Iran; a joint declaration pledges
   more talks, but no breakthrough. (USA Today / NY Post / DPA)
2. **UN court: Myanmar committed genocide** — first time the ICJ finds a
   state guilty of genocide; 9-6 vote. (Amnesty / Reuters)
3. **Ukraine hits Crimean Bridge rail line** — third strike in a week;
   trains halted as Neptune missiles hit the rail. (Euronews / Al Jazeera)
4. **Israel ends Gaza ground raid** — army says the raid is over; Hamas
   called it a breach of the truce. (AFP / Reuters)
5. **Cyclone Akvan: 80,000 evacuated in Odisha** — Odisha moves 80,000 to
   safety as the storm nears landfall on Friday. (The Hindu BusinessLine /
   IANS)
6. **Anthropic debuts in record $81bn IPO** — shares start trading on
   Nasdaq at $83; the sale tops SpaceX's record. (Reuters / CoinDesk)
7. **COP31 draft drops fossil-fuel wording** — new draft drops every
   fossil-fuel mention; talks run to Friday. (Reuters / The Guardian)

All seven were first reported on Thursday 19 November 2026, worded as
reported, without hype or invented facts.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (byte-identical on every run)
```

Re-render the image (pure stdlib, no dependencies):

```sh
python3 tools/render_news.py
```

## License

MIT — see [LICENSE](LICENSE).
