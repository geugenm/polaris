# Notes

## Manual process

- Need to create an account in db.satnogs.org to download telemetry
  - accounts on network/network-dev.satnogs.org are separate

- Choice of frames to download: everything/last week/last month
  - link is to:
      - https://db.satnogs.org/frames/[norad id]/
      - https://db.satnogs.org/frames/[norad id]/1
      - https://db.satnogs.org/frames/[norad id]/2
  - Clicking download from the dropdown, or visiting the links above,
    means you wait for an email with a link
  - The link was to a CSV file; only 1.7 MB, so going to include it here

- **Note:** What this gives us is encoded binary data, not raw
  telemetry.  Continuing down this road means (I think) taking the
  CSV, converting to binary, then parsing as AX.25 files, then using
  the Kitai structs to turn that into telemetry.

    - The alternative Patrick suggests is to ping @kerel to fetch
      telemetry directly from db.satnogs.org.  I haven't yet had time
      to play with that.

- Next steps:
  - read CSV, convert as appropriate (possibly using unhexlify, as in
    [Patrick's
    script](https://github.com/DL4PD/satnogs-kaitai-structs/blob/master/elfin_pp.py#L39))
  - start using his module to parse that as telemetry

# Parsing

https://github.com/DL4PD/satnogs-kaitai-structs

# Automation possibilities

- Settings page for db account has API key: https://db.satnogs.org/users/edit/

- API doc for db: https://db.satnogs.org/api/

- There's a CLI for downloading SatNOGS data, but I'm unsure if this
  will grab telemetry: https://github.com/deckbsd/glouton-satnogs-data-downloader
