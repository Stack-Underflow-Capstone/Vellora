import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.notifications.repository import NotificationRepository, DeviceTokenRepository
from app.modules.notifications.models import Notification, UserDeviceToken


class TestNotificationRepositorySave:
    @pytest.fixture
    def repo(self, mock_db_session):
        return NotificationRepository(mock_db_session)
    
    @pytest.fixture
    def mock_notification(self):
        return MagicMock(spec=Notification)
    
    @pytest.mark.asyncio
    async def test_save_notification(self, repo, mock_db_session, mock_notification):
        """Test saving a notification"""
        result = await repo.save(mock_notification)
        
        mock_db_session.add.assert_called_once_with(mock_notification)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_notification)
        assert result == mock_notification


class TestNotificationRepositoryGetById:
    @pytest.fixture
    def repo(self, mock_db_session):
        return NotificationRepository(mock_db_session)
    
    @pytest.fixture
    def mock_notification(self):
        return MagicMock(spec=Notification)
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repo, mock_db_session, mock_notification):
        """Test getting notification by ID when found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_notification
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        notification_id = uuid4()
        result = await repo.get_by_id(notification_id, user_id)
        
        assert result == mock_notification
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo, mock_db_session):
        """Test getting notification by ID when not found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        notification_id = uuid4()
        result = await repo.get_by_id(notification_id, user_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()


class TestNotificationRepositoryGetUserNotifications:
    @pytest.fixture
    def repo(self, mock_db_session):
        return NotificationRepository(mock_db_session)
    
    @pytest.fixture
    def mock_notifications(self):
        return [MagicMock(spec=Notification)]
    
    @pytest.mark.asyncio
    async def test_get_user_notifications_default_params(self, repo, mock_db_session, mock_notifications):
        """Test getting user notifications with default parameters"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_notifications
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        notifications = await repo.get_user_notifications(user_id)
        
        assert notifications == mock_notifications
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_notifications_unread_only(self, repo, mock_db_session, mock_notifications):
        """Test getting only unread notifications"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_notifications
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        notifications = await repo.get_user_notifications(user_id, unread_only=True)
        
        assert notifications == mock_notifications
        mock_db_session.execute.assert_called_once()


class TestNotificationRepositoryGetUnreadCount:
    @pytest.fixture
    def repo(self, mock_db_session):
        return NotificationRepository(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_get_unread_count_with_results(self, repo, mock_db_session):
        """Test getting unread notification count when count > 0"""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        result = await repo.get_unread_count(user_id)
        
        assert result == 5
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_unread_count_zero(self, repo, mock_db_session):
        """Test getting unread notification count when count is 0"""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        result = await repo.get_unread_count(user_id)
        
        assert result == 0
        mock_db_session.execute.assert_called_once()


class TestNotificationRepositoryMarkAsRead:
    @pytest.fixture
    def repo(self, mock_db_session):
        return NotificationRepository(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, repo, mock_db_session):
        """Test marking notifications as read successfully"""
        mock_result = MagicMock()
        mock_result.rowcount = 2
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        notification_ids = [uuid4(), uuid4()]
        result = await repo.mark_as_read(notification_ids, user_id)
        
        assert result == 2
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mark_as_read_none_updated(self, repo, mock_db_session):
        """Test marking notifications as read when none are updated"""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        notification_ids = [uuid4()]
        result = await repo.mark_as_read(notification_ids, user_id)
        
        assert result == 0
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestNotificationRepositoryUpdatePushSentStatus:
    @pytest.fixture
    def repo(self, mock_db_session):
        return NotificationRepository(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_update_push_sent_status_success(self, repo, mock_db_session):
        """Test updating push sent status"""
        notification_id = uuid4()
        await repo.update_push_sent_status(notification_id, True)
        
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_push_sent_status_false(self, repo, mock_db_session):
        """Test updating push sent status to false"""
        notification_id = uuid4()
        await repo.update_push_sent_status(notification_id, False)
        
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestDeviceTokenRepositoryGetByToken:
    @pytest.fixture
    def repo(self, mock_db_session):
        return DeviceTokenRepository(mock_db_session)
    
    @pytest.fixture
    def mock_device_token(self):
        return MagicMock(spec=UserDeviceToken)
    
    @pytest.mark.asyncio
    async def test_get_by_token_found(self, repo, mock_db_session, mock_device_token, sample_device_token):
        """Test getting device token when found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_device_token
        mock_db_session.execute.return_value = mock_result
        
        result = await repo.get_by_token(sample_device_token)
        
        assert result == mock_device_token
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_token_not_found(self, repo, mock_db_session, sample_device_token):
        """Test getting device token when not found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await repo.get_by_token(sample_device_token)
        
        assert result is None
        mock_db_session.execute.assert_called_once()


class TestDeviceTokenRepositoryUpdate:
    @pytest.fixture
    def repo(self, mock_db_session):
        return DeviceTokenRepository(mock_db_session)
    
    @pytest.fixture
    def mock_device_token(self):
        return MagicMock(spec=UserDeviceToken)
    
    @pytest.mark.asyncio
    async def test_update_device_token(self, repo, mock_db_session, mock_device_token):
        """Test updating device token"""
        result = await repo.update(mock_device_token)
        
        assert result == mock_device_token
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_device_token)
    @pytest.fixture
    def repo(self, mock_db_session):
        return DeviceTokenRepository(mock_db_session)
    
    @pytest.mark.asyncio  
    async def test_register_device_token_new(self, repo, mock_db_session, sample_device_token):
        """Test registering a new device token"""
        user_id = uuid4()
        result = await repo.register_device_token(user_id, sample_device_token, "ios")
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert result.user_id == user_id
        assert result.device_token == sample_device_token
        assert result.device_type == "ios"


class TestDeviceTokenRepositoryGetUserDeviceTokens:
    @pytest.fixture
    def repo(self, mock_db_session):
        return DeviceTokenRepository(mock_db_session)
    
    @pytest.fixture
    def mock_tokens(self):
        return [MagicMock(spec=UserDeviceToken)]
    
    @pytest.mark.asyncio
    async def test_get_user_device_tokens_active_only(self, repo, mock_db_session, mock_tokens):
        """Test getting active user device tokens"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_tokens
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        tokens = await repo.get_user_device_tokens(user_id, active_only=True)
        
        assert tokens == mock_tokens
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_device_tokens_empty(self, repo, mock_db_session):
        """Test getting user device tokens when none exist"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        user_id = uuid4()
        tokens = await repo.get_user_device_tokens(user_id)
        
        assert tokens == []
        mock_db_session.execute.assert_called_once()


class TestDeviceTokenRepositoryDeactivateDeviceToken:
    @pytest.fixture
    def repo(self, mock_db_session):
        return DeviceTokenRepository(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_deactivate_device_token_success(self, repo, mock_db_session, sample_device_token):
        """Test successfully deactivating a device token"""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        
        result = await repo.deactivate_device_token(sample_device_token)
        
        assert result is True
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deactivate_device_token_not_found(self, repo, mock_db_session, sample_device_token):
        """Test deactivating a device token that doesn't exist"""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result
        
        result = await repo.deactivate_device_token(sample_device_token)
        
        assert result is False
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()