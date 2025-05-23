from googly_eyes.main import GooglyEyesFactory, GooglyEyesInstance
import pytest

@pytest.fixture
def mock_instance():
    """Fixture for creating a mock GooglyEyes instance."""
    instance = GooglyEyesFactory.create_mock_instance()
    yield instance

def test_mock_instance(mock_instance):
    """Test that the mock instance is created correctly."""
    assert mock_instance is not None
    assert isinstance(mock_instance, GooglyEyesInstance)
    mock_instance._bot.start()
    assert mock_instance._bot.running is True
    mock_instance._bot.stop()
    assert mock_instance._bot.running is False