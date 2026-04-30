import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import httpx

from app.infra.adapters.expo_notification_adapter import ExpoNotificationAdapter
from app.modules.notifications.repository import DeviceTokenRepository
from app.modules.notifications.exceptions import NotificationDeliveryError


class TestExpoNotificationAdapterIsValidExpoToken:

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture  
    def adapter(self, device_token_repo):
        return ExpoNotificationAdapter(device_token_repo)

    def test_is_valid_expo_token_valid_formats(self, adapter):
        """Test token validation with valid token formats"""
        assert adapter._is_valid_expo_token("ExponentPushToken[abc123]") is True
        assert adapter._is_valid_expo_token("ExpoPushToken[def456]") is True
    
    def test_is_valid_expo_token_invalid_formats(self, adapter):
        """Test token validation with invalid token formats"""
        assert adapter._is_valid_expo_token("invalid-token") is False
        assert adapter._is_valid_expo_token("ExponentPushToken[missing-bracket") is False
        assert adapter._is_valid_expo_token("") is False
        assert adapter._is_valid_expo_token(None) is False
        assert adapter._is_valid_expo_token("just-text") is False


class TestExpoNotificationAdapterFilterValidExpoTokens:

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture  
    def adapter(self, device_token_repo):
        return ExpoNotificationAdapter(device_token_repo)

    def test_filter_valid_expo_tokens_mixed_input(self, adapter):
        """Test filtering of mixed valid and invalid tokens"""
        tokens = [
            "ExponentPushToken[valid1]",
            "ExpoPushToken[valid2]", 
            "invalid-token",
            "",
            None,
            "ExponentPushToken[valid3]"
        ]
        
        valid_tokens = adapter._filter_valid_expo_tokens(tokens)
        
        assert len(valid_tokens) == 3
        assert "ExponentPushToken[valid1]" in valid_tokens
        assert "ExpoPushToken[valid2]" in valid_tokens
        assert "ExponentPushToken[valid3]" in valid_tokens
    
    def test_filter_valid_expo_tokens_empty_input(self, adapter):
        """Test filtering with empty token list"""
        valid_tokens = adapter._filter_valid_expo_tokens([])
        assert valid_tokens == []


class TestExpoNotificationAdapterSendNotification:

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture  
    def adapter(self, device_token_repo):
        return ExpoNotificationAdapter(device_token_repo)

    @pytest.mark.asyncio
    async def test_send_notification_empty_tokens(self, adapter):
        """Test sending notification with empty token list"""
        result = await adapter.send_notification([], "Title", "Message")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_invalid_tokens(self, adapter):
        """Test sending notification with invalid tokens"""
        invalid_tokens = ["invalid-token", "another-invalid"]
        result = await adapter.send_notification(invalid_tokens, "Title", "Message")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_success(self, adapter):
        """Test successful notification sending"""
        device_tokens = ["ExponentPushToken[valid-token-1]"]
        title = "Test Notification"
        message = "Test message"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"status": "ok"}]}
        
        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            result = await adapter.send_notification(device_tokens, title, message)
            
            assert result is True
            mock_post.assert_called_once()
            
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert len(payload) == 1
            assert payload[0]["to"] == "ExponentPushToken[valid-token-1]"
            assert payload[0]["title"] == title
            assert payload[0]["body"] == message

    @pytest.mark.asyncio
    async def test_send_notification_with_data(self, adapter):
        """Test sending notification with custom data"""
        device_tokens = ["ExponentPushToken[valid-token-1]"]
        title = "Test Notification"
        message = "Test message"
        data = {"trip_id": str(uuid4()), "action": "view_trip"}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"status": "ok"}]}
        
        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            result = await adapter.send_notification(device_tokens, title, message, data)
            
            assert result is True
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload[0]["data"] == data

    @pytest.mark.asyncio
    async def test_send_notification_api_error(self, adapter):
        """Test handling of API error responses"""
        device_tokens = ["ExponentPushToken[valid-token-1]"]
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(NotificationDeliveryError) as exc_info:
                await adapter.send_notification(device_tokens, "Title", "Message")
            
            assert "Expo API returned status 400" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_notification_timeout(self, adapter):
        """Test handling of timeout errors"""
        device_tokens = ["ExponentPushToken[valid-token-1]"]
        
        with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timeout")):
            with pytest.raises(NotificationDeliveryError) as exc_info:
                await adapter.send_notification(device_tokens, "Title", "Message")
            
            assert "Expo push notification request timed out" in str(exc_info.value)


class TestExpoNotificationAdapterSendToUser:

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture  
    def adapter(self, device_token_repo):
        return ExpoNotificationAdapter(device_token_repo)

    @pytest.fixture
    def mock_device_token_obj(self):
        mock_token = MagicMock()
        mock_token.device_token = "ExponentPushToken[valid-token]"
        return mock_token

    @pytest.mark.asyncio
    async def test_send_to_user_no_storage(self):
        """Test send to user with no storage configured"""
        adapter = ExpoNotificationAdapter(None)
        user_id = uuid4()
        
        result = await adapter.send_to_user(user_id, "Title", "Message")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_to_user_no_tokens(self, adapter, device_token_repo):
        """Test send to user with no device tokens"""
        user_id = uuid4()
        device_token_repo.get_user_device_tokens.return_value = []
        
        result = await adapter.send_to_user(user_id, "Title", "Message")
        assert result is False
        device_token_repo.get_user_device_tokens.assert_called_once_with(user_id, active_only=True)

    @pytest.mark.asyncio
    async def test_send_to_user_success(self, adapter, device_token_repo, mock_device_token_obj):
        """Test successful send to user"""
        user_id = uuid4()
        device_token_repo.get_user_device_tokens.return_value = [mock_device_token_obj]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"status": "ok"}]}
        
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await adapter.send_to_user(user_id, "Title", "Message")
            
            assert result is True
            device_token_repo.get_user_device_tokens.assert_called_once_with(user_id, active_only=True)
    
    @pytest.mark.asyncio
    async def test_send_to_user_with_data(self, adapter, device_token_repo, mock_device_token_obj):
        """Test send to user with custom data"""
        user_id = uuid4()
        data = {"trip_id": str(uuid4())}
        device_token_repo.get_user_device_tokens.return_value = [mock_device_token_obj]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"status": "ok"}]}
        
        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            result = await adapter.send_to_user(user_id, "Title", "Message", data)
            
            assert result is True
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload[0]["data"] == data