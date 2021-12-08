from app import get_news
from app import schedule_update

def test_get_news():
    data = get_news()
    assert isinstance(data, list)

def test_schedule_update():
    data = get_news()
    assert isinstance(data, list)
