from archive.cd_detect import parse_cd_toc


def test_parse_cd_toc():
    sample = """
  1.    17762 [03:56.62]       33 [00:00.33]    no   no  2
  2.    15788 [03:30.38]    17795 [03:57.20]    no   no  2
TOTAL  231192 [51:22.42]    (audio only)
"""

    tracks = parse_cd_toc(sample)

    assert len(tracks) == 2
    assert tracks[0]["track_number"] == 1
    assert tracks[0]["duration_text"] == "03:56"
    assert tracks[1]["track_number"] == 2
    assert tracks[1]["duration_seconds"] == 210