from app.parser import parse_screenplay


def test_parser_extracts_scenes_dialogue_and_entities():
    screenplay = """INT. KITCHEN - NIGHT\n\nMARA\nI grab the phone and the keys.\n\nShe opens the letter.\n\nEXT. ROOFTOP - DAWN\n\nMARA\nWe made it.\n"""
    scenes = parse_screenplay(screenplay)
    assert len(scenes) == 2
    assert scenes[0].scene_number == 1
    assert scenes[0].slugline == "INT. KITCHEN - NIGHT"
    assert scenes[0].dialogue[0] == {"character": "Mara", "text": "I grab the phone and the keys."}
    assert scenes[0].props == ["keys", "letter", "phone"]
    assert scenes[1].locations == ["Rooftop"]


def test_parser_rejects_empty_input():
    import pytest

    with pytest.raises(ValueError, match="No screenplay scenes"):
        parse_screenplay("just a title")


def test_parser_keeps_multiline_dialogue_together():
    scenes = parse_screenplay("INT. ROOM - DAY\n\nALEX\nFirst line.\nSecond line.\n")
    assert scenes[0].dialogue == [
        {"character": "Alex", "text": "First line."},
        {"character": "Alex", "text": "Second line."},
    ]
