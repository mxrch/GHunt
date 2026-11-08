import asyncio

import ghunt.parsers.people as people
from ghunt.parsers.people import PersonPhoto


def test_profile_photo_without_url_is_default():
    photo = PersonPhoto()

    asyncio.run(photo._scrape(object(), {}, "profile_photo"))

    assert photo.url == ""
    assert photo.isDefault is True
    assert photo.flathash is None


def test_profile_photo_with_url_is_hashed(monkeypatch):
    async def fake_is_default_profile_pic(as_client, image_url):
        assert image_url == "https://example.com/profile.png"
        return False, "deadbeef"

    monkeypatch.setattr(people, "is_default_profile_pic", fake_is_default_profile_pic)

    photo = PersonPhoto()
    asyncio.run(photo._scrape(object(), {"url": "https://example.com/profile.png"}, "profile_photo"))

    assert photo.url == "https://example.com/profile.png"
    assert photo.isDefault is False
    assert photo.flathash == "deadbeef"


def test_cover_photo_without_image_url_is_default():
    photo = PersonPhoto()

    asyncio.run(photo._scrape(object(), {}, "cover_photo"))

    assert photo.url == ""
    assert photo.isDefault is True


def test_cover_photo_strips_size_parameter():
    photo = PersonPhoto()

    asyncio.run(photo._scrape(
        object(),
        {"imageUrl": "https://example.com/cover=s512", "isDefault": False},
        "cover_photo",
    ))

    assert photo.url == "https://example.com/cover"
    assert photo.isDefault is False
